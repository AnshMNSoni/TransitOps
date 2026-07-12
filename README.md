# TransitOps — Smart Transport Operations Platform

TransitOps is a centralized fleet and transport operations platform designed to digitize vehicle, driver, dispatch, maintenance, and expense management. Built as a custom Odoo 19 module, it enforces business logic, automates workflows, and provides high-level operational insights.

---

## Key Features

### 1. Dashboard & Real-Time KPIs
- Display real-time operational metrics:
  - **Active Vehicles** (On Trip)
  - **Available Vehicles** (Available)
  - **Vehicles in Maintenance** (In Shop)
  - **Active Trips**, **Pending Trips**, **Drivers On Duty**
  - **Fleet Utilization (%)**
- Custom filters for **Vehicle Type**, **Status**, and **Region**.
- **Recent Trips** monitoring list.
- **Vehicle Status** distribution visualization.

### 2. Vehicle Registry & Lifecycle Management
- Master registry for vehicles containing:
  - Model/Name, Type, Acquisition Cost, Region, and Image.
  - Tracking variables: Odometer and Max Load Capacity.
  - Unique **Registration Number** enforcement.
  - Automated status transitions: `Available` ↔ `On Trip` ↔ `In Shop` ↔ `Retired`.

### 3. Driver Management & Compliance
- Comprehensive driver profiles:
  - License Number (Unique), Category (LMV/HMV/HGMV), Expiry Date, Contact, and Safety Score.
  - Automated validity check: Blocks expired or suspended drivers from trip assignment.
  - License expiry email warnings sent automatically 30 days before expiration.

### 4. Smart Trip Dispatch Engine
- Create and manage trips (Draft → Dispatched → Completed → Cancelled).
- **Core Validations (Enforced before dispatch)**:
  - Cargo weight verification against vehicle's maximum capacity.
  - Double-booking prevention for drivers and vehicles.
  - Compliance check (expired license or suspended status).
- **Automatic Status Synchronization**:
  - Dispatching a trip changes both the vehicle and driver to `On Trip`.
  - Completing a trip changes both back to `Available` (with odometer updates).
  - Cancelling a dispatched trip restores statuses to `Available`.

### 5. Maintenance Workflow
- Direct logging for maintenance events (e.g., Oil Change, Engine Repair).
- Creating an active service record automatically shifts vehicle status to `In Shop`.
- In-shop vehicles are automatically hidden from the dispatch pool.
- Closing maintenance restores vehicle status to `Available`.

### 6. Fuel & Expense Management
- Fuel logs (liters, cost per liter, date) linked to vehicles.
- Operational expenses tracker (toll, miscellaneous, linked maintenance cost).
- Automatic calculation of **Total Operational Cost** (Fuel + Maintenance) per vehicle.

### 7. Reports & Analytics
- Multi-dimensional reports:
  - **Fuel Efficiency** (Distance / Fuel consumed).
  - **Fleet Utilization** metrics.
  - **Operational Costs** and **Vehicle ROI** computed using:
    $$\text{Vehicle ROI} = \frac{\text{Revenue} - (\text{Maintenance} + \text{Fuel})}{\text{Acquisition Cost}}$$
- QWeb PDF exports for trip details, vehicle operations, and fleet summaries.
- One-click CSV export on list views.

---

## Role-Based Access Control (RBAC)

| Role | Fleet | Driver | Trip | Fuel & Expense | Analytics |
|---|---|---|---|---|---|
| **Fleet Manager** | Full | Full | — | — | Full |
| **Dispatcher** | View | — | Full | — | — |
| **Safety Officer** | — | Full | View | — | — |
| **Financial Analyst** | View | — | — | Full | Full |

---

## Installation & Setup

1. Place this directory inside your Odoo `custom_addons` folder.
2. In your `odoo.conf`, ensure the custom addons path is configured:
   ```ini
   addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
   ```
3. Update the App list in Odoo:
   - Turn on **Developer Mode**.
   - Go to **Apps** → Click **Update Apps List**.
   - Search for **TransitOps** and click **Install**.

---

## Team Distribution Plans

The team task distribution files are located in:
* `docs/plan_member_1.md` (Core Models & Trip Engine)
* `docs/plan_member_2.md` (Operations, Finance & Security)
* `docs/plan_member_3.md` (Dashboard, Analytics, Reports & Polish)
