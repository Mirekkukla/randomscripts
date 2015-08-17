/* 
* Script to try every permutation of a answers to a quiz for self-study CS144 course (problem 2-2A)
* See https://lagunita.stanford.edu/courses/Engineering/Networking-SP/SelfPaced/courseware
* 
* Run this script in chrome developer console.
*/


// HELPER FUNCTIONS

/*
* Return an array of all pessible permutations of binary arrays of length "size"
* For instance, for size = 2, returns [[0,0],[0,1],[1,0],[1,1]]
*/
function getPermutations(size) {
  if (size == 1) {
    return [[1], [0]];
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
function clickBoxes(permutation) {
  console.log("Clicking " + permutation)
  for (var i = 0; i < permutation.length; i++) {
    if (permutation[i] == 1) {
      $("#input_i4x-Engineering-Networking-SP-problem-c32e8e8839bb4910bfb74ddea1a340ed_2_1_choice_" + i).click();
    }   
  }
}

/* Look at the answer object to see if the last answer (assumed to be 'permutation') was correct, alert if so */
function checkAnswer(permutation) {
  console.log("Checking answer")
  var statusObj = $("#status_i4x-Engineering-Networking-SP-problem-c32e8e8839bb4910bfb74ddea1a340ed_2_1")
  if (statusObj.attr('class')  == "status correct") {
    alert("BOOMSLAM it's " + permutation);
    console.log("It was " + permutation);
  }
}

/* Click the "submit" button */
var submitFn = function() {
  $("button.Submit")[4].click();
};


// SCRIPT CONTENTS

var permutations = getPermutations(7);

// Go through each permutation, click the corresponding boxes, submit the answer,
// and wait to see if it was correct. Make sure to wait a while for the server to respond
for (var i = 0; i < permutations.length; i++) {
  var permutation = permutations[i];
  
  var clickFn = (function(perm) {
    return function() {
      clickBoxes(perm);
    }
  })(permutation);

  var checkAnswerFn = (function(perm) {
    return function() {
      checkAnswer(perm);
    }
  })(permutation);

  var WAIT_TIME = 2000;
  setTimeout(clickFn, WAIT_TIME * i);
  setTimeout(submitFn, WAIT_TIME * i + WAIT_TIME / 10);
  setTimeout(checkAnswerFn, WAIT_TIME * i + WAIT_TIME * (8 / 10));
  setTimeout(clickFn, WAIT_TIME * i + WAIT_TIME * (9 / 10));
}
