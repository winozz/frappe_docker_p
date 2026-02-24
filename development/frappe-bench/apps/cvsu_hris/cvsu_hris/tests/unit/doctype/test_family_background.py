# Copyright (c) 2024, CvSU and Contributors
# See license.txt

# import frappe
import cvsu_hris.cvsu_hris.overrides.events.Employee as EmployeeDocValidator
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError
import frappe


class Test_Family_Background(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
    def setUp(self):
        self.doc = frappe.new_doc("Employee")
        self.doc.employee_number = 0
        self.doc.company = "Test Company"
    
    def test_raises_exception_when_multiple_non_child(self):
        relationships = ['Spouse', 'Father', 'Mother']

        for relationship in relationships:
            rel1 = frappe.new_doc("Family Background")
            rel1.relationship = relationship
            
            rel2 = frappe.new_doc("Family Background")
            rel2.relationship = relationship
            
            self.doc.custom_family = [rel1, rel2]
            
            with self.assertRaises(ValidationError) as ctx:
                EmployeeDocValidator.check_duplicate_family_relationship(self.doc)
            
            self.assertEquals(str(ctx.exception), "Cannot have multiple entry for spouse, father and mother!") 

    def test_no_exception_when_multiple_children(self):
        rel1 = frappe.new_doc("Family Background")
        rel1.relationship = "Children"
        
        rel2 = frappe.new_doc("Family Background")
        rel2.relationship = "Children"
        
        self.doc.custom_family = [rel1, rel2]

        EmployeeDocValidator.check_duplicate_family_relationship(self.doc)