from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TransitTrip(models.Model):
    _name = 'transit.trip'
    _description = 'Transit Trip'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Trip Reference', default='New', readonly=True, copy=False, tracking=True)
    source = fields.Char(string='Source', required=True, tracking=True)
    destination = fields.Char(string='Destination', required=True, tracking=True)
    vehicle_id = fields.Many2one('transit.vehicle', string='Vehicle',
                                  domain="[('status','=','available')]", required=True, tracking=True)
    driver_id = fields.Many2one('transit.driver', string='Driver',
                                 domain="[('status','=','available'),('is_license_expired','=',False)]",
                                 required=True, tracking=True)
    cargo_weight = fields.Float(string='Cargo Weight (kg)', tracking=True)
    planned_distance = fields.Float(string='Planned Distance (km)', tracking=True)
    actual_distance = fields.Float(string='Actual Distance (km)', tracking=True)
    final_odometer = fields.Float(string='Final Odometer (km)', tracking=True)
    fuel_consumed = fields.Float(string='Fuel Consumed (L)', tracking=True)
    revenue = fields.Float(string='Revenue', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('dispatched', 'Dispatched'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('transit.trip') or 'New'
        return super().create(vals_list)

    def action_dispatch(self):
        for trip in self:
            if trip.state != 'draft':
                raise ValidationError('Only draft trips can be dispatched!')

            # Cargo capacity check
            if trip.cargo_weight and trip.vehicle_id.max_load_capacity:
                if trip.cargo_weight > trip.vehicle_id.max_load_capacity:
                    raise ValidationError(
                        f'Cargo weight ({trip.cargo_weight} kg) exceeds vehicle max capacity '
                        f'({trip.vehicle_id.max_load_capacity} kg)!'
                    )

            # License validity check
            if trip.driver_id.is_license_expired:
                raise ValidationError('Cannot dispatch: Driver license has expired!')

            if trip.driver_id.status == 'suspended':
                raise ValidationError('Cannot dispatch: Driver is suspended!')

            # Double-booking prevention
            if trip.vehicle_id.status != 'available':
                raise ValidationError('Cannot dispatch: Vehicle is not available!')
            if trip.driver_id.status != 'available':
                raise ValidationError('Cannot dispatch: Driver is not available!')

            # Dispatch the trip
            trip.write({'state': 'dispatched'})
            trip.vehicle_id.write({'status': 'on_trip'})
            trip.driver_id.write({'status': 'on_trip'})

    def action_complete(self):
        for trip in self:
            if trip.state != 'dispatched':
                raise ValidationError('Only dispatched trips can be completed!')
            trip.write({'state': 'completed'})
            trip.vehicle_id.write({'status': 'available', 'odometer': trip.final_odometer})
            trip.driver_id.write({'status': 'available'})

    def action_cancel(self):
        for trip in self:
            if trip.state != 'dispatched':
                raise ValidationError('Only dispatched trips can be cancelled!')
            trip.write({'state': 'cancelled'})
            trip.vehicle_id.write({'status': 'available'})
            trip.driver_id.write({'status': 'available'})

    def action_reset_draft(self):
        for trip in self:
            if trip.state != 'cancelled':
                raise ValidationError('Only cancelled trips can be reset to draft!')
            trip.write({'state': 'draft'})
