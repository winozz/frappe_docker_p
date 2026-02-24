# Copyright (c) 2023, CvSU and contributors
# For license information, please see license.txt

import frappe
import datetime
import cvsu_hris.cvsu_hris.overrides.events.Employee as EmployeeDocValidator
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError
from itertools import combinations

class Test_Civil_Service_Eligibility(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
    def setUp(self):
        #Create base license in lower case
        licenses = ["license"]

        #Create different variations of base license
        licenses.append(licenses[0].capitalize())
        licenses.append(licenses[0].upper())
        licenses.append(licenses[1].swapcase())
        
        self.licenses = list(licenses)
        
        #Create more variations by adding spaces before and after each variations
        for license in licenses:
            self.licenses.append(f' {license} ')

        self.doc = frappe.new_doc("Employee")


    def test_unique_civil_service_eligibility(self):
        csc_eligibilities = []

        #Create csc eligibility from each license
        for license in self.licenses:
            csc_eligibility = frappe.new_doc("Civil Service Eligibility")
            csc_eligibility.civil_service_eligibility_license = license
            csc_eligibilities.append(csc_eligibility)

        #Pair together each csc eligibilities and test that they are not unique
        for csc1,csc2 in combinations(csc_eligibilities,2):
            self.doc.custom_civil_service_eligibility_ = [csc1,csc2]        
            with self.assertRaises(ValidationError) as ctx:
                EmployeeDocValidator.check_unique_civil_service_eligibility(self.doc)
            self.assertEquals(str(ctx.exception), "Civil service license must be unique!")


    def test_date_of_examination_less_than_date_of_validity(self):
        csc_eligibility = frappe.new_doc("Civil Service Eligibility")
        csc_eligibility.civil_service_license_date_validity = datetime.datetime.now()
        csc_eligibility.civil_service_date_examination = csc_eligibility.civil_service_license_date_validity + datetime.timedelta(days=1)

        # Unit test for Date of Examination/Conferment is less than the Date of Validity
        self.doc.custom_civil_service_eligibility_ = [csc_eligibility]

        with self.assertRaises(ValidationError) as ctx:
            EmployeeDocValidator.check_date_of_examination_less_than_date_of_validity(self.doc)
        self.assertEquals(str(ctx.exception), "Date of Examination/Conferment must be less than the Date of Validity!")