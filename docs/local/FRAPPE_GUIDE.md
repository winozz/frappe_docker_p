# Frappe Framework Guide

## 🏗️ Architecture Overview

```
frappe-bench/
├── apps/              # All Frappe apps (frappe, erpnext, hrms, ais, etc.)
├── sites/             # Each site = separate instance with own database
│   └── ais.localhost/
│       ├── site_config.json  # Database credentials & config
│       └── private/          # Uploaded files
├── config/            # Redis, supervisor configs
└── env/              # Python virtual environment
```

## 📊 DocType Explained

### What is a DocType?
A **DocType** is Frappe's way of defining data models. Each DocType represents:

1. **Database Table** - Automatically created in MariaDB
2. **Web Form** - Auto-generated CRUD interface
3. **API Endpoints** - RESTful APIs for the DocType
4. **Business Logic** - Python controllers
5. **Permissions** - Role-based access control

### Example: Customer DocType

When you create a "Customer" DocType with fields:
- `customer_name` (Data)
- `email` (Data)
- `phone` (Data)

Frappe automatically creates:
- **Table**: `tabCustomer` in MariaDB
- **Form**: `/app/customer` to add/edit customers
- **List**: `/app/customer` to view all customers
- **API**: GET/POST to `/api/resource/Customer`

### DocType Structure

```
apps/ais/ais/ais/doctype/
└── my_doctype/
    ├── my_doctype.json         # Field definitions (UI-created)
    ├── my_doctype.py           # Python controller (business logic)
    ├── my_doctype.js           # Client-side JavaScript
    └── my_doctype_list.js      # List view customization
```

## 🗄️ Database Structure

### Database Name
Your site uses: `_0a189b99783e3c71` (from site_config.json)

### Table Naming Convention
- **DocTypes**: `tabDocTypeName` (e.g., `tabCustomer`, `tabItem`)
- **Singles**: `tabSingles` (for single-value settings)
- **Series**: `tabSeries` (for naming series like INV-2024-)

### Core Tables
```
tabDocType           # Metadata about all DocTypes
tabDocField          # Field definitions for each DocType
tabUser              # User accounts
tabRole              # User roles
tabDocPerm           # Permissions mapping
```

## 🔍 How to Access the Database

### Method 1: Using Bench Console (Recommended)
```bash
cd /workspace/development/frappe-bench
bench --site ais.localhost console

# In the console:
frappe.db.sql("SHOW TABLES")
frappe.db.sql("SELECT * FROM tabUser")
frappe.get_all("Customer", fields=["name", "customer_name"])
```

### Method 2: Direct MariaDB Connection
```bash
# Connection details from site_config.json:
# Host: mariadb (container) or localhost:3307 (from host)
# Database: _0a189b99783e3c71
# User: _0a189b99783e3c71
# Password: mkLDqxSM77mUzxFg

# Inside frappe container:
mysql -h mariadb -u _0a189b99783e3c71 -pmkLDqxSM77mUzxFg _0a189b99783e3c71

# From your Windows host:
mysql -h 127.0.0.1 -P 3307 -u _0a189b99783e3c71 -pmkLDqxSM77mUzxFg _0a189b99783e3c71
```

### Method 3: Database GUI Tools
Use tools like:
- **DBeaver** (Free, cross-platform)
- **MySQL Workbench**
- **HeidiSQL** (Windows)

**Connection Settings:**
- Host: `localhost`
- Port: `3307`
- User: `_0a189b99783e3c71`
- Password: `mkLDqxSM77mUzxFg`
- Database: `_0a189b99783e3c71`

## 🎯 Common Frappe Commands

### Site Management
```bash
# List all sites
bench --site all list-apps

# Migrate (run database migrations)
bench --site ais.localhost migrate

# Clear cache
bench --site ais.localhost clear-cache

# Reinstall site (WARNING: deletes all data)
bench --site ais.localhost reinstall
```

### App Management
```bash
# Create new app
bench new-app myapp

# Install app on site
bench --site ais.localhost install-app myapp

# Uninstall app
bench --site ais.localhost uninstall-app myapp
```

### Development
```bash
# Start development server
bench start

# Build assets
bench build

# Watch and rebuild on changes
bench watch
```

### Database Operations
```bash
# Backup database
bench --site ais.localhost backup

# Restore database
bench --site ais.localhost restore /path/to/backup.sql.gz

# Run SQL directly
bench --site ais.localhost mariadb
```

## 🔧 Creating Your First DocType

### Via Web UI (Recommended for beginners)
1. Login: http://ais.localhost:8000
2. Search: "DocType List"
3. Click "New"
4. Fill in:
   - **Name**: Employee
   - **Module**: AIS
   - **Fields**: Add fields (name, department, salary, etc.)
5. Save & "Add Fields"

### Via Code (For version control)
```bash
# Inside container
cd /workspace/development/frappe-bench
bench --site ais.localhost console

# In console:
doc = frappe.get_doc({
    "doctype": "DocType",
    "name": "Employee",
    "module": "AIS",
    "fields": [
        {"fieldname": "employee_name", "fieldtype": "Data", "label": "Employee Name"},
        {"fieldname": "department", "fieldtype": "Link", "options": "Department"},
    ]
})
doc.insert()
```

## 📦 Predefined Components

### 1. **Frappe (Core Framework)**
- User management
- Role & Permissions
- Workflow engine
- Email integration
- Reports & Dashboard
- API framework

### 2. **ERPNext (ERP App)**
- Accounting
- Inventory
- Manufacturing
- CRM
- HR (payroll, leave, attendance)
- Project management

### 3. **HRMS (HR App)**
- Recruitment
- Attendance tracking
- Leave management
- Payroll processing
- Performance reviews

### 4. **Payments**
- Payment gateway integration
- Payment requests
- Subscription management

## 🔗 Database Relationships

### Link Fields (Foreign Keys)
```python
# In DocType definition
{
    "fieldname": "customer",
    "fieldtype": "Link",
    "options": "Customer"  # References tabCustomer
}
```

### Table Fields (Child Tables)
```python
# Parent DocType: Sales Order
# Child DocType: Sales Order Item

# Creates 1-to-many relationship
# tabSales Order (1) -> tabSales Order Item (many)
```

### Query Relationships
```python
# Get customer with all orders
customer = frappe.get_doc("Customer", "CUST-001")
orders = frappe.get_all("Sales Order", 
    filters={"customer": customer.name},
    fields=["name", "total", "status"]
)
```

## 🎨 Developer Mode Features

Your site has `developer_mode: 1` enabled, which provides:
- Reload on code changes
- Detailed error messages
- DocType export to JSON
- JavaScript console access
- Performance profiling

## 📚 Useful Resources

- **Official Docs**: https://frappeframework.com/docs
- **ERPNext Docs**: https://docs.erpnext.com
- **Forum**: https://discuss.frappe.io
- **API Reference**: http://ais.localhost:8000/api/method/frappe.desk.reportview.get

## 🚀 Quick Start Workflow

1. **Start containers**: `docker compose -f .devcontainer/docker-compose.yml up -d`
2. **Access site**: http://ais.localhost:8000
3. **Login**: Administrator / (your admin password)
4. **Create DocType**: Search "DocType List" → New
5. **View Database**: Use MySQL client with credentials above
6. **Code**: Edit files in `apps/ais/`
7. **Test**: Changes auto-reload in developer mode

## 🐛 Debugging Tips

### View Logs
```bash
# Application logs
tail -f /workspace/development/frappe-bench/logs/bench.log

# Database logs (in mariadb container)
docker compose -f .devcontainer/docker-compose.yml logs mariadb
```

### Python Debugger
```python
# Add to any Python file
import frappe
frappe.set_trace()  # Breakpoint - opens pdb debugger
```

### Check Database Schema
```sql
-- Show table structure
DESCRIBE tabCustomer;

-- Show all columns
SELECT * FROM information_schema.COLUMNS 
WHERE TABLE_NAME = 'tabCustomer';
```
