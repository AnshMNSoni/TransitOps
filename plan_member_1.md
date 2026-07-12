# TransitOps — Implementation Plan for Person A (Core Models & Trip Engine)

You are responsible for creating the foundation of the Odoo 19 module: Core Models, Trip Workflow, and Validation checks. 
To avoid Git/merge conflicts, you will work **exclusively** on your set of files.

---

## 📂 Your Dedicated Files
Do not modify files assigned to Person B or Person C.
* `custom_addons/TransitOps/__manifest__.py` (You will create the initial file, then merge changes from others during sync)
* `custom_addons/TransitOps/__init__.py`
* `custom_addons/TransitOps/models/__init__.py`
* `custom_addons/TransitOps/models/transit_vehicle.py`
* `custom_addons/TransitOps/models/transit_driver.py`
* `custom_addons/TransitOps/models/transit_trip.py`
* `custom_addons/TransitOps/wizards/__init__.py`
* `custom_addons/TransitOps/wizards/trip_complete_wizard.py`
* `custom_addons/TransitOps/wizards/trip_complete_wizard_views.xml`
* `custom_addons/TransitOps/views/vehicle_views.xml`
* `custom_addons/TransitOps/views/driver_views.xml`
* `custom_addons/TransitOps/views/trip_views.xml`
* `custom_addons/TransitOps/data/sequence_data.xml`

---

## 🛠️ Step-by-Step Implementation Guide

### Step 1: Module Initial Scaffolding
Create the directory structure:
```
TransitOps/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── transit_vehicle.py
│   ├── transit_driver.py
│   └── transit_trip.py
├── wizards/
│   ├── __init__.py
│   ├── trip_complete_wizard.py
│   └── trip_complete_wizard_views.xml
├── views/
│   ├── vehicle_views.xml
│   ├── driver_views.xml
│   └── trip_views.xml
└── data/
    └── sequence_data.xml
```

In `__manifest__.py`:
```python
{
    'name': 'TransitOps',
    'version': '19.0.1.0.0',
    'summary': 'Smart Transport Operations Platform',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'data/sequence_data.xml',
        'wizards/trip_complete_wizard_views.xml',
        'views/vehicle_views.xml',
        'views/driver_views.xml',
        'views/trip_views.xml',
    ],
    'installable': True,
    'application': True,
}
```

In `sequence_data.xml`, define sequences for `transit.trip` (`TR00001`).

---

### Step 2: Implement Models

#### 1. Vehicle Model (`models/transit_vehicle.py`)
* Model: `transit.vehicle`
* Fields:
  * `name` (Char, Required) - e.g., "Van-05"
  * `registration_number` (Char, Required) - unique constraint:
    `_sql_constraints = [('reg_unique', 'unique(registration_number)', 'The registration number must be unique!')]`
  * `vehicle_type` (Selection: `van`, `truck`, `mini`, `bus`, `trailer`)
  * `max_load_capacity` (Float) - In kg
  * `odometer` (Float) - Current reading
  * `acquisition_cost` (Float)
  * `status` (Selection: `available`, `on_trip`, `in_shop`, `retired`, default `available`)
  * `region` (Char)
  * `image_1920` (Binary)
  * `trip_ids` (One2many → `transit.trip`)
  * `total_fuel_cost` (Float, compute=`_compute_fuel_costs`) - sum of related fuel logs
  * `total_maintenance_cost` (Float, compute=`_compute_maint_costs`) - sum of maintenance cost
  * `total_operational_cost` (Float, compute=`_compute_op_costs`) - fuel + maintenance
  * `total_revenue` (Float, compute=`_compute_revenue`) - sum of trip revenue
  * `vehicle_roi` (Float, compute=`_compute_roi`) - `(Revenue - OpCost) / Acquisition`
  * `fuel_efficiency` (Float, compute=`_compute_fuel_eff`) - total distance / total fuel

#### 2. Driver Model (`models/transit_driver.py`)
* Model: `transit.driver`
* Fields:
  * `name` (Char, Required)
  * `license_number` (Char, Required) - unique constraint
  * `license_category` (Selection: `LMV`, `HMV`, `HGMV`)
  * `license_expiry` (Date)
  * `contact_number` (Char)
  * `safety_score` (Float, default 100.0)
  * `status` (Selection: `available`, `on_trip`, `off_duty`, `suspended`, default `available`)
  * `image_1920` (Binary)
  * `is_license_expired` (Boolean, compute=`_compute_license_expired`)

#### 3. Trip Model (`models/transit_trip.py`)
* Model: `transit.trip`
* Fields:
  * `name` (Char, default='New') - Sequence `TR00001`
  * `source` (Char, Required)
  * `destination` (Char, Required)
  * `vehicle_id` (Many2one → `transit.vehicle`, Domain: `[('status','=','available')]`)
  * `driver_id` (Many2one → `transit.driver`, Domain: `[('status','=','available'),('is_license_expired','=',False)]`)
  * `cargo_weight` (Float)
  * `planned_distance` (Float)
  * `actual_distance` (Float)
  * `final_odometer` (Float)
  * `fuel_consumed` (Float)
  * `revenue` (Float)
  * `state` (Selection: `draft`, `dispatched`, `completed`, `cancelled`, default `draft`)

---

### Step 3: Implement Workflows & Validations (in `transit.trip`)

1. **Cargo Capacity Check**:
   Raise `ValidationError` on `action_dispatch()` if `cargo_weight > vehicle_id.max_load_capacity`.
2. **License check**:
   Raise `ValidationError` if `driver_id.is_license_expired` is True or `driver_id.status == 'suspended'`.
3. **Double Booking**:
   Ensure `vehicle_id.status == 'available'` and `driver_id.status == 'available'` before dispatching.
4. **Auto State Updates**:
   * On **Dispatch**: Set `state = 'dispatched'`, update `vehicle_id.status = 'on_trip'`, and update `driver_id.status = 'on_trip'`.
   * On **Cancel** (from Dispatched): Restore `vehicle_id.status = 'available'` and `driver_id.status = 'available'`. Set `state = 'cancelled'`.

---

### Step 4: Complete Trip Wizard (`wizards/trip_complete_wizard.py`)
* TransientModel: `transit.trip.complete.wizard`
* Fields:
  * `trip_id` (Many2one → `transit.trip`)
  * `final_odometer` (Float, Required)
  * `fuel_consumed` (Float, Required)
  * `actual_distance` (Float, Required)
  * `fuel_price_per_liter` (Float, Required)
* Logic:
  * On Save: Update trip's `final_odometer`, `fuel_consumed`, `actual_distance`, and set trip `state = 'completed'`.
  * Update `vehicle_id.odometer` with `final_odometer`.
  * Set `vehicle_id.status = 'available'` and `driver_id.status = 'available'`.
  * **Call B's model API** (or dynamically create `transit.fuel.log`) using:
    ```python
    self.env['transit.fuel.log'].create({
        'vehicle_id': trip.vehicle_id.id,
        'trip_id': trip.id,
        'date': fields.Date.today(),
        'liters': self.fuel_consumed,
        'cost_per_liter': self.fuel_price_per_liter,
    })
    ```

---

### Step 5: Implement XML Views
Build high-quality Odoo views (`vehicle_views.xml`, `driver_views.xml`, `trip_views.xml`). Use clear lists with colored badges (e.g. `<field name="status" widget="badge" decoration-success="status == 'available'" decoration-danger="status == 'retired'"/>`).
