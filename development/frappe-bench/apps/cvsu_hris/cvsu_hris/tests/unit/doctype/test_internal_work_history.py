# Copyright (c) 2023, CvSU and contributors
# For license information, please see license.txt

# import frappe
import frappe
import datetime
import cvsu_hris.cvsu_hris.overrides.events.Employee as EmployeeDocValidator
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError

class Test_Internal_Work_History(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
    def test_internal_work_history_must_unique(self):
        internal_work_history_doc_1 = frappe.new_doc("Employee Internal Work History")
        internal_work_history_doc_1.custom_iw_position = "Instructor I"
        internal_work_history_doc_1.from_date = datetime.datetime(2024,1,1)
        internal_work_history_doc_1.to_date = datetime.datetime(2025,1,1)
        internal_work_history_doc_1.custom_iw_status_appointment = "Permanent"

        internal_work_history_doc_2 = frappe.new_doc("Employee Internal Work History")
        internal_work_history_doc_2.custom_iw_position = "Instructor I"
        internal_work_history_doc_2.from_date = datetime.datetime(2024,1,1)
        internal_work_history_doc_2.to_date = datetime.datetime(2025,1,1)
        internal_work_history_doc_2.custom_iw_status_appointment = "Permanent"
        
        internal_work_history_doc_3 = frappe.new_doc("Employee Internal Work History")
        internal_work_history_doc_3.custom_iw_position = "INSTRUCTOR I"
        internal_work_history_doc_3.from_date = datetime.datetime(2024,1,1)
        internal_work_history_doc_3.to_date = datetime.datetime(2025,1,1)
        internal_work_history_doc_3.custom_iw_status_appointment = "PERMANENT"
        
        internal_work_history_doc_4 = frappe.new_doc("Employee Internal Work History")
        internal_work_history_doc_4.custom_iw_position = " INSTRUCTOR I "
        internal_work_history_doc_4.from_date = datetime.datetime(2024,1,1)
        internal_work_history_doc_4.to_date = datetime.datetime(2025,1,1)
        internal_work_history_doc_4.custom_iw_status_appointment = " PERMANENT "

#1&2
        self.doc = frappe.new_doc("Employee")
        self.doc.internal_work_history = [internal_work_history_doc_1,internal_work_history_doc_2]

        with self.assertRaises(ValidationError) as ctx:
            EmployeeDocValidator.check_unique_internal_work_experience(self.doc)

        self.assertEquals(str(ctx.exception), "Internal work experience must be unique!")
#1&3
        self.doc = frappe.new_doc("Employee")
        self.doc.internal_work_history = [internal_work_history_doc_1,internal_work_history_doc_3]

        with self.assertRaises(ValidationError) as ctx:
            EmployeeDocValidator.check_unique_internal_work_experience(self.doc)

        self.assertEquals(str(ctx.exception), "Internal work experience must be unique!")
#1&4
        self.doc = frappe.new_doc("Employee")
        self.doc.internal_work_history = [internal_work_history_doc_1,internal_work_history_doc_4]

        with self.assertRaises(ValidationError) as ctx:
            EmployeeDocValidator.check_unique_internal_work_experience(self.doc)

        self.assertEquals(str(ctx.exception), "Internal work experience must be unique!")
    
    def test_internal_work_history_dates_from_to(self):
        internal_work_history_doc_1 = frappe.new_doc("Employee Internal Work History")
        internal_work_history_doc_1.from_date = datetime.datetime.now() + datetime.timedelta(days=1)
        internal_work_history_doc_1.to_date = datetime.datetime.now()
#from&to
        self.doc = frappe.new_doc("Employee")
        self.doc.internal_work_history = [internal_work_history_doc_1]

        with self.assertRaises(ValidationError) as ctx:
            EmployeeDocValidator.check_date_of_internal_work_experience(self.doc)

        self.assertEquals(str(ctx.exception), "Date From (start date) must be less than or equal to To (end date) of entries in Internal Work Experience!")