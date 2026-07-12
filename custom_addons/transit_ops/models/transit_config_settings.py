from odoo import models, fields, api


class TransitConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    depot_name = fields.Char(
        string='Depot Name',
        config_parameter='TransitOps.depot_name',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        config_parameter='TransitOps.currency_id',
    )
    distance_unit = fields.Selection(
        selection=[
            ('km', 'Kilometers (km)'),
            ('miles', 'Miles'),
        ],
        string='Distance Unit',
        default='km',
        config_parameter='TransitOps.distance_unit',
    )
