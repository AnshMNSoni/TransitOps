# -*- coding: utf-8 -*-
from odoo import models, fields, api


class TransitDashboard(models.Model):
    _name = 'transit.dashboard'
    _description = 'Transit Dashboard'

    name = fields.Char(string='Name', default='Fleet Operations Dashboard', readonly=True)

    # Vehicle KPIs
    total_vehicles = fields.Integer(string='Total Fleet Vehicles', compute='_compute_kpis')
    available_vehicles = fields.Integer(string='Available Vehicles', compute='_compute_kpis')
    ontrip_vehicles = fields.Integer(string='Vehicles On Trip', compute='_compute_kpis')
    maintenance_vehicles = fields.Integer(string='Vehicles in Shop', compute='_compute_kpis')

    # Driver KPIs
    total_drivers = fields.Integer(string='Total Drivers', compute='_compute_kpis')
    drivers_on_duty = fields.Integer(string='Drivers On Duty', compute='_compute_kpis')

    # Trip KPIs
    active_trips = fields.Integer(string='Active Trips', compute='_compute_kpis')
    pending_trips = fields.Integer(string='Pending Trips', compute='_compute_kpis')

    # Utilization
    fleet_utilization = fields.Float(string='Fleet Utilization (%)', compute='_compute_kpis', digits=(16, 1))

    def _compute_kpis(self):
        Vehicle = self.env['transit.vehicle']
        Driver = self.env['transit.driver']
        Trip = self.env['transit.trip']

        # Get vehicles
        vehicles = Vehicle.search([])
        total_veh = len(vehicles.filtered(lambda v: v.status != 'retired'))
        avail_veh = len(vehicles.filtered(lambda v: v.status == 'available'))
        on_trip_veh = len(vehicles.filtered(lambda v: v.status == 'on_trip'))
        in_shop_veh = len(vehicles.filtered(lambda v: v.status == 'in_shop'))

        # Get drivers
        drivers = Driver.search([])
        total_drv = len(drivers.filtered(lambda d: d.status != 'suspended'))
        on_duty_drv = len(drivers.filtered(lambda d: d.status == 'on_trip'))

        # Get trips
        trips = Trip.search([])
        act_trips = len(trips.filtered(lambda t: t.state == 'dispatched'))
        pend_trips = len(trips.filtered(lambda t: t.state == 'draft'))

        # Calculate fleet utilization
        # Fleet utilization = (On Trip Vehicles / Total Fleet Vehicles) * 100
        utilization = 0.0
        if total_veh > 0:
            utilization = (on_trip_veh / total_veh) * 100.0

        for rec in self:
            rec.total_vehicles = total_veh
            rec.available_vehicles = avail_veh
            rec.ontrip_vehicles = on_trip_veh
            rec.maintenance_vehicles = in_shop_veh
            rec.total_drivers = total_drv
            rec.drivers_on_duty = on_duty_drv
            rec.active_trips = act_trips
            rec.pending_trips = pend_trips
            rec.fleet_utilization = utilization

    def action_open_dashboard(self):
        self.ensure_one()
        # Force recompute before displaying
        self._compute_kpis()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fleet Dashboard',
            'res_model': 'transit.dashboard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'flags': {'initial_mode': 'view'},
        }

    @api.model
    def get_dashboard_action(self):
        # Helper to find or create singleton dashboard record and open it
        dashboard = self.search([], limit=1)
        if not dashboard:
            dashboard = self.create({})
        return dashboard.action_open_dashboard()
