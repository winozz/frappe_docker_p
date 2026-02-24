export default class Heap{
    constructor(data, is_min_heap = true){
        this.h = data.slice().sort((e1, e2) => is_min_heap ? e1.r - e2.r : e2.r - e1.r)
    }
    get(){
        return this.h[0];
    }
    remove(){
        return this.h.shift();
    }
    is_empty(){
        return this.h.length == 0;
    }
}