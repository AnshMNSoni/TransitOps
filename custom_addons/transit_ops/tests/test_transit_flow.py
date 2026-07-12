# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class TestTransitFlow(TransactionCase):

    def setUp(self):
        super(TestTransitFlow, self).setUp()
        self.Vehicle = self.env['transit.vehicle']
        self.Driver = self.env['transit.driver']
        self.Trip = self.env['transit.trip']
        self.Maintenance = self.env['transit.maintenance']
        self.Dashboard = self.env['transit.dashboard']

    def test_transit_operations_lifecycle(self):
        # Step 1: Register a vehicle 'Van-05' with max capacity 500 kg. Status = Available.
        vehicle = self.Vehicle.create({
            'name': 'Van-05-Test',
            'registration_number': 'TEST-VAN-05',
            'vehicle_type': 'van',
            'max_load_capacity': 500.0,
            'odometer': 1000.0,
            'acquisition_cost': 20000.0,
            'status': 'available',
        })
        self.assertEqual(vehicle.status, 'available')

        # Step 2: Register driver 'Alex' with a valid driving license.
        driver = self.Driver.create({
            'name': 'Alex-Test',
            'license_number': 'LIC-ALEX-123',
            'license_category': 'LMV',
            'license_expiry': date.today() + timedelta(days=100),
            'contact_number': '1234567890',
            'safety_score': 90.0,
            'status': 'available',
        })
        self.assertEqual(driver.status, 'available')
        self.assertFalse(driver.is_license_expired)

        # Step 3: Create a trip with Cargo Weight = 450 kg.
        trip = self.Trip.create({
            'source': 'Depot A',
            'destination': 'Client X',
            'vehicle_id': vehicle.id,
            'driver_id': driver.id,
            'cargo_weight': 450.0,
            'planned_distance': 100.0,
            'revenue': 500.0,
        })
        self.assertEqual(trip.state, 'draft')

        # Step 4: System validates that 450 kg <= 500 kg and allows dispatch.
        # Verify that if cargo weight exceeds capacity, validation fails
        with self.assertRaises(ValidationError):
            trip_heavy = self.Trip.create({
                'source': 'Depot A',
                'destination': 'Client X',
                'vehicle_id': vehicle.id,
                'driver_id': driver.id,
                'cargo_weight': 600.0,
                'planned_distance': 100.0,
            })
            trip_heavy.action_dispatch()

        # Try to dispatch valid trip
        trip.action_dispatch()

        # Step 5: Vehicle and Driver status automatically become On Trip.
        self.assertEqual(trip.state, 'dispatched')
        self.assertEqual(vehicle.status, 'on_trip')
        self.assertEqual(driver.status, 'on_trip')

        # Step 6: Complete the trip using the Wizard (simulating final odometer and fuel consumed).
        wizard = self.env['transit.trip.complete.wizard'].with_context(active_id=trip.id).create({
            'final_odometer': 1100.0,
            'fuel_consumed': 10.0,
            'actual_distance': 100.0,
            'fuel_price_per_liter': 2.0,
        })
        wizard.action_confirm()

        # Step 7: System marks both Vehicle and Driver as Available.
        self.assertEqual(trip.state, 'completed')
        self.assertEqual(vehicle.status, 'available')
        self.assertEqual(driver.status, 'available')
        self.assertEqual(vehicle.odometer, 1100.0)

        # Verify fuel log was created and operational costs were updated
        fuel_log = self.env['transit.fuel.log'].search([('trip_id', '=', trip.id)])
        self.assertTrue(fuel_log)
        self.assertEqual(fuel_log.total_cost, 20.0)
        self.assertEqual(vehicle.total_fuel_cost, 20.0)
        self.assertEqual(vehicle.total_operational_cost, 20.0)

        # Step 8: Create a maintenance record (e.g., Oil Change).
        # Vehicle status automatically becomes In Shop and is hidden from dispatch.
        maintenance = self.Maintenance.create({
            'vehicle_id': vehicle.id,
            'service_type': 'oil_change',
            'description': 'Regular oil change',
            'cost': 150.0,
            'state': 'active',
        })
        self.assertEqual(vehicle.status, 'in_shop')

        # Close maintenance
        maintenance.action_complete()
        self.assertEqual(vehicle.status, 'available')

        # Step 9: Reports/Computes update operational cost and fuel efficiency based on the latest trip and fuel log.
        # Force recomputing vehicle total maintenance cost
        vehicle.invalidate_recordset(['total_maintenance_cost', 'total_operational_cost', 'vehicle_roi', 'fuel_efficiency'])
        self.assertEqual(vehicle.total_maintenance_cost, 150.0)
        self.assertEqual(vehicle.total_operational_cost, 170.0) # Fuel 20 + Maint 150
        # Fuel efficiency = (total_distance) / (total_fuel)
        self.assertEqual(vehicle.fuel_efficiency, 10.0)
        # ROI = (Revenue - Operational Cost) / Acquisition Cost * 100
        # ROI = (500 - 170) / 20000 * 100 = 330 / 20000 * 100 = 1.65%
        self.assertAlmostEqual(vehicle.vehicle_roi, 1.65)

        # Verify Dashboard KPIs
        dashboard = self.env['transit.dashboard'].create({})
        dashboard._compute_kpis()
        total_vehicles_in_db = self.env['transit.vehicle'].search_count([])
        available_vehicles_in_db = self.env['transit.vehicle'].search_count([('status', '=', 'available')])
        ontrip_vehicles_in_db = self.env['transit.vehicle'].search_count([('status', '=', 'ontrip')])

        self.assertEqual(dashboard.total_vehicles, total_vehicles_in_db)
        self.assertEqual(dashboard.available_vehicles, available_vehicles_in_db)
        self.assertEqual(dashboard.ontrip_vehicles, ontrip_vehicles_in_db)
        # Fleet utilization check is safe as long as ontrip/active calculations match
        expected_utilization = (ontrip_vehicles_in_db / total_vehicles_in_db * 100) if total_vehicles_in_db else 0.0
        self.assertAlmostEqual(dashboard.fleet_utilization, expected_utilization)
