// parentnode vs parentelement?

// https://www.airbnb.com/s/Prague--Czech-Republic/homes?refinement_paths%5B%5D=%2Fhomes&checkin=2018-11-30&checkout=2018-12-04&adults=2&price_min=23&price_max=52&query=Prague%2C%20Czech%20Republic&place_id=ChIJi3lwCZyTC0cRkEAWZg-vAAQ&allow_override%5B%5D=&s_tag=duuZACVT

//$$("._i655ore")[2].parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode
function getOuterDiv(totalAmountNode) {
    var node = totalAmountNode;
    while (node.parentNode.className != "_fhph4u") {
        node = node.parentNode;
        if (node == null) {
            console.log("Couldn't find parent for");
            console.log(totalAmountNode);
            return null;
        }
    }

    return node;
}


var maxTotalAllowed = 180;

var candidateLeafNodes = $$("._i655ore");
for (var i = 0; i < candidateLeafNodes.length; i++) {
    var candidateLeaf = candidateLeafNodes[i];
    if (candidateLeaf.children.length === 0) {
        continue;
    }

    var text = candidateLeaf.textContent;
    if (text[0] !== "$") {
        continue;
    }

    // at this point the string is e.g. "$251total"
    var amountStr = candidateLeaf.textContent.split('t')[0];
    var amountInt = amountStr.slice(1, amountStr.length);

    if (amountInt > maxTotalAllowed) {
        console.log("i is " + i + " amountStr "  + amountStr);
        var totalAmountNode = candidateLeafNodes[i];

        var outerDivNode = getOuterDiv(totalAmountNode);
        if (outerDivNode == null) {
            console.log("Didn't find outer div, quitting");
            break;
        }

        console.log("About to remove:");
        console.log(outerDivNode); // console.dir shows it as a javascript object (if you want to see all properties etc)
        console.log("Amount is " + amountInt);
        outerDivNode.remove();
    }
}

