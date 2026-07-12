from odoo import models, fields, api
from datetime import date, timedelta


class TransitDriver(models.Model):
    _name = 'transit.driver'
    _description = 'Transit Driver'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Driver Name', required=True, tracking=True)
    license_number = fields.Char(string='License Number', required=True, tracking=True)
    license_category = fields.Selection([
        ('LMV', 'Light Motor Vehicle (LMV)'),
        ('HMV', 'Heavy Motor Vehicle (HMV)'),
        ('HGMV', 'Heavy Goods Motor Vehicle (HGMV)'),
    ], string='License Category', tracking=True)
    license_expiry = fields.Date(string='License Expiry Date', tracking=True)
    contact_number = fields.Char(string='Contact Number', tracking=True)
    safety_score = fields.Float(string='Safety Score', default=100.0, tracking=True)
    status = fields.Selection([
        ('available', 'Available'),
        ('on_trip', 'On Trip'),
        ('off_duty', 'Off Duty'),
        ('suspended', 'Suspended'),
    ], string='Status', default='available', tracking=True)
    image_1920 = fields.Image(string='Driver Photo', max_width=1920, max_height=1920)
    is_license_expired = fields.Boolean(string='License Expired', compute='_compute_license_expired', store=True)

    _sql_constraints = [
        ('license_unique', 'unique(license_number)', 'The license number must be unique!')
    ]

    @api.depends('license_expiry')
    def _compute_license_expired(self):
        today = date.today()
        for rec in self:
            rec.is_license_expired = bool(rec.license_expiry and rec.license_expiry < today)
