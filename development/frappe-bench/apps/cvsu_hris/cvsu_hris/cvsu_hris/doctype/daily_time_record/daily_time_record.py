from frappe.model.document import Document
import frappe

class DailyTimeRecord(Document):
    pass  # Keep the original class as it is

@frappe.whitelist()
def get_year_options():
    """Fetch distinct years based on user role."""
    user = frappe.session.user  # Get the current logged-in user

    # Check if the user has the HR role
    is_hr = frappe.db.exists("Has Role", {"parent": user, "role": "HR User"})

    if is_hr:
        # If HR, fetch all distinct years
        years = frappe.db.sql_list("""
            SELECT DISTINCT year 
            FROM `tabDaily Time Record`
            ORDER BY year ASC
        """)
    else:
        # If not HR, fetch years specific to the user
        years = frappe.db.sql_list("""
            SELECT DISTINCT year 
            FROM `tabDaily Time Record`
            WHERE owner = %s
            ORDER BY year ASC
        """, (user,))

    return years if years else [""]
