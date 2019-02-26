// Run this script on the ghost.io "subscribers" page to
// extract everyone's email address and display them in
// a prompt that allows you to copy them
(function() {
  'use strict';

  let list = $(".lt-body")[0];
  let emails = [];
  for (let x of list.children) {
      emails.push(x.children[0].textContent);
  }

  prompt("Copy the following (don't forget to BCC!):", emails); 
})();

