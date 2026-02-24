# Copyright (c) 2023, CvSU and contributors
# For license information, please see license.txt

# import frappe
import frappe
import cvsu_hris.cvsu_hris.overrides.events.Employee as EmployeeDocValidator
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError
from itertools import combinations

class Test_Non_Academic_Distinctions_Recognition(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
    def setUp(self):
        #Create base award in lower case
        awards = ["award"]

        #Create different variations of base award
        awards.append(awards[0].capitalize())
        awards.append(awards[0].upper())
        awards.append(awards[1].swapcase())
        
        self.awards = list(awards)
        
        #Create more variations by adding spaces before and after each variations
        for award in awards:
            self.awards.append(f' {award} ')

        self.doc = frappe.new_doc("Employee")
    
    def test_non_academic_recognition_must_unique(self):
        non_acad_recognitions = []

        #Create non-acad recognition from each awards
        for award in self.awards:
            non_acad_recognition = frappe.new_doc("Non Academic Distinctions or Recognition")
            non_acad_recognition.other_information_non_academic_distinctions_recognition = award
            non_acad_recognitions.append(non_acad_recognition)

        #Pair together each non-acad recognitions and test that they are not unique
        for recognition1,recognition2 in combinations(non_acad_recognitions,2):
            self.doc.custom_non_academic_distinctions_recognition = [recognition1,recognition2]        
            with self.assertRaises(ValidationError) as ctx:
                EmployeeDocValidator.check_unique_non_academic_distinctions(self.doc)
            self.assertEquals(str(ctx.exception), "Non Academic distinctions or recognition must be unique!")