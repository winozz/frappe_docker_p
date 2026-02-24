import Heap from './heap';
import $ from 'jquery';

const MQL = window.matchMedia("print");

MQL.onchange = (e) => {
    auto_fit();
};

export function start_auto_fit(){   
    auto_fit();
}

function auto_fit(){
    $('.worksheet').each(function(){
        let page = $(this)
        let content = $('.content',page);
        let page_width = page.width(), page_height = page.height();
        let content_width = content.width(), content_height = content.height();
        let scaleX = page_width/content_width, scaleY = page_height/content_height;
        let auto_width = page.data('fit-width') ?? false , auto_height = page.data('fit-height') ?? false;

        if(auto_width && auto_height){
            content.css({ 'transform': `scale(${scaleX},${scaleY})` });
        }else if(auto_width){
            content.css({ 'transform': `scaleX(${scaleX})` });
        }else if(auto_height){
            content.css({ 'transform': `scaleY(${scaleY})` });
        }
    });
    reduce_font_size();
}

export function get_rowspans(rows, max_available_rows){
    let rowspans = compute_rowspans(rows);
    let rowspan_count = rowspans.reduce((s,v) => s + v , 0);

    // console.log(rowspans, excess_rowspans)
    
    while(rowspan_count > max_available_rows){
        //Current last row (also the number of rows left if the current last row is removed)
        let pos = rowspans.length - 1;

        //Number of rowspans after removing the rowspan of the last row
        let next_rowspan_count = rowspan_count - rowspans[pos];

        //If removing the last row will result to deficient number of rows
        if(next_rowspan_count < max_available_rows){
            //Count number of rowspans that are greater than 1
            let multispanning_count = rowspans.reduce((c,v) => v > 1 ? c + 1 : c, 0);

            /* 
             * Compute the number of rowspans to add to remaining rows except the last row 
             * to fill-up the deficiency:    
             *
             * Number of deficient rows divided by remaining rows
             */ 
            let rowspan_inc = Math.ceil((max_available_rows - next_rowspan_count)/pos);
            
            /*
             * Compute the number of rowspans to remove from rows inlcuding the last row 
             * whose rowspan is greater than 1 to fit all remaining rows:
             * 
             * Number of excess rows divided by the number of rows that can be reduced 
             */
            let rowspan_dec = Math.ceil((rowspan_count - max_available_rows) / multispanning_count);
            
            let delta_rowspan; //Increase or decrease to rowspan 
            
            /*
            * The heap use for selecting which rowspan will be updated first.
            * The heap elements is a pair (r,i) that represents rowspans[i] = r    
            */ 
            let heap;

            //Determine which of the two changes will have less overall impact
            if(rowspan_inc <= rowspan_dec) { 
                /*
                 * Create a min heap with rowspan as priority.
                 * This heap will guarantee that elements with smaller rowspan will be incremented first.
                 */
                heap = new Heap(rowspans.map((rowspan,indx) => ({r: rowspan, i: indx})), true);

                delta_rowspan = rowspan_inc;                
                //Remove last row and
                rowspan_count = next_rowspan_count;
                rowspans.pop(); 

            }else{
                /*
                 * Create a max heap with rowspan as priority, not including those with rowspan 1.
                 * This heap will guarantee that elements with larger rowspan will be decremented first.
                 */
                heap = new Heap(rowspans.filter((v)=> v > 1).map((rowspan,indx) => ({r: rowspan, i: indx})), false);
                delta_rowspan =  -rowspan_dec;            
            }

            // console.log(rowspan_inc, rowspan_dec, delta_rowspan);
            
            //Iterate over all rows until the total rowspan matches expected max rows 
            while( rowspan_count != max_available_rows && !heap.is_empty()){
                // console.log(rowspan_count, max_rows);

                //Ensure that the change in rowspan is never more than the necessary change                
                if  (Math.abs(max_available_rows - rowspan_count) < Math.abs(delta_rowspan)){
                    delta_rowspan = max_available_rows - rowspan_count;
                }
                
                /*
                 * Apply change to any row if the change will increase the rowspan
                 * Otherwise, only decrease if it will not result to 0 
                 */ 
                let indx = heap.remove().i;
                rowspans[indx] =  rowspans[indx] + delta_rowspan;
                rowspan_count += delta_rowspan;
            }
            break;
        }else{
            //Remove last row
            rowspans.pop();
        }
        //Update the current total rowspan
        rowspan_count = next_rowspan_count;
    }
    // console.log(rowspans, excess_rowspans)
    return rowspans
}

function compute_rowspans(rows){
    let rowspans = [];
    Object.entries(rows).forEach(function([row_id, row],index){
        if(!Array.isArray(row))
            return;

        //Get the contents of each column of the current row 
        var col_contents = row.map((col) => col.text());
        
        //Get the current height of each column of the current row 
        var col_original_heights = row.map((col) => col.height());
        
        //Get the max height among all column heights 
        var max_original_heights = col_original_heights.reduce((mh,h) => h > mh ? h : mh, 0);
        
        //Clear the content of all columns
        row.forEach((col) => col.text(''));
        
        //Get the height of the empty columns 
        var col_empty_heights = row.map((col) => col.height());    
        
        //Get the max height among the empty columns
        var max_col_empty_heights = col_empty_heights.reduce((mh,h) => h > mh ? h : mh, 0);
        
        //Compute the rowspan by computing the growth factorof an empty column  
        var rspan = Math.floor(max_original_heights / max_col_empty_heights);

        //Restore the contents
        col_contents.forEach((content,idx) => row[idx].text(content));

        //Save the rowspan for the row
        rowspans[index] = rspan;        
    })
    
    return rowspans;
}

function reduce_font_size(){
    //Find all tags with bindings
    $("[x-bind]").each(function(){
        let source = $(this), copy = $("#pseudo-content");
        copy.text(source.text());
        copy.css('font', source.css('font'));
        copy.css('min-width',source.width());
    
        let font_size = Math.floor(parseFloat(source.css('font-size')));
        let content_width = copy.innerWidth();
        let container_width = source.outerWidth();
        let resize_factor = content_width/container_width;

        if (resize_factor > 1 && resize_factor < 2 && /^\S*$/.test(source.text())){
            font_size = Math.floor(font_size * Math.min(1, resize_factor))
            font_size = Math.max(2, font_size > 1 ? font_size - 1: font_size);
            source.attr('style', `font-size: ${font_size}px !important;`);
        }
    });
}


// $("#pseudo-content").remove();