from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TransitMaintenance(models.Model):
    _name = 'transit.maintenance'
    _description = 'Transit Maintenance'
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
    service_type = fields.Selection(
        selection=[
            ('oil_change', 'Oil Change'),
            ('tyre_replace', 'Tyre Replacement'),
            ('engine_repair', 'Engine Repair'),
            ('brake', 'Brake Service'),
            ('general', 'General Service'),
        ],
        string='Service Type',
        required=True,
        default='general',
        tracking=True,
    )
    description = fields.Text(string='Description')
    cost = fields.Float(string='Cost', tracking=True)
    date = fields.Date(
        string='Service Date',
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('completed', 'Completed'),
        ],
        string='Status',
        default='active',
        required=True,
        tracking=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'transit.maintenance'
                ) or _('New')
        records = super().create(vals_list)
        # When a maintenance record is created as active, mark vehicle "In Shop"
        for rec in records:
            if rec.state == 'active' and rec.vehicle_id.status != 'retired':
                rec.vehicle_id.status = 'in_shop'
        return records

    def action_complete(self):
        for rec in self:
            if rec.state != 'active':
                raise UserError(_('Only active maintenance records can be completed.'))
            rec.state = 'completed'
            # Free the vehicle unless it's retired
            if rec.vehicle_id and rec.vehicle_id.status == 'in_shop':
                rec.vehicle_id.status = 'available'

    def action_reset_to_active(self):
        for rec in self:
            if rec.state == 'completed':
                rec.state = 'active'
                if rec.vehicle_id.status != 'retired':
                    rec.vehicle_id.status = 'in_shop'
