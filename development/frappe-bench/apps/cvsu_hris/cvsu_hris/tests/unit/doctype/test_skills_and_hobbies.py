import frappe
import cvsu_hris.cvsu_hris.overrides.events.Employee as EmployeeDocValidator
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError
from itertools import combinations

class Test_Skills_and_Hobbies(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        #Create base skill in lower case
        skills_and_hobbies = ["skill"]

        #Create different variations of base skill
        skills_and_hobbies.append(skills_and_hobbies[0].capitalize())
        skills_and_hobbies.append(skills_and_hobbies[0].upper())
        skills_and_hobbies.append(skills_and_hobbies[1].swapcase())
        
        self.skills_and_hobbies = list(skills_and_hobbies)
        
        #Create more variations by adding spaces before and after each variations
        for skill in skills_and_hobbies:
            self.skills_and_hobbies.append(f' {skill} ')

        self.doc = frappe.new_doc("Employee")

    def test_skills_and_hobbies_are_unique(self):
        skills_and_hobbies = []

        #Create skill and hobby entry from each skills and hobbies 
        for skill1 in self.skills_and_hobbies:
            skill_and_hobby = frappe.new_doc("Special Skills and Hobbies")
            skill_and_hobby.special_skills_and_hobbies = skill1
            skills_and_hobbies.append(skill_and_hobby)

        #Pair together each skills and hobbies and test that they are not unique
        for skill1,skill2 in combinations(skills_and_hobbies,2):
            self.doc.custom_special_skills_hobbies = [skill1,skill2]                    
            with self.assertRaises(ValidationError) as ctx:
                EmployeeDocValidator.check_unique_skills_and_hobbies(self.doc)            
            self.assertEquals(str(ctx.exception), "Skills and Hobbies must be unique!") 