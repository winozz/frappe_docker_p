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
        #Create base organization in lower case
        organizations = ["organization"]

        #Create different variations of base organization
        organizations.append(organizations[0].capitalize())
        organizations.append(organizations[0].upper())
        organizations.append(organizations[1].swapcase())
        
        self.organizations = list(organizations)
        
        #Create more variations by adding spaces before and after each variations
        for org in organizations:
            self.organizations.append(f' {org} ')

        self.doc = frappe.new_doc("Employee")

    def test_voluntary_work_must_unique(self):
        voluntary_works = []

        #Create voluntary work experiences from each organizations 
        for org in self.organizations:
            voluntary_work = frappe.new_doc("Voluntary Work")
            voluntary_work.voluntary_work_organization_name = org
            voluntary_works.append(voluntary_work)

        #Pair together each voluntary works and test that they are not unique
        for vw1,vw2 in combinations(voluntary_works,2):
            self.doc.custom_voluntary_work_ = [vw1,vw2]        
            with self.assertRaises(ValidationError) as ctx:
                EmployeeDocValidator.check_unique_voluntary_work(self.doc)
            self.assertEquals(str(ctx.exception), "Voluntary Work must be unique!")

    def test_voluntary_work_dates_from_to(self):
        #Validate that the From (start date) is less than or equal to To (end date)
        voluntary_work_doc = frappe.new_doc("Voluntary Work")
        voluntary_work_doc.voluntary_work_inclusive_dates_to = datetime.datetime.now()
        voluntary_work_doc.voluntary_work_inclusive_dates_from = voluntary_work_doc.voluntary_work_inclusive_dates_to + datetime.timedelta(days=1)

        self.doc.custom_voluntary_work_ = [voluntary_work_doc]
        with self.assertRaises(ValidationError) as ctx:
            EmployeeDocValidator.check_voluntary_work_dates_from_to(self.doc)
        self.assertEquals(str(ctx.exception), "Voluntary Work From (start date) should be less than or equal to To (end date)")