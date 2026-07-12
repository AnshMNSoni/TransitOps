# TransitOps — Implementation Plan for Person B (Operations, Finance & Security)

You are responsible for implementing Operations, Finance, Settings, and Security/RBAC. 
To avoid Git/merge conflicts, you will work **exclusively** on your set of files.

---

## 📂 Your Dedicated Files
Do not modify files assigned to Person A or Person C.
* `custom_addons/TransitOps/models/transit_maintenance.py`
* `custom_addons/TransitOps/models/transit_fuel_log.py`
* `custom_addons/TransitOps/models/transit_expense.py`
* `custom_addons/TransitOps/models/transit_config_settings.py`
* `custom_addons/TransitOps/security/transit_security.xml`
* `custom_addons/TransitOps/security/ir.model.access.csv`
* `custom_addons/TransitOps/views/maintenance_views.xml`
* `custom_addons/TransitOps/views/fuel_log_views.xml`
* `custom_addons/TransitOps/views/expense_views.xml`
* `custom_addons/TransitOps/views/settings_views.xml`

---

## 🛠️ Step-by-Step Implementation Guide

### Step 1: Security & RBAC Configuration
Configure access control in `security/transit_security.xml` first to establish security groups:
1. Define a Category named `TransitOps`.
2. Define the security groups:
   - **Fleet Manager** (`group_transit_fleet_manager`)
   - **Dispatcher** (`group_transit_dispatcher`)
   - **Safety Officer** (`group_transit_safety_officer`)
   - **Financial Analyst** (`group_transit_financial_analyst`)
3. Create `security/ir.model.access.csv` and specify full/partial permissions as per this matrix:
   - *Fleet Manager*: Full access to vehicles, maintenance, and analytics.
   - *Dispatcher*: Write access to trips; view vehicles/drivers.
   - *Safety Officer*: Full access to drivers; view-only trips.
   - *Financial Analyst*: View vehicles; write access to expenses & fuel logs.

---

### Step 2: Implement Models

#### 1. Maintenance Model (`models/transit_maintenance.py`)
* Model: `transit.maintenance`
* Fields:
  * `name` (Char, default='New') - Sequence `MNT00001`
  * `vehicle_id` (Many2one → `transit.vehicle`, Required)
  * `service_type` (Selection: `oil_change`, `tyre_replace`, `engine_repair`, `brake`, `general`, Required)
  * `description` (Text)
  * `cost` (Float)
  * `date` (Date, default=today)
  * `state` (Selection: `active`, `completed`, default `active`)
* Business Logic:
  * Overrides `create()` or changes vehicle status: When a maintenance record is saved/active, update `vehicle_id.status = 'in_shop'`.
  * Button Action `action_complete()`: Sets `state = 'completed'`, and updates `vehicle_id.status = 'available'` (unless the vehicle has been marked `retired`).
  * Add automatic integration so In Shop vehicles are excluded from Trip selections.

#### 2. Fuel Log Model (`models/transit_fuel_log.py`)
* Model: `transit.fuel.log`
* Fields:
  * `name` (Char, default='New') - Sequence `FL00001`
  * `vehicle_id` (Many2one → `transit.vehicle`, Required)
  * `trip_id` (Many2one → `transit.trip`, Optional)
  * `date` (Date, default=today)
  * `liters` (Float, Required)
  * `cost_per_liter` (Float, Required)
  * `total_cost` (Float, compute=`_compute_total_cost`, store=True) - `liters * cost_per_liter`

#### 3. Expense Model (`models/transit_expense.py`)
* Model: `transit.expense`
* Fields:
  * `name` (Char, Required) - Description of expense
  * `vehicle_id` (Many2one → `transit.vehicle`, Required)
  * `trip_id` (Many2one → `transit.trip`, Optional)
  * `toll` (Float)
  * `other` (Float)
  * `maintenance_linked` (Float, compute=`_compute_maintenance_linked`, store=True) - Auto cost from maintenance if linked.
  * `total` (Float, compute=`_compute_total`, store=True) - `toll + other + maintenance_linked`
  * `date` (Date, default=today)

#### 4. Settings Model (`models/transit_config_settings.py`)
* Model: `res.config.settings` (Inherited)
* Fields:
  * `depot_name` (Char, config_parameter='TransitOps.depot_name')
  * `currency_id` (Many2one → `res.currency`, config_parameter='TransitOps.currency_id')
  * `distance_unit` (Selection: `km`, `miles`, default `km`, config_parameter='TransitOps.distance_unit')

---

### Step 3: Implement XML Views
Build views matching the wireframes:
1. **Maintenance View** (`views/maintenance_views.xml`): Split layout. Left has a simple Log Service Record form. Right has the Service Log list view.
2. **Fuel Logs & Expenses View** (`views/fuel_log_views.xml`, `views/expense_views.xml`): Standard list and form views. Make sure to display the computed Operational Cost in the list view footer.
3. **Settings View** (`views/settings_views.xml`): Config settings form. Add Depot name, Currency, and Distance Unit fields. On the right side, add a static display of the Role-Based Access matrix for reference.

---

### Step 4: Add Manifest Registrations
Ask Person A to include your XML data files inside the `'data'` block of `__manifest__.py`:
```python
        'security/transit_security.xml',
        'security/ir.model.access.csv',
        'views/maintenance_views.xml',
        'views/fuel_log_views.xml',
        'views/expense_views.xml',
        'views/settings_views.xml',
```
 Also, import your models inside `models/__init__.py`.
