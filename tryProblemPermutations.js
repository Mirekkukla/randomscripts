/* 
* Script to try every permutation of a answers to a quiz for self-study CS144 course (problem 2-2A)
* See https://lagunita.stanford.edu/courses/Engineering/Networking-SP/SelfPaced/courseware
* 
* Run this script in chrome developer console.
*/


// HELPER FUNCTIONS

/*
* Retruns an array of all pessible permutations of binary arrays of length "size"
* For instance, for size = 2, returns [[0,0],[0,1],[1,0],[1,1]]
*/
function getPermutations(size) {
  if (size == 1) {
    return [[0], [1]];
  }

  var result = [];
  var permsOfSizeMinusOne = getPermutations(size - 1);

  for (var i = 0; i < permsOfSizeMinusOne.length; i++) {
    var permutation = permsOfSizeMinusOne[i];
    var permutationCopy = permutation.slice(0);
    
    permutation.push(1);
    permutationCopy.push(0);

    result.push(permutation);
    result.push(permutationCopy);
  }

  return result;
}

/* Click all check checkboxes corresponding to 1's in the given 'permutation' (an array of 1's and 0's) */
function clickStuff(permutation) {
  for (var i = 0; i < permutation.length; i++) {
    if (permutation[i] == 1) {
      $("#" + checkboxes[i]).click();
    }   
  }
}

/* Click all checkboxes corresponding to the given 'permutation' after 4000*i milliseconds */
function click(permutation, i) {
  setTimeout(function() {
    console.log("about to click " + permutation);
    clickStuff(permutation);
  }, 4000*i);
}

/*
* After 3500 + 4000*i milliseconds, check if the previous click was the right answer. If not,
* un-check all checkboxes corresponding to the given 'permutation'
*/
function unclick(permutation, i) {
  setTimeout(function() {
    var status = $("#status_i4x-Engineering-Networking-SP-problem-c32e8e8839bb4910bfb74ddea1a340ed_2_1").attr('class') 
    if (status == "status correct") {
      alert("BOOMSLAM it's " + permutation);
      console.log("Its was " + permutation);
    }
    console.log("about to unclick " + permutation);
    clickStuff(permutation);
  }, 3500 + 4000*i);
}

/* After 500 + 4000*i) seconds, click the "Submit" button to submit the answer */
function submit(i) {
  setTimeout(function() {
    $("button.Submit")[4].click();
  }, 500 + 4000*i);
}


// SCRIPT CONTENTS

var checkboxes = []
for (var i = 0; i < 7; i++) {
  checkboxes.push("input_i4x-Engineering-Networking-SP-problem-c32e8e8839bb4910bfb74ddea1a340ed_2_1_choice_" + i);
}

var permutations = getPermutations(7);


for (var i = 0; i < 128; i++) {
  var perm = permutations[i];
  click(perm, i);
  submit(i);
  unclick(perm, i);
}
