# Copyright (c) 2024, CvSU and Contributors
# See license.txt

# import frappe
import cvsu_hris.cvsu_hris.overrides.events.Employee as EmployeeDocValidator
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError
import frappe
from itertools import combinations


class TestID(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()

	def setUp(self):
		self.doc = frappe.new_doc("Employee")
		self.doc.employee_number = 0
		# self.doc.company = frappe.new_doc('Company')
		self.doc.company = "Test Company"
		
	def test_raises_exception_when_no_primary_id(self):
		#Create a new blank ID document 
		self.doc.custom_government_id = [frappe.new_doc("ID")]
		
		#Create a context manager that expects an execpetion.
		with self.assertRaises(ValidationError) as ctx:
			EmployeeDocValidator.check_single_primary(self.doc)

		#Check if the exception has the expected message
		self.assertEquals(str(ctx.exception), "No default ID is set!") 

	def test_raises_exception_when_multiple_primary_id(self):
		#Two standard and two non-standard ID
		ids_metadata = [("GSIS",None),("SSS",None),("OTHERS","ID 1"),("OTHERS","ID 2")]

		#Create id from each metadata 
		ids = []		
		for selected_type,other_type in ids_metadata:
			id = frappe.new_doc("ID")
			id.id_selected_type = selected_type
			id.id_other_type = other_type
			id.id_is_primary = True
			ids.append(id)
		
		#Pair together each ID and test that there are multiple default ID
		for id1,id2 in combinations(ids,2):
			self.doc.custom_government_id = [id1,id2]        
			with self.assertRaises(ValidationError) as ctx:
				EmployeeDocValidator.check_single_primary(self.doc)
			self.assertEquals(str(ctx.exception), "Cannot have multiple default ID!") 


	def test_raises_exception_when_multiple_same_type(self):
		#Create standard ID
		ids_metadata = [("GSIS",None)]

		#Create different variations of standard ID
		#Duplicate Standard ID
		ids_metadata.append((ids_metadata[0][0], None))
		#Duplicate Non-Standard ID
		ids_metadata.append(("OTHERS", ids_metadata[0][0]))
		#Variations of Non-Standard ID
		ids_metadata.append(("OTHERS", ids_metadata[0][0].capitalize()))
		ids_metadata.append(("OTHERS", ids_metadata[0][0].lower()))
		ids_metadata.append(("OTHERS", ids_metadata[0][0].capitalize().swapcase()))

		#Create more variations from non-standard id by adding spaces
		for selected_type,other_type in ids_metadata[2:6]:
			ids_metadata.append((selected_type,f' {other_type} '))

		#Create id from each metadata 
		ids = []		
		for selected_type,other_type in ids_metadata:
			id = frappe.new_doc("ID")
			id.id_selected_type = selected_type
			id.id_other_type = other_type
			id.id_is_primary = True
			ids.append(id)
		
		#Pair together each ID and test that they are not unique
		for id1,id2 in combinations(ids,2):
			self.doc.custom_government_id = [id1,id2]        
			with self.assertRaises(ValidationError) as ctx:
				EmployeeDocValidator.check_duplicate_id_type(self.doc)
			self.assertEquals(str(ctx.exception), "Cannot have multiple ID of the same type!") 

	def test_must_create_company_id_when_it_doesnt_exists(self):
		#Case when government ID list is empty
		# self.doc.run_method("before_insert")
		EmployeeDocValidator.create_government_id_from_employee_id(self.doc)
		company_id = self._get_company_id()
		self.assertIsNotNone(company_id , "No Company ID added")

		#Case when government ID list is not empty but does not include a Company ID
		cid = frappe.new_doc("ID")
		cid.id_number = 1
		cid.id_selected_type = "OTHERS"
		self.doc.custom_government_id = [cid]
		# self.doc.run_method("before_insert")
		EmployeeDocValidator.create_government_id_from_employee_id(self.doc)
		company_id = self._get_company_id()
		self.assertIsNotNone(company_id , "No Company ID added")


	def test_must_not_create_company_id_when_it_exists(self):
		cid = frappe.new_doc("ID")
		cid.id_number = 1
		cid.id_selected_type = "COMPANY ID"
		cid.id_place = self.doc.company
		self.doc.custom_government_id = [cid]
		# self.doc.run_method("before_insert")
		EmployeeDocValidator.create_government_id_from_employee_id(self.doc)
		company_id = self._get_company_id()
		self.assertIsNone(company_id , "Duplicate Company ID added")
	

	def test_must_make_company_id_primary_when_primary_id_doesnt_exists(self):
		#Case when the government ID list is empty
		# self.doc.run_method("before_insert")
		EmployeeDocValidator.create_government_id_from_employee_id(self.doc)
		company_id = self._get_company_id()
		self.assertTrue(company_id.id_is_primary , "Company ID should be primary")

		#Case when government ID list is not empty but does not include a primary ID
		cid = frappe.new_doc("ID")
		cid.id_number = 1
		cid.id_selected_type = "OTHERS"
		self.doc.custom_government_id = [cid]
		# self.doc.run_method("before_insert")
		EmployeeDocValidator.create_government_id_from_employee_id(self.doc)
		self.assertTrue(company_id.id_is_primary , "Company ID should be primary")
	

	def test_must_not_make_company_id_primary_when_primary_id_exists(self):
		cid = frappe.new_doc("ID")
		cid.id_number = 1
		cid.id_selected_type = "OTHERS"
		cid.id_is_primary = True
		self.doc.custom_government_id = [cid]
		# self.doc.run_method("before_insert")
		EmployeeDocValidator.create_government_id_from_employee_id(self.doc)
		company_id = self._get_company_id()
		self.assertFalse(company_id.id_is_primary , "Company ID should not be primary")


	def _get_company_id(self):
		for cid in self.doc.custom_government_id:
			
			doc_name, emp_number, company = self.doc.name, self.doc.employee_number, self.doc.company

			if (cid.id_selected_type == "COMPANY ID" and cid.id_number == emp_number and cid.id_place == company and 
	   			cid.parent == doc_name and cid.parenttype == "Employee" and cid.parentfield == "custom_government_id"):

				return cid
		return None
		