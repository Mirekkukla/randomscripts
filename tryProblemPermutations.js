function getPerm(size) {
  if (size == 0) {
    return [];
  }

  if (size == 1) {
    return [[0], [1]];
  }

  var result = [];

  var smaller = getPerm(size - 1);

  for (var i = 0; i < smaller.length; i++) {
    var onePerm = smaller[i];
    var onePermCopy = onePerm.slice(0);
    
    onePerm.push(1);
    onePermCopy.push(0);

    result.push(onePerm);
    result.push(onePermCopy);
  }

  return result;
}

function clickStuff(permutationArr) {
  for (var i = 0; i < 7; i++) {
    if (permutationArr[i] == 1) {
      $("#" + boxes[i]).click();
    }   
  }
}

var boxes = []
for (var i = 0; i < 7; i++) {
  boxes.push("input_i4x-Engineering-Networking-SP-problem-c32e8e8839bb4910bfb74ddea1a340ed_2_1_choice_" + i);
}

var permutations = getPerm(7);

function click(perm, i) {
  setTimeout(function() {
    console.log("about to click " + perm);
    clickStuff(perm);
  }, 4000*i);
}

function unclick(perm, i) {
  setTimeout(function() {
    var status = $("#status_i4x-Engineering-Networking-SP-problem-c32e8e8839bb4910bfb74ddea1a340ed_2_1").attr('class') 
    if (status == "status correct") {
      alert("BOOMSLAM it's " + perm);
      console.log("Its was " + perm);
    }
    console.log("about to unclick " + perm);
    clickStuff(perm);
  }, 3500 + 4000*i);
}

function submit(i) {
  setTimeout(function() {
    $("button.Submit")[4].click();
  }, 500 + 4000*i);
}

for (var i = 0; i < 1; i++) {
  var perm = permutations[i];
  click(perm, i);
  submit(i);
  unclick(perm, i);
}
