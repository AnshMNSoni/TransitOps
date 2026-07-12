from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TripCompleteWizard(models.TransientModel):
    _name = 'transit.trip.complete.wizard'
    _description = 'Complete Trip Wizard'

    trip_id = fields.Many2one('transit.trip', string='Trip', required=True)
    final_odometer = fields.Float(string='Final Odometer (km)', required=True)
    fuel_consumed = fields.Float(string='Fuel Consumed (L)', required=True)
    actual_distance = fields.Float(string='Actual Distance (km)', required=True)
    fuel_price_per_liter = fields.Float(string='Fuel Price per Liter', required=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            trip = self.env['transit.trip'].browse(active_id)
            res.update({
                'trip_id': trip.id,
                'final_odometer': trip.vehicle_id.odometer,
            })
        return res

    def action_confirm(self):
        self.ensure_one()
        trip = self.trip_id

        if self.actual_distance <= 0:
            raise ValidationError('Actual distance must be greater than zero!')
        if self.fuel_consumed <= 0:
            raise ValidationError('Fuel consumed must be greater than zero!')
        if self.fuel_price_per_liter <= 0:
            raise ValidationError('Fuel price per liter must be greater than zero!')

        # Update trip fields
        trip.write({
            'final_odometer': self.final_odometer,
            'fuel_consumed': self.fuel_consumed,
            'actual_distance': self.actual_distance,
            'state': 'completed',
        })

        # Update vehicle odometer and status
        trip.vehicle_id.write({
            'odometer': self.final_odometer,
            'status': 'available',
        })

        # Update driver status
        trip.driver_id.write({'status': 'available'})

        # Create fuel log entry
        self.env['transit.fuel.log'].create({
            'vehicle_id': trip.vehicle_id.id,
            'trip_id': trip.id,
            'date': fields.Date.today(),
            'liters': self.fuel_consumed,
            'cost_per_liter': self.fuel_price_per_liter,
        })

        return {'type': 'ir.actions.act_window_close'}
