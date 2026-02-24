# Copyright (c) 2023, CvSU and contributors
# For license information, please see license.txt

# import frappe
import frappe
import cvsu_hris.cvsu_hris.overrides.events.Employee as EmployeeDocValidator
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError
from itertools import combinations

class Test_References(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
    def setUp(self):
        #Create base reference in lower case
        references = ["reference"]

        #Create different variations of base reference
        references.append(references[0].capitalize())
        references.append(references[0].upper())
        references.append(references[1].swapcase())
        
        self.references = list(references)
        
        #Create more variations by adding spaces before and after each variations
        for reference in references:
            self.references.append(f' {reference} ')

        self.doc = frappe.new_doc("Employee")

    def test_reference_must_unique(self):
        references = []

        #Create reference entry from each references 
        for ref in self.references:
            reference = frappe.new_doc("References")
            reference.references_name = ref
            references.append(reference)

        #Pair together each references and test that they are not unique
        for ref1,ref2 in combinations(references,2):
            self.doc.custom_references_ = [ref1,ref2]        
            with self.assertRaises(ValidationError) as ctx:
                EmployeeDocValidator.check_unique_references(self.doc)
            self.assertEquals(str(ctx.exception), "Reference must be unique!")

    def test_reference_must_three_entries(self):
        self.doc.custom_references_  = []

        #Create four unique references and add them one at a time
        for c in "ABCD":
            reference = frappe.new_doc("References")
            reference.references_name = f'{self.references[0]} {c}.'
            self.doc.custom_references_.append(reference)        
            
            if len(self.doc.custom_references_) == 3:
                EmployeeDocValidator.check_reference_has_three_entries(self.doc)
                continue

            with self.assertRaises(ValidationError) as ctx:
                EmployeeDocValidator.check_reference_has_three_entries(self.doc)
            self. assertEquals(str(ctx.exception), "The references must have exactly three entries!")
