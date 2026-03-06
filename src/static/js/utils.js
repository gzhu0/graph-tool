// Utility Functions

export function insertInOrder(list, x) { 
    // Inserts in order into a list
    for (let i = 0; i < list.length; i++) {
        if (x < list[i]) {
            list.splice(i,0,x);
            return;
        }
        break;
    }
    list.push(x);
}

