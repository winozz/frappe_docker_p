import frappe
import cvsu_hris.cvsu_hris.overrides.events.Employee as EmployeeDocValidator
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError
from itertools import combinations

class Test_Membership_in_association_or_Organization(FrappeTestCase):
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

    def test_membership_in_association_or_organization(self):
        memberships = []

        #Create memberships from each organizations 
        for org in self.organizations:
            membership = frappe.new_doc("Membership in Association or Organization")
            membership.other_information_membership_association_organization = org
            memberships.append(membership)

        #Pair together each memberships and test that they are not unique
        for membership1,membership2 in combinations(memberships,2):
            self.doc.custom_membership_association_organization = [membership1,membership2]        
            with self.assertRaises(ValidationError) as ctx:
                EmployeeDocValidator.check_unique_membership(self.doc)
            self.assertEquals(str(ctx.exception), "Membership in Association or Organization must be unique!")