from odoo import models, fields, api, _


class TransitFuelLog(models.Model):
    _name = 'transit.fuel.log'
    _description = 'Transit Fuel Log'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Reference',
        default=lambda self: _('New'),
        required=True,
        copy=False,
        readonly=True,
        tracking=True,
    )
    vehicle_id = fields.Many2one(
        'transit.vehicle',
        string='Vehicle',
        required=True,
        tracking=True,
        ondelete='restrict',
    )
    trip_id = fields.Many2one(
        'transit.trip',
        string='Trip',
        tracking=True,
        ondelete='set null',
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )
    liters = fields.Float(string='Liters', required=True, tracking=True)
    cost_per_liter = fields.Float(
        string='Cost / Liter',
        required=True,
        tracking=True,
    )
    total_cost = fields.Float(
        string='Total Cost',
        compute='_compute_total_cost',
        store=True,
        tracking=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'transit.fuel.log'
                ) or _('New')
        return super().create(vals_list)

    @api.depends('liters', 'cost_per_liter')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = (rec.liters or 0.0) * (rec.cost_per_liter or 0.0)
