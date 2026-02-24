import Alpine from 'alpinejs';
import CellData from './celldata';
import $ from 'jquery';

const EDUCATION_LEVELS = {
	'elementary': elementary, 
	'secondary': secondary, 
	'vocational': vocational, 
	'college': college,
	'graduate_studies': graduate_studies
}

function mmddyyyy_to_ddmmyyyy(dateStr) {
	if (!dateStr || dateStr === 'N/A' || dateStr === 'PRESENT') return dateStr;

	const parts = dateStr.split('/');
	if (parts.length !== 3) return dateStr;

	const [mm, dd, yyyy] = parts;
	return `${dd}/${mm}/${yyyy}`;
}

//uppercase all Strings
function toUpperCaseEntries(obj) {
	return Object.fromEntries(Object.entries(obj).map(([k, v]) => typeof v == "string" ? [k, v.toUpperCase()] : [k,v]));
}  

//return N/A if null
function replaceNullValues(obj,replacement='N/A') {
	return Object.fromEntries(Object.entries(obj).map(([k, v]) => v  ? [k,v] : [k,replacement] ));

}

//Set entry to be last. This is for entries that are N/A and Nothing Follows
function make_entry_terminal(entry, merged= true ,text='Nothing follows'){
	entry.is_terminal = true;
	entry.fields[0].text = text;
	entry.fields.slice(1).forEach(field => {
		if(merged){
			entry.fields[0].colspan += field.colspan  
			field.merged = true;
			field.text = "";
		}else{
			field.text = text;
		}
	});
}

//PDS Page 1
function load_umid_id(){
	!umid_id ? $(`#T-C1 tr.R-27 td.C-4`).html('N/A') : $(`#T-C1 tr.R-27 td.C-4`).html(umid_id['id_number'])
}

function load_pagibig_id(){
	!pagibig_id ? $(`#T-C1 tr.R-29 td.C-4`).html('N/A') : $(`#T-C1 tr.R-29 td.C-4`).html(pagibig_id['id_number'])
}

function load_philhealth_id(){
	!philhealth_id ? $(`#T-C1 tr.R-31 td.C-4`).html('N/A') : $(`#T-C1 tr.R-31 td.C-4`).html(philhealth_id['id_number'])
}

function load_philsys_id(){
	!philsys_id ? $(`#T-C1 tr.R-32 td.C-4`).html('N/A') : $(`#T-C1 tr.R-32 td.C-4`).html(philsys_id['id_number'])
}

function load_tin_id(){
	!tin_id ? $(`#T-C1 tr.R-33 td.C-4`).html('N/A') : $(`#T-C1 tr.R-33 td.C-4`).html(tin_id['id_number'])
}

function load_spouse(){
    var row = 36
	const LAST_ROW = 42
	if(!spouse){
		for(row; row<=LAST_ROW; row++){
			$(`#T-C1 tr.R-${row} td.C-4`).html('N/A')
		}
		$(`#T-C1 tr.R-37 td.C-7`).html(`${$(`#T-C1 tr.R-37 td.C-7`).html()} <strong>N/A</strong>`)
	}
	else{
		spouse = toUpperCaseEntries(replaceNullValues(spouse))
		let name_extension = `${$(`#T-C1 tr.R-37 td.C-7`).html()} <strong> ${spouse['name_extension'] ? spouse['name_extension'] : 'N/A'} </strong>`  
		$(`#T-C1 tr.R-36 td.C-4`).html(spouse['surname'])
		$(`#T-C1 tr.R-37 td.C-4`).html(spouse['first_name'])
		$(`#T-C1 tr.R-37 td.C-7`).html(name_extension)
		$(`#T-C1 tr.R-38 td.C-4`).html(spouse['middle_name'])
		$(`#T-C1 tr.R-39 td.C-4`).html(spouse['occupation'])
		$(`#T-C1 tr.R-40 td.C-4`).html(spouse['employers_business_name'])
		$(`#T-C1 tr.R-41 td.C-4`).html(spouse['employers_business_address'])
		$(`#T-C1 tr.R-42 td.C-4`).html(spouse['telephone_number'])
	}
}

function load_father(){
    var row = 43
	const LAST_ROW = 45
	if(!father){
		for(row; row<=LAST_ROW; row++){
			$(`#T-C1 tr.R-${row} td.C-4`).html('N/A')
		}
		$(`#T-C1 tr.R-44 td.C-7`).html(`${$(`#T-C1 tr.R-44 td.C-7`).html()} <strong>N/A</strong>`)
	}
	else{
		father = toUpperCaseEntries(replaceNullValues(father))
		let name_extension = `${$(`#T-C1 tr.R-44 td.C-7`).html()} <strong> ${father['name_extension'] ? father['name_extension'] : 'N/A'} </strong>`  
		$(`#T-C1 tr.R-43 td.C-4`).html(father['surname'] ?? 'N/A')
		$(`#T-C1 tr.R-44 td.C-4`).html(father['first_name'] ?? 'N/A')
		$(`#T-C1 tr.R-44 td.C-7`).html(name_extension)
		$(`#T-C1 tr.R-45 td.C-4`).html(father['middle_name'] ?? 'N/A')
	}
}

function load_mother(){
    var row = 47
	const LAST_ROW = 49
	if(!mother){
		for(row; row<=LAST_ROW; row++){
			$(`#T-C1 tr.R-${row} td.C-4`).html('N/A')
		}
	}
	else{
		mother = toUpperCaseEntries(replaceNullValues(mother))
		$(`#T-C1 tr.R-47 td.C-4`).html(mother['surname'] ?? 'N/A')
		$(`#T-C1 tr.R-48 td.C-4`).html(mother['first_name'] ?? 'N/A')
		$(`#T-C1 tr.R-49 td.C-4`).html(mother['middle_name'] ?? 'N/A')
	}
}

function load_children(){
	const start_row = 37, end_row = 48, max_rows = end_row - start_row + 1;
	let store = Alpine.store('children');

	if(children.length == 0){
		make_entry_terminal(store[0], false, 'N/A');
	}else{
		let last_indx = 0;
		children.forEach(function(child, indx){
			child = toUpperCaseEntries(replaceNullValues(child))
			let child_name = child['first_name'] + ' ' + 
							(child['middle_name']=='N/A' ? '' : child['middle_name'][0] + '. ')  + 
							child['surname'] +
							(child['name_extension']=='N/A' ? '' : ' ' + child['name_extension']);

			if(indx >= store.length){
				//Create new entry when full
				store.push({
					is_terminal:false,
					fields: Array.from({length: 2}, () => new CellData(1,1,false,''))
				});
			}			
			
			let entry = store[indx];
			entry.is_terminal = false;
			entry.fields[0].text = child_name;
			entry.fields[1].text = mmddyyyy_to_ddmmyyyy(child['date_of_birth']);

			last_indx = indx;
		})
		//Create Nothing Follows if needed
		if(last_indx < max_rows - 1){
			make_entry_terminal(store[last_indx + 1]);
		}
	}
}

function load_education(level){
	let store = Alpine.store(level);
	let education_level = EDUCATION_LEVELS[level];

	if(education_level.length == 0){
		make_entry_terminal(store[0], false, 'N/A');
	}else{
		education_level.forEach(function(education, indx){
            education = toUpperCaseEntries(replaceNullValues(education))
			
			if(indx >= store.length){
				//Create new entry when full
				store.push({
					is_terminal:false,
					fields: Array.from({length: 7}, () => new CellData(1,1,false,''))
				});
			}

			let period_of_attendance_to, year_graduated;
			if(education['custom_education_is_completed']==1){
				period_of_attendance_to = education['custom_education_period_of_attendance_to']
				year_graduated = education['custom_education_period_of_attendance_to']
			}else{
				if(new Date().getFullYear() != education['custom_education_period_of_attendance_to']){
					period_of_attendance_to = education['custom_education_period_of_attendance_to']
				}  
				else{
					period_of_attendance_to = 'PRESENT'
				}
				year_graduated = 'N/A'
			}

			let entry = store[indx];
			entry.is_terminal = false;
			entry.fields[0].text = education['custom_education_school_university'];
			entry.fields[1].text = education['custom_education_degree_course'];
			entry.fields[2].text = education['custom_education_period_of_attendance_from'];
			entry.fields[3].text = period_of_attendance_to;
			entry.fields[4].text = education['custom_education_units_earned'];
			entry.fields[5].text = year_graduated;
			entry.fields[6].text = education['custom_education_scholarship_academic_honors_received'];
		})
	}
}

//PDS Page 2
function load_civil_service_eligibilities(){
	const start_row = 5, end_row = 11, max_rows = end_row - start_row + 1;
	let store = Alpine.store('eligibilities');
	
	if(civil_service_eligibilities.length == 0){
		make_entry_terminal(store[0], false, 'N/A');
	}else{
		let last_indx = 0;
		civil_service_eligibilities.forEach(function(eligibility, indx){
            eligibility = toUpperCaseEntries(replaceNullValues(eligibility))
			// console.log(eligibility)
			if(indx >= store.length){
				//Create new entry when full
				store.push({
					is_terminal:false,
					fields: Array.from({length: 6}, () => new CellData(1,1,false,''))
				});
			}
			
			let entry = store[indx];
			entry.is_terminal = false;
			entry.fields[0].text = eligibility['civil_service_eligibility_license'];
			entry.fields[1].text = eligibility['civil_service_rating'];
			entry.fields[2].text = mmddyyyy_to_ddmmyyyy(eligibility['civil_service_date_examination']);
			entry.fields[3].text = eligibility['civil_service_place_examination'];
			entry.fields[4].text = eligibility['civil_service_license_number'];
			entry.fields[5].text = eligibility['civil_service_license_date_validity'];	
			
			last_indx = indx;
		})
		//Create Nothing Follows if needed
		if(last_indx < max_rows - 1){
			make_entry_terminal(store[last_indx + 1]);
		}
	}
}

function load_work_experiences(){
	const start_row = 18, end_row = 45, max_rows = end_row - start_row + 1;
	let store = Alpine.store('work_experiences');

	if(work_experiences.length == 0){
		make_entry_terminal(store[0], false, 'N/A');
	}else{
		let last_indx = 0;
		work_experiences.forEach(function(work_experience, indx){
            work_experience = toUpperCaseEntries(replaceNullValues(work_experience))
			
			let workplace = ([
				work_experience['company'], 
				work_experience['branch'], 
				work_experience['office'], 
				work_experience['unit']
			].filter(d => d != 'N/A')).join('/') 

			if(indx >= store.length){
				//Create new entry when full
				store.push({
					is_terminal:false,
					fields: Array.from({length: 8}, () => new CellData(1,1,false,''))
				});
			}

			let entry = store[indx];
			entry.is_terminal = false;
			// entry.fields[0].text = work_experience['from'];
			// entry.fields[1].text = work_experience['to'];
			entry.fields[0].text = mmddyyyy_to_ddmmyyyy(work_experience['from']);
			entry.fields[1].text = mmddyyyy_to_ddmmyyyy(work_experience['to']);
			entry.fields[2].text = work_experience['position'];
			entry.fields[3].text = workplace;

			// Determine which salary to use
			let raw_salary = "";

			// let status = (work_experience['status_appointment'] || "").toUpperCase();

			// if (status === "PART TIME/JOB ORDER" || status === "CONTRACT OF SERVICE") {
			// 	raw_salary = work_experience['hourly_salary'] || "";
			// } else {
			// 	raw_salary = work_experience['monthly_salary'] || "";
			// }

			raw_salary = work_experience['monthly_salary'] || "";

			// 1. Remove all characters except digits and period
			let clean = raw_salary.toString().replace(/[^0-9.]/g, "");

			// 2. Convert to number
			let num = Number(clean);

			// 3. Format with commas and always 2 decimals
			if (!isNaN(num) && clean !== "") {
				clean = num.toLocaleString("en-US", {
					minimumFractionDigits: 2,
					maximumFractionDigits: 2
				});
			} else {
				clean = "";
			}

			// 4. Append /m only if there is a numeric value
			let final_salary = clean ? clean : "";

			// Assign to field
			entry.fields[4].text = final_salary;

			entry.fields[5].text = work_experience['salary_grade'];
			entry.fields[6].text = work_experience['status_appointment'];
			entry.fields[7].text = work_experience['government_service'];

			last_indx = indx;
		})
		//Create Nothing Follows if needed
		if(last_indx < max_rows - 1){
			make_entry_terminal(store[last_indx + 1]);
		}
	}
}

//PDS Page 3
function load_voluntary_works(){
	const start_row = 6, end_row = 12, max_rows = end_row - start_row + 1;
	let store = Alpine.store('voluntary_works');
	
	if(voluntary_works.length == 0){
		make_entry_terminal(store[0], false, 'N/A');
	}else{
		let last_indx = 0;
		voluntary_works.forEach(function(voluntary_work,indx){
            voluntary_work = toUpperCaseEntries(replaceNullValues(voluntary_work))
			
			if(indx >= store.length){
				//Create new entry when full
				store.push({
					is_terminal:false,
					fields: Array.from({length: 5}, () => new CellData(1,1,false,''))
				});
			}

			let entry = store[indx];
			entry.is_terminal = false;
			entry.fields[0].text = voluntary_work['voluntary_work_organization_name'] + ' / ' + voluntary_work['voluntary_work_organization_address'];
			entry.fields[1].text = mmddyyyy_to_ddmmyyyy(voluntary_work['voluntary_work_inclusive_dates_from']);
			entry.fields[2].text = mmddyyyy_to_ddmmyyyy(voluntary_work['voluntary_work_inclusive_dates_to']);
			entry.fields[3].text = voluntary_work['voluntary_work_number_hours'];
			entry.fields[4].text = voluntary_work['voluntary_work_position'];

			last_indx = indx;
		})
		//Create Nothing Follows if needed
		if(last_indx < max_rows - 1){
			make_entry_terminal(store[last_indx + 1]);
		}
	}
}

function load_trainings(){
	const start_row = 37, end_row = 57, max_rows = end_row - start_row + 1;
	let store = Alpine.store('trainings');

	if(trainings.length == 0){
		make_entry_terminal(store[0], false, 'N/A');
	}else{
		let last_indx = 0;
		trainings.forEach(function(training, indx){
            training = toUpperCaseEntries(replaceNullValues(training))
			
			if(indx >= store.length){
				//Create new entry when full
				store.push({
					is_terminal:false,
					fields: Array.from({length: 6}, () => new CellData(1,1,false,''))
				});
			}

			let entry = store[indx];
			entry.is_terminal = false;
			entry.fields[0].text = training['training_program_title'];
			entry.fields[1].text = mmddyyyy_to_ddmmyyyy(training['training_program_inclusive_dates_attendance_from']);
			entry.fields[2].text = mmddyyyy_to_ddmmyyyy(training['training_program_inclusive_dates_attendance_to']);
			entry.fields[3].text = training['training_program_number_hours'];
			entry.fields[4].text = training['training_program_ld_type'];
			entry.fields[5].text = training['training_program_sponsored_by'];
			
			last_indx = indx;
		})
		//Create Nothing Follows if needed
		if(last_indx < max_rows - 1){
			make_entry_terminal(store[last_indx + 1]);
		}
	}
}

function load_skills_hobbies(){
	const start_row = 42, end_row = 48, max_rows = end_row - start_row + 1;
	let store = Alpine.store('skills');
	
	if(skills_hobbies.length == 0){
		make_entry_terminal(store[0], false, 'N/A');
	}else{
		let last_indx = 0;
		
		skills_hobbies.forEach(function(skill_hobby,indx){
            skill_hobby = toUpperCaseEntries(replaceNullValues(skill_hobby))
			
			if(indx >= store.length){
				//Create new entry when full
				store.push({
					is_terminal:false,
					fields: Array.from({length: 1}, () => new CellData(1,1,false,''))
				});
			}

			let entry = store[indx];
			entry.is_terminal = false;
			entry.fields[0].text = skill_hobby['special_skills_and_hobbies'];
			
			last_indx = indx;
		})
		//Create Nothing Follows if needed
		if(last_indx < max_rows - 1){
			make_entry_terminal(store[last_indx + 1]);
		}
	}
}

function load_non_academic_distinctions(){
	const start_row = 42, end_row = 48, max_rows = end_row - start_row + 1;
	let store = Alpine.store('recognitions');

	if(non_academic_distinctions.length == 0){
		make_entry_terminal(store[0], false, 'N/A');
	}else{
		let last_indx = 0;
		non_academic_distinctions.forEach(function(non_academic_distinction,indx){
            non_academic_distinction = toUpperCaseEntries(replaceNullValues(non_academic_distinction))
			
			if(indx >= store.length){
				//Create new entry when full
				store.push({
					is_terminal:false,
					fields: Array.from({length: 1}, () => new CellData(1,1,false,''))
				});
			}

			let entry = store[indx];
			entry.is_terminal = false;
			entry.fields[0].text = non_academic_distinction['other_information_non_academic_distinctions_recognition'];

			last_indx = indx;
		})
		//Create Nothing Follows if needed
		if(last_indx < max_rows - 1){
			make_entry_terminal(store[last_indx + 1]);
		}
	}
}

function load_memberships(){
	const start_row = 42, end_row = 48, max_rows = end_row - start_row + 1;
	let store = Alpine.store('organizations');

	if(memberships.length == 0){
		make_entry_terminal(store[0], false, 'N/A');
	}else{
		let last_indx = 0;
		memberships.forEach(function(membership, indx){
            membership = toUpperCaseEntries(replaceNullValues(membership))
			
			if(indx >= store.length){
				//Create new entry when full
				store.push({
					is_terminal:false,
					fields: Array.from({length: 1}, () => new CellData(1,1,false,''))
				});
			}

			let entry = store[indx];
			entry.is_terminal = false;
			entry.fields[0].text = membership['other_information_membership_association_organization'];

			last_indx = indx;
		})
		//Create Nothing Follows if needed
		if(last_indx < max_rows - 1){
			make_entry_terminal(store[last_indx + 1]);
		}
	}
}


//PDS Page 4
function load_references(){
    var row = 52
	const LAST_ROW = 54
	if(references.length == 0){
		$(`#T-C4 tr.R-${row} td.C-1`).html('N/A')
		$(`#T-C4 tr.R-${row} td.C-6`).html('N/A')
		$(`#T-C4 tr.R-${row} td.C-7`).html('N/A')
	}
	else{
		references.forEach(function(reference){
            reference = toUpperCaseEntries(replaceNullValues(reference))
			
			$(`#T-C4 tr.R-${row} td.C-1`).html(reference['references_name'])
			$(`#T-C4 tr.R-${row} td.C-6`).html(reference['references_address'])
			$(`#T-C4 tr.R-${row} td.C-7`).html(reference['references_telephone_number'])
			row++
		})
		if(row <= LAST_ROW){
			$(`#T-C4 tr.R-${row} td.C-1`).attr('colspan',9)
			$(`#T-C4 tr.R-${row} td.C-6`).remove()
			$(`#T-C4 tr.R-${row} td.C-7`).remove()
			$(`#T-C4 tr.R-${row} td.C-1`).html('Nothing follows')
		}
	}
}

function load_pwd_id(){
	if(!pwd_id){
		$(`#T-C4 tr.R-46 td.C-12`).html('N/A')
		$( "#is_pwd_yes").prop('checked', false);
		$( "#is_pwd_no").prop('checked', true);
	}
	else{			
		$(`#T-C4 tr.R-46 td.C-12`).html(pwd_id['id_number'])
		$( "#is_pwd_yes").prop('checked', true);
		$( "#is_pwd_no").prop('checked', false);
	}
}

function load_solo_parent_id(){
	if(!solo_parent_id){
		$(`#T-C4 tr.R-48 td.C-12`).html('N/A')
		$( "#is_solo_parent_yes").prop('checked', false);
		$( "#is_solo_parent_no").prop('checked', true);
	}
	else{			
		$(`#T-C4 tr.R-48 td.C-12`).html(solo_parent_id['id_number'])
		$( "#is_solo_parent_yes").prop('checked', true);
		$( "#is_solo_parent_no").prop('checked', false);
	}
}

function load_government_id(){
	if(primary_id.length == 0){
		$(`#T-C4 tr.R-61 td.C-4`).html('N/A')
		$(`#T-C4 tr.R-62 td.C-4`).html('N/A')
		$(`#T-C4 tr.R-64 td.C-4`).html('N/A')
	}
	else{
		primary_id = toUpperCaseEntries(primary_id)
				
		$(`#T-C4 tr.R-61 td.C-4`).html(primary_id['id_selected_type'])
		$(`#T-C4 tr.R-62 td.C-4`).html(primary_id['id_number'])
		$(`#T-C4 tr.R-64 td.C-4`).html(primary_id['id_date'] + '/' + primary_id['id_place'])		
	}
}

function load_hr_director(){
	
	if(hr_director){
		hr_director = toUpperCaseEntries(hr_director)
		let hr_director_name = hr_director['first_name'] + ' ' +		
			(hr_director['middle_name']=='' ? '' : hr_director['middle_name'][0] + '. ')  + 
			hr_director['last_name'] +
			(hr_director['custom_name_extension']=='' ? '' : ' ' + hr_director['custom_name_extension']) + 
			(hr_director_post_nominal_title['custom_preferred_post_nominal_titles']=='' ? '' : ', ' + hr_director_post_nominal_title['custom_preferred_post_nominal_titles'])	
		$(`#T-C4 tr.R-68 td.C-5`).html('<br>' + hr_director_name + '<br> Director, HRDO')		
	}
	else if(hr_oic){
		hr_oic = toUpperCaseEntries(hr_oic)
		let hr_oic_name = hr_oic['first_name'] + ' ' +		
			(hr_oic['middle_name']=='' ? '' : hr_oic['middle_name'][0] + '. ') +
			hr_oic['last_name'] +
			(hr_oic['custom_name_extension']=='' ? '' : ' ' + hr_oic['custom_name_extension']) + 
			(hr_oic_post_nominal_title['custom_preferred_post_nominal_titles']=='' ? '' : ', ' + hr_oic_post_nominal_title['custom_preferred_post_nominal_titles']) 	
		$(`#T-C4 tr.R-68 td.C-5`).html('<br>' + hr_oic_name + '<br> OIC, HRDO')	
		// console.log(hr_oic_post_nominal_title)
	}
	else{
		alert('No Person Administering Oath Set!')
		$(`#T-C4 tr.R-68 td.C-5`).html('<br>N/A')
	}
}

export function load_data(){
	//PDS Page 1
	load_umid_id();
	load_pagibig_id();
	load_philhealth_id();
	load_philsys_id();
	load_tin_id();
	load_spouse();
	load_father();
	load_mother();
	load_children();

	Object.keys(EDUCATION_LEVELS).forEach(level => {
		load_education(level);
	});

	//PDS Page 2
	load_civil_service_eligibilities();
	load_work_experiences();

	//PDS Page 3
	load_voluntary_works();
	load_trainings();
	load_skills_hobbies();
	load_non_academic_distinctions();
	load_memberships();

	//PDS Page 4
	load_references();
	load_pwd_id();
	load_solo_parent_id();
	load_government_id();
	load_hr_director();
}