
import frappe

def check_duplicate_service_record(doc):
    existing_record = frappe.db.exists(
        "Service Record",
        {
            "date": doc.date,
            "employee": doc.employee,
            "name": ["!=", doc.name]  # Exclude the current record when editing
        }
    )
    if existing_record:
        frappe.throw("A record with the same employee and date already exists.")

def before_validate(doc, method=None):
    check_duplicate_service_record(doc) 