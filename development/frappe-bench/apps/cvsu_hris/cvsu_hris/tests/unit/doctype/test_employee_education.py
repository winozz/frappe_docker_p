# Copyright (c) 2023, CvSU and contributors
# For license information, please see license.txt

# import frappe
import frappe
import cvsu_hris.cvsu_hris.overrides.events.Employee as EmployeeDocValidator
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError

class Test_Employee_Education(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
    def test_employee_education_must_unique(self):
        employee_education_doc_1 = frappe.new_doc("Employee Education")
        employee_education_doc_1.custom_education_school_university = "Cavite State University"
        employee_education_doc_1.custom_education_period_of_attendance_from = 2024
        employee_education_doc_1.custom_education_period_of_attendance_to = 2025

        employee_education_doc_2 = frappe.new_doc("Employee Education")
        employee_education_doc_2.custom_education_school_university = "Cavite State University"
        employee_education_doc_2.custom_education_period_of_attendance_from = 2024
        employee_education_doc_2.custom_education_period_of_attendance_to = 2025

        employee_education_doc_3 = frappe.new_doc("Employee Education")
        employee_education_doc_3.custom_education_school_university = "CAVITE STATE UNIVERSITY"        
        employee_education_doc_3.custom_education_period_of_attendance_from = 2024
        employee_education_doc_3.custom_education_period_of_attendance_to = 2025

        employee_education_doc_4 = frappe.new_doc("Employee Education")
        employee_education_doc_4.custom_education_school_university = " Cavite State University "
        employee_education_doc_4.custom_education_period_of_attendance_from = 2024
        employee_education_doc_4.custom_education_period_of_attendance_to = 2025

#1&3
        self.doc = frappe.new_doc("Employee")
        self.doc.education = [employee_education_doc_1,employee_education_doc_3]

        with self.assertRaises(ValidationError) as ctx:
            EmployeeDocValidator.check_unique_employee_education(self.doc)

        self.assertEquals(str(ctx.exception), "Employee Education Details (School/University and Period of Attendance) must be unique!")
#1&4
        self.doc = frappe.new_doc("Employee")
        self.doc.education = [employee_education_doc_1,employee_education_doc_4]

        with self.assertRaises(ValidationError) as ctx:
            EmployeeDocValidator.check_unique_employee_education(self.doc)

        self.assertEquals(str(ctx.exception), "Employee Education Details (School/University and Period of Attendance) must be unique!")
    
    def test_employee_education_dates_from_to(self):
        employee_education_doc_1 = frappe.new_doc("Employee Education")
        employee_education_doc_1.custom_education_period_of_attendance_from = 2025
        employee_education_doc_1.custom_education_period_of_attendance_to = 2024
#from&to
        self.doc = frappe.new_doc("Employee")
        self.doc.education = [employee_education_doc_1]

        with self.assertRaises(ValidationError) as ctx:
            EmployeeDocValidator.check_employee_education_dates_from_to(self.doc)

        self.assertEquals(str(ctx.exception), "Employee Education (Period of Attendance) From (start date) should be less than or equal to To (end date)")