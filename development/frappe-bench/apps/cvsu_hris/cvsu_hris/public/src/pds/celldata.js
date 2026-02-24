export default class CellData{
    constructor(colspan, rowspan, merged, text){
        this.colspan = colspan;
        this.rowspan = rowspan;
        this.merged = merged;
        this.text = text;
    }
}