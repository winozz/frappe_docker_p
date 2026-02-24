from frappe.tests.utils import FrappeTestCase

import frappe
import datetime
import cvsu_hris.cvsu_hris.overrides.events.Employee as Employee



class TestEmployee(FrappeTestCase):

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        #Unsaved Employee Document with Solo Parent and PWD ID
        doc_with_id = frappe.new_doc("Employee")

        #Unsaved Employee Document without Solo Parent and PWD ID
        doc_without_id = frappe.new_doc("Employee")
        
        #Solo Parent ID
        solo_parent_id = frappe.new_doc("ID")
        solo_parent_id.id_selected_type = "SOLO PARENT"
        solo_parent_id.id_number = "1"

        #PWD ID
        pwd_id = frappe.new_doc("ID")
        pwd_id.id_selected_type = "PWD"
        pwd_id.id_number = "2"
        
        #Set the Solo Parent and PWD ID 
        doc_with_id.custom_government_id = [solo_parent_id, pwd_id]
        

        self.government_id = doc_with_id.custom_government_id
        
        #Retieve the document field values with computed virtual field values as dictionaries
        self.doc_with_id_values = doc_with_id.as_dict()
        self.doc_without_id_values = doc_without_id.as_dict()

    def test_must_be_solo_parent(self):
        self.assertEqual(self.doc_with_id_values['custom_is_solo_parent'], 'YES', 
                         'Has Solo Parent ID but not set as Solo Parent')

    def test_must_match_solo_parent_id(self):
        self.assertEqual(self.doc_with_id_values['custom_solo_parent_id_number'], 
                         self.government_id[0].id_number,
                         'ID does not match the given Solo Parent ID')
        
    def test_must_be_pwd(self):
        self.assertEqual(self.doc_with_id_values['custom_is_disabled'], 'YES', 
                         'Has PWD ID but not set as PWD')

    def test_must_match_pwd_id(self):
        self.assertEqual(self.doc_with_id_values['custom_disability_id_number'], 
                         self.government_id[1].id_number,
                         'ID does not match the given PWD ID')

    def test_must_not_be_solo_parent(self): 
        self.assertEqual(self.doc_without_id_values['custom_is_solo_parent'], 'NO',
                         'Has no Solo Parent ID but set as Solo Parent')
        self.assertEqual(self.doc_without_id_values['custom_solo_parent_id_number'], '',
                         'Solo Parent ID not empty')

    def test_must_not_be_pwd(self):
        self.assertEqual(self.doc_without_id_values['custom_is_disabled'], 'NO',
                         'Has no PWD ID but set as Disabled')
        self.assertEqual(self.doc_without_id_values['custom_disability_id_number'], '',
                         'PWD ID not empty')

    def test_must_sync_residential_and_permanent_if_selected(self):
        doc = frappe.new_doc("Employee")
        doc.custom_residential_house_block_lot_number = "House Lot No."
        doc.custom_residential_street = "Street"
        doc.custom_residential_subdivision_village = "Subd. Village"
        doc.custom_residential_barangay = "Barangay"
        doc.custom_residential_city_municipality = "Municipality"
        doc.custom_residential_province = "Province"
        doc.custom_residential_zip_code = "Zip"

        doc.custom_is_same_as_residential_address = True

        Employee.sync_residential_and_permanent_address(doc)

        self.assertEqual(doc.custom_residential_house_block_lot_number, doc.custom_permanent_house_block_lot_number,
                        "Residential house number is not the same as permanent house number!")
        
        self.assertEqual(doc.custom_residential_street, doc.custom_permanent_street,
                        "Residential street address is not the same as permanent street address!")
        
        self.assertEqual(doc.custom_residential_subdivision_village, doc.custom_permanent_subdivision_village,
                        "Residential subdivision/village address is not the same as permanent subdivision/village address!")
        
        self.assertEqual(doc.custom_residential_barangay, doc.custom_permanent_barangay,
                        "Residential barangay address is not the same as permanent barangay address")
        
        self.assertEqual(doc.custom_residential_city_municipality, doc.custom_permanent_city_municipality,
                        "Residential city/municipality address is not the same as permanent city/municipality address!")

        self.assertEqual(doc.custom_residential_province, doc.custom_permanent_province,
                        "Residential province address is not the same as permanent province address!")

        self.assertEqual(doc.custom_residential_zip_code, doc.custom_permanent_zip_code,
                        "Residential zip code is not the same as permanent zip code!")

    def test_must_sync_internal_work_to_date_date_today_if_selected(self):
        doc = frappe.new_doc("Employee Internal Work History")

        doc.custom_is_present_work = True

        Employee.sync_internal_work_to_date_date_today(doc)

        self.assertEqual(doc.to_date, datetime.datetime.now().date(),
                        "To Date is not the same with the Date Today!")
    
        