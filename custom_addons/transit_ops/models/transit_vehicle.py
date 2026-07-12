from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TransitVehicle(models.Model):
    _name = 'transit.vehicle'
    _description = 'Transit Vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Vehicle Name', required=True, tracking=True)
    registration_number = fields.Char(string='Registration Number', required=True, tracking=True)
    vehicle_type = fields.Selection([
        ('van', 'Van'),
        ('truck', 'Truck'),
        ('mini', 'Mini'),
        ('bus', 'Bus'),
        ('trailer', 'Trailer'),
    ], string='Vehicle Type', tracking=True)
    max_load_capacity = fields.Float(string='Max Load Capacity (kg)', tracking=True)
    odometer = fields.Float(string='Odometer (km)', tracking=True)
    acquisition_cost = fields.Float(string='Acquisition Cost', tracking=True)
    status = fields.Selection([
        ('available', 'Available'),
        ('on_trip', 'On Trip'),
        ('in_shop', 'In Shop'),
        ('retired', 'Retired'),
    ], string='Status', default='available', tracking=True)
    region = fields.Char(string='Region', tracking=True)
    image_1920 = fields.Image(string='Vehicle Image', max_width=1920, max_height=1920)
    trip_ids = fields.One2many('transit.trip', 'vehicle_id', string='Trips')
    fuel_log_ids = fields.One2many('transit.fuel.log', 'vehicle_id', string='Fuel Logs')
    maintenance_ids = fields.One2many('transit.maintenance', 'vehicle_id', string='Maintenance Logs')

    total_fuel_cost = fields.Float(string='Total Fuel Cost', compute='_compute_fuel_costs', store=True)
    total_maintenance_cost = fields.Float(string='Total Maintenance Cost', compute='_compute_maint_costs', store=True)
    total_operational_cost = fields.Float(string='Total Operational Cost', compute='_compute_op_costs', store=True)
    total_revenue = fields.Float(string='Total Revenue', compute='_compute_revenue', store=True)
    vehicle_roi = fields.Float(string='Vehicle ROI (%)', compute='_compute_roi', store=True, aggregator='avg')
    fuel_efficiency = fields.Float(string='Fuel Efficiency (km/L)', compute='_compute_fuel_eff', store=True, aggregator='avg')

    _reg_unique = models.Constraint('unique(registration_number)', 'The registration number must be unique!')

    @api.depends('fuel_log_ids.total_cost')
    def _compute_fuel_costs(self):
        for rec in self:
            rec.total_fuel_cost = sum(rec.fuel_log_ids.mapped('total_cost'))

    @api.depends('maintenance_ids.cost', 'maintenance_ids.state')
    def _compute_maint_costs(self):
        for rec in self:
            completed_maint = rec.maintenance_ids.filtered(lambda m: m.state == 'completed')
            rec.total_maintenance_cost = sum(completed_maint.mapped('cost'))

    @api.depends('total_fuel_cost', 'total_maintenance_cost')
    def _compute_op_costs(self):
        for rec in self:
            rec.total_operational_cost = rec.total_fuel_cost + rec.total_maintenance_cost

    @api.depends('trip_ids.revenue', 'trip_ids.state')
    def _compute_revenue(self):
        for rec in self:
            completed_trips = rec.trip_ids.filtered(lambda t: t.state == 'completed')
            rec.total_revenue = sum(completed_trips.mapped('revenue'))

    @api.depends('total_revenue', 'total_operational_cost', 'acquisition_cost')
    def _compute_roi(self):
        for rec in self:
            if rec.acquisition_cost:
                rec.vehicle_roi = ((rec.total_revenue - rec.total_operational_cost) / rec.acquisition_cost) * 100
            else:
                rec.vehicle_roi = 0.0

    @api.depends('trip_ids.actual_distance', 'trip_ids.fuel_consumed', 'trip_ids.state')
    def _compute_fuel_eff(self):
        for rec in self:
            completed_trips = rec.trip_ids.filtered(lambda t: t.state == 'completed')
            total_distance = sum(completed_trips.mapped('actual_distance'))
            total_fuel = sum(completed_trips.mapped('fuel_consumed'))
            rec.fuel_efficiency = total_distance / total_fuel if total_fuel else 0.0
