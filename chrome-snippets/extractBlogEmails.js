{
'use strict'

let list = $(".lt-body")[0];
let emails = []
for (let x of list.children) {
    emails.push(x.children[0].textContent)
}
prompt("Copy the following:", emails)
 
}

