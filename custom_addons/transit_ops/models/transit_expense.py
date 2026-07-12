from odoo import models, fields, api


class TransitExpense(models.Model):
    _name = 'transit.expense'
    _description = 'Transit Expense'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='Description', required=True, tracking=True)
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
    toll = fields.Float(string='Toll', tracking=True)
    other = fields.Float(string='Other Expenses', tracking=True)
    maintenance_linked = fields.Float(
        string='Maintenance Cost (Linked)',
        compute='_compute_maintenance_linked',
        store=True,
    )
    total = fields.Float(
        string='Total',
        compute='_compute_total',
        store=True,
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )

    @api.depends('vehicle_id', 'date')
    def _compute_maintenance_linked(self):
        """Auto-pull maintenance cost from same vehicle on same date."""
        for rec in self:
            if rec.vehicle_id and rec.date:
                maint = self.env['transit.maintenance'].search([
                    ('vehicle_id', '=', rec.vehicle_id.id),
                    ('date', '=', rec.date),
                    ('state', '=', 'completed'),
                ])
                rec.maintenance_linked = sum(maint.mapped('cost'))
            else:
                rec.maintenance_linked = 0.0

    @api.depends('toll', 'other', 'maintenance_linked')
    def _compute_total(self):
        for rec in self:
            rec.total = (rec.toll or 0.0) + (rec.other or 0.0) + (rec.maintenance_linked or 0.0)
