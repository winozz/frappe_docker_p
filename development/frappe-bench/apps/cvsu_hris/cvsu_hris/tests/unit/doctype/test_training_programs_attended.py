# Copyright (c) 2023, CvSU and contributors
# For license information, please see license.txt

# import frappe
import frappe
import datetime
import cvsu_hris.cvsu_hris.overrides.events.Employee as EmployeeDocValidator
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError
from itertools import combinations

class Test_Training_Program_Attended(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
    def setUp(self):
        #Create base training in lower case
        trainings = ["training"]

        #Create different variations of base training
        trainings.append(trainings[0].capitalize())
        trainings.append(trainings[0].upper())
        trainings.append(trainings[1].swapcase())
        
        self.trainings = list(trainings)
        
        #Create more variations by adding spaces before and after each variations
        for training in trainings:
            self.trainings.append(f' {training} ')

        self.doc = frappe.new_doc("Employee")

    def test_training_must_unique(self):
        training_programs = []

        #Create training programs from each trainings
        for training in self.trainings:
            training_program = frappe.new_doc("Training Programs Attended")
            training_program.training_program_title = training
            training_programs.append(training_program)

        #Pair together each training programs and test that they are not unique
        for tp1,tp2 in combinations(training_programs,2):
            self.doc.custom_training_programs_attended_ = [tp1,tp2]        
            with self.assertRaises(ValidationError) as ctx:
                EmployeeDocValidator.check_unique_trainings(self.doc)
            self.assertEquals(str(ctx.exception), "Training programs attended must be unique!")

    def test_training_dates_from_to(self):
        training_doc = frappe.new_doc("Training Programs Attended")
        training_doc.training_program_inclusive_dates_attendance_to = datetime.datetime.now()
        training_doc.training_program_inclusive_dates_attendance_from = training_doc.training_program_inclusive_dates_attendance_to + datetime.timedelta(days=1)

        self.doc.custom_training_programs_attended_ = [training_doc]
        with self.assertRaises(ValidationError) as ctx:
            EmployeeDocValidator.check_trainings_attended_dates_from_to(self.doc)

        self.assertEquals(str(ctx.exception), "Training From (start date) should be less than or equal to To (end date)")