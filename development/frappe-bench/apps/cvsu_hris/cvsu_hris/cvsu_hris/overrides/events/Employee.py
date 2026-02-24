import frappe
import re  # Required for regex functions like re.sub
import datetime
import zlib
import random

# def create_reference_code(doc):
#     reference_code = f'{doc.employee_number}{datetime.datetime.now().date()}{random.getrandbits(32)}'
#     doc.custom_reference_code = zlib.crc32(str.encode(reference_code))

def create_government_id_from_employee_id(doc):
    def get_primary_id(ids):
        for cid in ids:
            if cid.id_is_primary:
                return cid
        return None
    
    def get_company_id(ids):
        for cid in ids:
            if (cid.id_selected_type == "COMPANY ID" or (cid.id_other_type if cid.id_other_type else "").strip().upper() == "COMPANY ID") and cid.id_place == doc.company:
                return cid
        return None
    
    primary_id = get_primary_id(doc.custom_government_id)
    company_id = get_company_id(doc.custom_government_id)

    if company_id is None:
        cid = frappe.new_doc("ID")
        cid.id_selected_type = "COMPANY ID"
        cid.id_number = doc.employee_number
        cid.id_date = doc.date_of_joining
        cid.id_place = doc.company
        cid.parent = doc.name
        cid.parenttype = "Employee"
        cid.parentfield = "custom_government_id"
        
        if primary_id is None:
            cid.id_is_primary = True
        
        doc.custom_government_id.append(cid)

def check_duplicate_id_type(doc):
    #get all other id type without duplicate 
    other_ids={t.id_other_type.upper().strip() for t in doc.custom_government_id if t.id_selected_type == 'OTHERS'}
    
    #get all standard id type without duplicates then combine with other id types
    ids={t.id_selected_type for t in doc.custom_government_id if t.id_selected_type != 'OTHERS'}.union(other_ids)
    
    #check if the number of unique ID matches the number of listed ID
    if len(ids) < len(doc.custom_government_id):
        frappe.msgprint(msg='Cannot have multiple Government ID of the same type!',title='Error',raise_exception=frappe.ValidationError)    

def check_single_primary(doc):
    # Collect all government IDs and primary IDs
    all_ids = {t for t in doc.custom_government_id}  # All IDs (unique)
    primary_ids = {t for t in doc.custom_government_id if t.id_is_primary}  # Primary IDs (set to True)

    # Check if there are multiple IDs or no primary ID at all
    if doc.status != "Left" and len(primary_ids) > 1:  # If there are multiple primary IDs
        frappe.msgprint(
            msg='Cannot have multiple default Government IDs!',
            title='Error',
            raise_exception=frappe.ValidationError
        )
    
    # Skip this validation IF document is new
    if doc.is_new():
        return
    
    if doc.status != "Left" and len(primary_ids) == 0:  # If no primary ID is set
        frappe.msgprint(
            msg='No default Government ID is set!',
            title='Error',
            raise_exception=frappe.ValidationError
        )

def check_duplicate_family_relationship(doc):
    # Relationships allowed to appear multiple times
    allowed_multiple = ["Children", "Spouse"]
    # allowed_multiple = ["Children"]

    # Extract relationships from child table
    relationships = [t.relationship for t in doc.custom_family]

    # Filter out the ones that are not allowed multiple times
    restricted_relationships = [r for r in relationships if r not in allowed_multiple]

    # Check for duplicates in restricted relationships
    duplicates = {r for r in restricted_relationships if restricted_relationships.count(r) > 1}

    if duplicates:
        frappe.throw(
            f"You cannot have multiple entries for: {', '.join(duplicates)}",
            frappe.ValidationError
        )


def check_family_has_entries(doc):
    if doc.status != "Left" and len(doc.custom_family) < 1:
        frappe.msgprint(
            msg='The Family Background must have entries!',
            title='Error',
            raise_exception=frappe.ValidationError
        )

#check the unique training programs attended
def check_unique_trainings(doc):
    trainings = {f'{r.training_program_title.upper().strip()} {r.training_program_inclusive_dates_attendance_from} {r.training_program_inclusive_dates_attendance_to}' for r in doc.custom_training_programs_attended_}
    if len(trainings) < len(doc.custom_training_programs_attended_):
        frappe.msgprint(msg='Training programs attended must be unique!',title='Error',raise_exception=frappe.ValidationError)

#check that the From (start date) is less than or equal to To (end date) for trainings attended
def check_trainings_attended_dates_from_to(doc):
    for t in doc.custom_training_programs_attended_:
        if t.training_program_inclusive_dates_attendance_from > t.training_program_inclusive_dates_attendance_to:
            frappe.msgprint(msg= 'Training From (start date) should be less than or equal to To (end date)',title='Error',raise_exception=frappe.ValidationError)      

#check the unique non academic distinctions or recognition
def check_unique_non_academic_distinctions(doc):
    non_acad_distinctions = {r.other_information_non_academic_distinctions_recognition.upper().strip() for r in doc.custom_non_academic_distinctions_recognition}
    if len(non_acad_distinctions) < len(doc.custom_non_academic_distinctions_recognition):
        frappe.msgprint(msg='Non Academic distinctions or recognition must be unique!',title='Error',raise_exception=frappe.ValidationError)

#check the unique employee education details (school and period of attendance)
def check_unique_employee_education(doc):
    employee_education = {f'{r.custom_education_school_university.upper().strip()} {r.custom_education_period_of_attendance_from} {r.custom_education_period_of_attendance_to}' for r in doc.education}
    if len(employee_education) < len(doc.education):
        frappe.msgprint(msg='Employee Education Details (School/University and Period of Attendance) must be unique!',title='Error',raise_exception=frappe.ValidationError)

#check that the From (start date) is less than or equal to To (end date) for employee education
def check_employee_education_dates_from_to(doc):
    for t in doc.education:
        if t.custom_education_period_of_attendance_from > t.custom_education_period_of_attendance_to:
            frappe.msgprint(msg= 'Employee Education (Period of Attendance) From (start date) should be less than or equal to To (end date)',title='Error',raise_exception=frappe.ValidationError)      

def check_employee_education_has_entries(doc):
    if doc.status != "Left" and len(doc.education) < 1:
        frappe.msgprint(
            msg='The Educational Background must have entries!',
            title='Error',
            raise_exception=frappe.ValidationError
        )

def check_unique_membership(doc):
    membership = {m.other_information_membership_association_organization.upper().strip() for m in doc.custom_membership_association_organization}
    if len(membership) < len(doc.custom_membership_association_organization):
        frappe.msgprint(msg='Membership in Association or Organization must be unique!', title='Error', raise_exception=frappe.ValidationError)

def check_unique_skills_and_hobbies(doc):
    #check if the skills and hobbies are unique
    skills_and_hobbies = {sh.special_skills_and_hobbies.upper().strip() for sh in doc.custom_special_skills_hobbies}
    if len(skills_and_hobbies) < len(doc.custom_special_skills_hobbies):
        frappe.msgprint(msg='Skills and Hobbies must be unique!',title='Error',raise_exception=frappe.ValidationError)    

def check_unique_references(doc):
    #check if the entries for references are unique
    references = {r.references_name.upper().strip() for r in doc.custom_references_}
    if len(references) < len(doc.custom_references_):
        frappe.msgprint(msg='Reference must be unique!',title='Error',raise_exception=frappe.ValidationError)
     
def check_reference_has_three_entries(doc):
    if doc.status != "Left" and len(doc.custom_references_) != 3:
        frappe.msgprint(
            msg='The References must have exactly three entries!',
            title='Error',
            raise_exception=frappe.ValidationError
        )

def check_unique_civil_service_eligibility(doc):
    #check if the civil service license is unique
    civil_service_eligibility_licenses = {cs.civil_service_eligibility_license.upper().strip() for cs in doc.custom_civil_service_eligibility_}
    if len(civil_service_eligibility_licenses) < len(doc.custom_civil_service_eligibility_):
        frappe.msgprint(msg='Civil service license must be unique!', title='Error', raise_exception=frappe.ValidationError)

def check_date_of_examination_less_than_date_of_validity(doc):
    #check if Date of Examination/Conferment is less than the Date of Validity
    for de in doc.custom_civil_service_eligibility_:
        if de.civil_service_license_date_validity and de.civil_service_date_examination > de.civil_service_license_date_validity:
            frappe.msgprint(msg= 'Date of Examination/Conferment must be less than the Date of Validity!',title='Error',raise_exception=frappe.ValidationError) 

def check_unique_voluntary_work(doc):
    #check if voluntary work entries are unique
    voluntary_work = {f'{v.voluntary_work_organization_name.upper().strip()}:{v.voluntary_work_inclusive_dates_from}-{v.voluntary_work_inclusive_dates_to}:{v.voluntary_work_position.upper().strip() if v.voluntary_work_position else ""}' for v in doc.custom_voluntary_work_}
    if len(voluntary_work) < len(doc.custom_voluntary_work_):
        frappe.msgprint(msg='Voluntary Work must be unique!',title='Error',raise_exception=frappe.ValidationError)

def check_voluntary_work_dates_from_to(doc):
    #check if From (start date) is less than or equal to To (end date)
    for vw in doc.custom_voluntary_work_:
        if vw.voluntary_work_inclusive_dates_from > vw.voluntary_work_inclusive_dates_to:
            frappe.msgprint(msg= 'Voluntary Work From (start date) should be less than or equal to To (end date)',title='Error',raise_exception=frappe.ValidationError)  

def check_unique_external_work_experience(doc):
    #check if external work experience entries are unique
    external_work = {f'{r.custom_ew_position.upper().strip()} {r.custom_ew_from_date} {r.custom_ew_to_date} {r.custom_ew_status_appointment.upper().strip()}' for r in doc.external_work_history}
    if len(external_work) < len(doc.external_work_history):
        frappe.msgprint(msg='External work experience must be unique!',title='Error',raise_exception=frappe.ValidationError)

def check_unique_internal_work_experience(doc):
    #check if internal work experience entries are unique
    internal_work = {f'{r.custom_iw_position.upper().strip()} {r.from_date} {r.to_date} {r.custom_iw_status_appointment.upper().strip()}' for r in doc.internal_work_history}
    if len(internal_work) < len(doc.internal_work_history):
        frappe.msgprint(msg='Internal work experience must be unique!',title='Error',raise_exception=frappe.ValidationError)

def check_date_of_external_work_experience(doc):
    #checks if external work experience date From is less than To
    for ewd in doc.external_work_history:
        if ewd.custom_ew_from_date > ewd.custom_ew_to_date:
             frappe.msgprint(msg="Date From (start date) must be less than or equal to To (end date) of entries in External Work Experience!",title='Error',raise_exception=frappe.ValidationError)

def check_date_of_internal_work_experience(doc):
    #checks if internal work experience date From is less than To
    for iwd in doc.internal_work_history:
        if not iwd.custom_is_present_work and not iwd.to_date:
            # if  is not None:
            if iwd.from_date > iwd.to_date:
                frappe.msgprint(msg="Date From (start date) must be less than or equal to To (end date) of entries in Internal Work Experience!",title='Error',raise_exception=frappe.ValidationError)

def validate_id(doc):
    check_duplicate_id_type(doc)
    check_single_primary(doc)

def validate_family_relationships(doc):
    check_duplicate_family_relationship(doc)

def validate_family(doc):
    check_family_has_entries(doc)

def validate_trainings(doc):
    check_unique_trainings(doc)
    check_trainings_attended_dates_from_to(doc)

def validate_non_academic_distinctions(doc):
    check_unique_non_academic_distinctions(doc)

def validate_skills_and_hobbies(doc):
    check_unique_skills_and_hobbies(doc)

def validate_employee_education(doc):
    check_unique_employee_education(doc)
    check_employee_education_dates_from_to(doc)
    check_employee_education_has_entries(doc)

def validate_work_experiences(doc):
    check_unique_internal_work_experience(doc)
    check_unique_external_work_experience(doc)
    check_date_of_internal_work_experience(doc)
    check_date_of_external_work_experience(doc)

def validate_membership(doc):
    check_unique_membership(doc)

def validate_references(doc):
    check_unique_references(doc)
    
    # Only enforce exactly 3 references if Status is NOT "Left"
    check_reference_has_three_entries(doc)
    #If references is mandatory then check if it contains 3 entries
    # if len(doc.meta.get("fields", {"reqd": ("=", 1),"fieldname": "custom_references_"})) > 0:
    #     check_reference_has_three_entries(doc)

def validate_eligibility(doc):
    check_unique_civil_service_eligibility(doc)
    check_date_of_examination_less_than_date_of_validity(doc)

def validate_voluntary_work(doc):
    check_unique_voluntary_work(doc)
    check_voluntary_work_dates_from_to(doc)

# def before_insert(doc, method=None):
    

def after_insert(doc, method=None):
    emp_number=int(doc.name.split('-')[2])
    doc.employee_number=emp_number
    doc.attendance_device_id=emp_number
    create_government_id_from_employee_id(doc)
    doc.save()

def before_validate(doc, method=None):
    validate_family_relationships(doc)
    validate_family(doc)    
    validate_id(doc)    
    validate_employee_education(doc)
    validate_trainings(doc)
    validate_non_academic_distinctions(doc)
    validate_work_experiences(doc)
    validate_eligibility(doc)
    validate_skills_and_hobbies(doc)
    validate_voluntary_work(doc)
    validate_membership(doc)
    validate_references(doc)
    # create_reference_code(doc)


def before_save(doc, method=None):
    # Clean gov ID
    for i, d in enumerate(doc.custom_government_id):
        if d.id_selected_type == 'OTHERS':
            doc.custom_government_id[i].id_other_type = doc.custom_government_id[i].id_other_type.strip().upper()

    # Cleaner function
    def clean_string(s):
        s = s.replace("'", "").replace('"', "")   # remove quotes
        s = re.sub(r"\s+", " ", s)                # normalize spaces
        return s.strip().upper()                  # trim + uppercase

    # --- Fields to skip (main table) ---
    EXCLUDED_FIELDS = {
        "custom_preferred_post_nominal_titles",
        "personal_email",
        "company_email"
    }

    # --- Child table field exclusions ---
    CHILD_TABLE_EXCLUDED_FIELDS = {
        # format: "ChildDoctype.fieldname"
        "Employee Internal Work History.custom_remarks"
    }

    # --- Process fields in Employee DocType ---
    for field in doc.meta.fields:
        if field.fieldtype in ["Data", "Small Text", "Text", "Code"]:
            if field.fieldname in EXCLUDED_FIELDS:
                continue

            value = doc.get(field.fieldname)
            if isinstance(value, str):
                doc.set(field.fieldname, clean_string(value))

        # --- Process child tables ---
        elif field.fieldtype == "Table":
            child_table = doc.get(field.fieldname)
            if child_table:
                for row in child_table:

                    child_meta = frappe.get_meta(row.doctype)

                    for child_field in child_meta.fields:
                        if child_field.fieldtype in ["Data", "Small Text", "Text", "Code"]:

                            # Check if this child field is excluded
                            full_key = f"{row.doctype}.{child_field.fieldname}"
                            if full_key in CHILD_TABLE_EXCLUDED_FIELDS:
                                continue

                            val = row.get(child_field.fieldname)
                            if isinstance(val, str):
                                row.set(child_field.fieldname, clean_string(val))

    # If employee is marked as Left, allow saving even if first_name is empty
    if doc.status == "Left":
        # remove first_name from mandatory list
        doc.flags.ignore_mandatory = True
