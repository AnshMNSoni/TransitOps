# TransitOps — Implementation Plan for Person C (Dashboard, Analytics, Reports & Polish)

You are responsible for creating the Dashboard, Analytics charts, QWeb PDF reports, scheduled actions (Cron), and menus.
To avoid Git/merge conflicts, you will work **exclusively** on your set of files.

---

## 📂 Your Dedicated Files
Do not modify files assigned to Person A or Person B.
* `custom_addons/TransitOps/views/menu_views.xml`
* `custom_addons/TransitOps/views/dashboard_views.xml`
* `custom_addons/TransitOps/views/analytics_views.xml`
* `custom_addons/TransitOps/data/cron_data.xml`
* `custom_addons/TransitOps/data/mail_template_data.xml`
* `custom_addons/TransitOps/data/demo_data.xml`
* `custom_addons/TransitOps/reports/trip_report_template.xml`
* `custom_addons/TransitOps/reports/vehicle_report_template.xml`
* `custom_addons/TransitOps/reports/fleet_summary_report.xml`
* `custom_addons/TransitOps/static/description/icon.png`

---

## 🛠️ Step-by-Step Implementation Guide

### Step 1: Menu Structure & Navigation (`views/menu_views.xml`)
Create the main menu tree matching the sidebar:
* **TransitOps** (Root Menu)
  * **Dashboard** (Action: Link to dashboard views)
  * **Fleet** (Action: Link to Person A's Vehicle views)
  * **Drivers** (Action: Link to Person A's Driver views)
  * **Trips** (Action: Link to Person A's Trip views)
  * **Maintenance** (Action: Link to Person B's Maintenance views)
  * **Fuel & Expenses** (Submenu)
    * *Fuel Logs* (Action: Link to Person B's Fuel views)
    * *Other Expenses* (Action: Link to Person B's Expense views)
  * **Analytics** (Submenu)
    * *Vehicle Performance* (Action: Link to Analytics views)
  * **Settings** (Action: Link to Person B's Config views)

---

### Step 2: Dashboard Views (`views/dashboard_views.xml`)
Implement the TransitOps Dashboard:
1. Define a dashboard view type or a custom client action with a template containing **KPI cards**:
   - Active Vehicles
   - Available Vehicles
   - Vehicles in Maintenance
   - Active Trips
   - Pending Trips
   - Drivers On Duty
   - Fleet Utilization (%)
2. Include a **Recent Trips** list table view displaying Name, Vehicle, Driver, Status, and ETA.
3. Display a **Vehicle Status** chart (stacked bar or pie chart showing Available vs. On Trip vs. In Shop).

---

### Step 3: Analytics & Reporting Views (`views/analytics_views.xml`)
Use Odoo's native `<graph>` and `<pivot>` views to implement charts from wireframe #7:
1. **Fuel Efficiency Graph**: Line/bar chart displaying Distance / Fuel.
2. **Monthly Revenue Bar Chart**: Visualizing revenue totals per month.
3. **Top Costliest Vehicles Graph**: Horizontal bar chart comparing vehicles by maintenance/fuel expenses.

---

### Step 4: QWeb PDF Reports (`reports/`)
Define print actions and HTML templates:
1. **Trip Summary Report** (`trip_report_template.xml`): Details route, driver, vehicle, weight, fuel, and odometer data.
2. **Vehicle Operations Report** (`vehicle_report_template.xml`): Summary of operational cost, maintenance, and vehicle ROI.
3. **Fleet Summary PDF** (`fleet_summary_report.xml`): Overview of overall fleet metrics, KPIs, and utilization rates.

---

### Step 5: Automated Cron Jobs & Mail Templates (`data/`)
1. **License Expiry Scheduled Action** (`cron_data.xml`):
   - Set up an Odoo scheduled action (`ir.cron`) running daily.
   - Executes Python code to search for `transit.driver` whose `license_expiry` is within the next 30 days.
2. **License Expiry Email Template** (`mail_template_data.xml`):
   - Define a custom email template.
   - When the cron runs, it sends a styled notification email containing the expiring drivers' list to the **Safety Officer** group users.

---

### Step 6: Demo Data & Branding (`data/demo_data.xml`)
1. Create demo data for all models (Vehicle "Van-05", Driver "Alex", sample trips, maintenance, and fuel logs) to make the application immediately functional.
2. Add a clean TransitOps icon to `static/description/icon.png`.

---

### Step 7: Add Manifest Registrations
Ask Person A to include your XML files inside the `'data'` block of `__manifest__.py`:
```python
        'data/cron_data.xml',
        'data/mail_template_data.xml',
        'data/demo_data.xml',
        'reports/trip_report_template.xml',
        'reports/vehicle_report_template.xml',
        'reports/fleet_summary_report.xml',
        'views/dashboard_views.xml',
        'views/analytics_views.xml',
        'views/menu_views.xml',
```
 Ensure all menu actions match standard window actions.
