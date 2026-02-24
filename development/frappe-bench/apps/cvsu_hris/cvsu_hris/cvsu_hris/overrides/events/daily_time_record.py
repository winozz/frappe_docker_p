
import frappe

def check_duplicate_dtr(doc):
    existing_record = frappe.db.exists(
        "Daily Time Record",
        {
            "year": doc.year,
            "month": doc.month,
            "cut_off": doc.cut_off,
            "employee": doc.employee,
            "name": ["!=", doc.name]  # Exclude the current record when editing
        }
    )
    if existing_record:
        frappe.throw("A record with the same Year, Month, and Cut-off already exists.")

def create_id_for_sorting(doc):
    if doc.year and doc.month and doc.cut_off:  
        month_map = {
            "January": "01", "February": "02", "March": "03", "April": "04",
            "May": "05", "June": "06", "July": "07", "August": "08",
            "September": "09", "October": "10", "November": "11", "December": "12"
        }

        cut_off_map = {
            "16-31": "01", "1-15": "02", "1-31": "03"
        }

        try:
            year = int(doc.year)  # Convert year to integer
        except ValueError:
            frappe.throw("Invalid Year Format. Please enter a valid year.")

        month = month_map.get(doc.month)  # Get 2-digit month
        cut_off = cut_off_map.get(doc.cut_off)  # Get 2-digit cut-off

        if not month:
            frappe.throw("Invalid Month Name. Please enter a valid month.")
        if not cut_off:
            frappe.throw("Invalid Cut-off Value. Please select a valid cut-off.")

        doc.year_month_cut_off = int(f"{year}{month}{cut_off}")  # Convert to integer

def before_save(doc, method=None):
    create_id_for_sorting(doc)

def before_validate(doc, method=None):
    check_duplicate_dtr(doc) 


    