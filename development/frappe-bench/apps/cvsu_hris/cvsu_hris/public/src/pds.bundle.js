import * as util from './pds/util';
import * as load_data from './pds/load_data';
import CellData from './pds/celldata';
import Alpine from 'alpinejs';
import $ from 'jquery';

//Counter use to determine when the pages are ready for autofitting
const waitset = Alpine.reactive([]);

const SHEETS = Object.freeze({
    PAGE_1 : $('#WS-C1'),
    PAGE_2 : $('#WS-C2'),
    PAGE_3 : $('#WS-C3'),
    PAGE_4 : $('#WS-C4'),
});

$(() => {
    window.Alpine = Alpine;
    //Bind columns to reactive data
    wire_table_data();
    Alpine.start();
})

document.addEventListener("alpine:initialized", () => {
    $('.show-notice').toggleClass('show-notice');
    
    load_data.load_data();

    //Once all data are loaded, span columns to multiple rows when needed and move overflowing contents to extra pages 
    Alpine.nextTick(() =>{
        redistribute_tables();
    })

    //Wait until waitset is empty before autofitting and showing the pages
    Alpine.watch(
        () => waitset, 
        (waitset) => !waitset.length && Alpine.nextTick(() => {  
            util.start_auto_fit(); 
            //Manually remove `x-cloak` because we only want to show the page after autofitting
            $('[x-cloak]').removeAttr('x-cloak');
        })
    )

});

function wire_table_data(){
    wire_children_data();
    wire_education_data();
    wire_eligibilities_data();
    wire_work_experiences();
    wire_voluntary_works();
    wire_trainings();
    wire_skills();
    wire_recognitions();
    wire_organizations();
}

function wire_children_data(){
    const start_row = 37, end_row = 48; 
    const col_filter = {name: 9, dob: 13};
    wire_columns_to_data(SHEETS.PAGE_1, start_row, end_row, col_filter, 'children');
}

function wire_education_data(){
    const start_row = 54, end_row = 58;
    const groups = ['elementary', 'secondary', 'vocational', 'college', 'graduate_studies'];
    const col_filter = {school: 4, degree: 7, period_from: 10, period_to: 11, units: 12, year_graduated: 13, honors: 14};
    

    let extra_education = {
        length: function() {
            return Object.values(this).reduce((l,v) => l + (Array.isArray(v)? v.slice(1).length : 0),0)
        }
    };

    groups.forEach((group,indx) => {
        let store_name = `${group}`;
        wire_columns_to_data(SHEETS.PAGE_1, start_row + indx, start_row + indx, col_filter, store_name);
        extra_education[group] = Alpine.store(store_name);
        //There is no need to wait for entries to be redistributed
        waitset.pop();
    });
    Alpine.store('extra_education', extra_education );
    
}

function wire_eligibilities_data(){
    const start_row = 5, end_row = 11;
    wire_columns_to_data(SHEETS.PAGE_2, start_row, end_row, null, 'eligibilities');
}

function wire_work_experiences(){
    const start_row = 18, end_row = 45;
    wire_columns_to_data(SHEETS.PAGE_2, start_row, end_row, null, 'work_experiences');
    
}

function wire_voluntary_works(){
    const start_row = 6, end_row = 12;
    wire_columns_to_data(SHEETS.PAGE_3, start_row, end_row, null, 'voluntary_works');
}

function wire_trainings(){
    const start_row = 18, end_row = 38;
    wire_columns_to_data(SHEETS.PAGE_3, start_row, end_row, null, 'trainings');
}

function wire_skills(){
    const start_row = 42, end_row = 48;
    const col_filter = {skill: 1};
    wire_columns_to_data(SHEETS.PAGE_3, start_row, end_row, col_filter, 'skills');
}

function wire_recognitions(){
    const start_row = 42, end_row = 48;
    const col_filter = {recognition: 3};
    wire_columns_to_data(SHEETS.PAGE_3, start_row, end_row, col_filter, 'recognitions');
}

function wire_organizations(){
    const start_row = 42, end_row = 48;
    const col_filter = {organization: 9};
    wire_columns_to_data(SHEETS.PAGE_3, start_row, end_row, col_filter, 'organizations');
}

function redistribute_tables() {
    redistribute_children();
    redistribute_eligibilities();
    redistribute_work_experiences();
    redistribute_voluntary_works();
    redistribute_trainings();
    redistribute_skills();
    redistribute_recognitions();
    redistribute_organizations();
}

function redistribute_children(){
    let children = Alpine.store('children');
    const start_row = 37, end_row = 48; 
    const col_filter = {name: 9, dob: 13};
    redistribute_sheet_rows(SHEETS.PAGE_1, start_row, end_row, col_filter, children);
}

function redistribute_eligibilities(){
    let eligibilities = Alpine.store('eligibilities');
    const start_row = 5, end_row = 11;
    redistribute_sheet_rows(SHEETS.PAGE_2, start_row, end_row, null, eligibilities);
}

function redistribute_work_experiences(){
    let work_experiences = Alpine.store('work_experiences');
    const start_row = 18, end_row = 45;
    redistribute_sheet_rows(SHEETS.PAGE_2, start_row, end_row, null, work_experiences);
}

function redistribute_voluntary_works(){
    let voluntary_works = Alpine.store('voluntary_works');
    const start_row = 6, end_row = 12;
    redistribute_sheet_rows(SHEETS.PAGE_3, start_row, end_row, null, voluntary_works);
}

function redistribute_trainings(){
    let trainings = Alpine.store('trainings');
    const start_row = 18, end_row = 38;
    redistribute_sheet_rows(SHEETS.PAGE_3, start_row, end_row, null, trainings);
}

function redistribute_skills(){
    let skills = Alpine.store('skills');
    const start_row = 42, end_row = 48;
    const col_filter = {skill: 1};
    redistribute_sheet_rows(SHEETS.PAGE_3, start_row, end_row, col_filter, skills);
}

function redistribute_recognitions(){
    let recognitions = Alpine.store('recognitions');
    const start_row = 42, end_row = 48;
    const col_filter = {recognition: 3};
    redistribute_sheet_rows(SHEETS.PAGE_3, start_row, end_row, col_filter, recognitions);
}

function redistribute_organizations(){
    let organizations = Alpine.store('organizations');
    const start_row = 42, end_row = 48;
    const col_filter = {organization: 9};
    redistribute_sheet_rows(SHEETS.PAGE_3, start_row, end_row, col_filter, organizations);
}

function redistribute_sheet_rows(sheet, start_row, end_row, col_filter, store){
    let rows = {};
    let ignored_row_columns = {};
    let col_selector;

    //Create class selectors that includes only the columns being considered in the redistribution
    if(col_filter){
        col_selector = (Object.values(col_filter).map((col_id) => `.C-${col_id}`)).join(',')
    }
    
    for(let r = start_row; r <= end_row; r++ ){
        //The row containing all considered columns
        let row = [];

        if (col_filter){  //Filter columns if column filters are set
            //Get all columns considered for the given row
            row = Object.values(col_filter).map((col_id)=> $(`.R-${r} .C-${col_id}`, sheet));
            
            //Find all columns of the row that are not considered 
            $(`.R-${r} td`, sheet).not(col_selector).each((i,td)=>{
                //Create an array to store the ignored columns
                if(!(r in ignored_row_columns)){
                    ignored_row_columns[r] = [];       
                }
                
                //Get the column
                let col = $(td)

                //Store the column to the set of ignored column, including its rowspan, for resetting later
                ignored_row_columns[r].push({
                    "column": col,
                    "rowspan": col.attr('rowspan')
                })

                //Ensure that ignored columns will not affect the size of columns being considered 
                col.addClass('nowrap-col');
                col.attr('rowspan',1);
            }) 

        }else{
            row = $(`.R-${r} td`, sheet).map((i,td) => $(td)).get();
        }

        //Add the constructed row
        rows[r] = row;
    }

    //Compute rowspans of rows that can fit on the available size
    const rowspans = util.get_rowspans(rows, end_row - start_row + 1);  

    //Reset the ignored columns
    Object.values(ignored_row_columns).forEach((row) => {
        row.forEach(meta => {
            let col = meta['column']
    
            col.removeClass('nowrap-col');

            //Reset the rowspan
            if(meta['rowspan']){
                col.attr('rowspan', meta['rowspan']);
            }
        })
    })

    //Update the rowspan starting from the end
    rowspans.reverse().forEach((rowspan, indx) => {
        //Get the row index
        let row_indx = rowspans.length - 1 - indx;

        //Get the column meta data
        let cols_data = store[row_indx].fields;

        /*
         * Add extra entries that represents the amount of additional rowspan needed by the current row
         * This should shift row data down
         */
        for(let r = 1; r < rowspan; r++){
            //Extra (padding) data to push elements down 
            store.splice(row_indx + 1,0, {
                is_terminator: false, 
                fields: cols_data.map(() => new CellData(1,1,true,'')) 
            })    
        }

        //Update the rowspans of each columns
        cols_data.forEach(col_data => col_data.rowspan = rowspan)
    })

    //The set of rows are ready for autofit, remove a counter from the waitset
    waitset.pop();
}

function wire_columns_to_data(sheet, start_row, end_row, col_filter, store_name){    
    //Create class selector if column filter is set
    if(col_filter){
        col_selector = (Object.values(col_filter).map((col_id) => `.C-${col_id}`)).join(',')
    }
  
    let entries = [];
    //Iterate over all rows based on the given range of rows
    for(let r = start_row, entry_indx =0 ; r <= end_row; r++, entry_indx++){
        //Select a row
        let row = $(`tr.R-${r}`, sheet);
        let cols;         
        //Select the columns
        if (col_filter){
            cols = $(`${col_selector}`,row)
        }else{
            cols = $('td',row)
        }
        
        //Data about each columns
        let cols_meta = []; 
        
        cols.each((col_indx,c) => {   
            let col = $(c);         
            cols_meta.push(new CellData(
                col.attr('colspan') ?? 1,
                col.attr('rowspan') ?? 1,
                false,
                ''
            ));          
            
            //Create the reactive data to be assigned to the column
            let binding = `_${btoa(`${store_name}${entry_indx}${col_indx}`).replaceAll("=","_")}_`;
            
            Alpine.bind(binding, {
                [':colspan'](){
                    return this[store_name][entry_indx].fields[col_indx].colspan
                },
                [':rowspan'](){
                    return this[store_name][entry_indx].fields[col_indx].rowspan
                },
                ['x-show'](){
                    return !this[store_name][entry_indx].fields[col_indx].merged
                },
                ['x-text'](){
                    return this[store_name][entry_indx].fields[col_indx].text
                },
            });

            //Assign the reactive data to each column
            col.attr('x-bind', `${binding}`)     
        })
        //Save the data of each column in the row
        entries.push({ is_terminal: true, fields: cols_meta });
    }

    //This newly wired rows is not yet ready for autosizing, add a counter to the waitset 
    waitset.push(store_name);

    Alpine.store(store_name, entries);
    
}