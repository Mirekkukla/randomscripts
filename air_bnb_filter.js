// parentnode vs parentelement?

// https://www.airbnb.com/s/Prague--Czech-Republic/homes?refinement_paths%5B%5D=%2Fhomes&checkin=2018-11-30&checkout=2018-12-04&adults=2&price_min=23&price_max=52&query=Prague%2C%20Czech%20Republic&place_id=ChIJi3lwCZyTC0cRkEAWZg-vAAQ&allow_override%5B%5D=&s_tag=duuZACVT

// include jqury
var script = document.createElement('script');
script.src = "https://ajax.googleapis.com/ajax/libs/jquery/2.2.0/jquery.min.js";
document.getElementsByTagName('head')[0].appendChild(script);


//$$("._i655ore")[2].parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode
function getOuterDiv(totalAmountNode) {
    var node = totalAmountNode;
    while (node.parentNode.className !== "_fhph4u") { // This hasn't been changing... yet
        node = node.parentNode;
        console.log(node);
        if (node === null) {
            console.log("Couldn't find parent for");
            console.log(totalAmountNode);
            return null;
        }
    }

    return node;
}

var maxTotalAllowed = 180;

// Searching for the intersection fo "$" and "total"  returns two kinds of containers:
// - those with the total (where text is e.g. '$208total')
// - the parent container with the nightly price (e.g. 'Price$42/night$208total')
// We want to make sure we only get the former
var candidateLeafNodes = $("span:contains($):contains(total):not(:contains(Price))");

candidateLeafNodes.each(function(i, candidateLeaf) {
    if (candidateLeaf.children.length === 0) {
        return;
    }

    // Should no longer need but lets be safe
    var text = candidateLeaf.textContent;
    if (!text.includes("$")) {
        return;
    }

    // The leaf string used to be e.g. "$251total" or "Price$265" - for some reason it changes??
    var inner_digits_re = /[^0-9$]*\$([0-9]+)[^0-9]*/;
    var re_result = text.match(inner_digits_re);
    if (re_result === null || re_result.length !== 2) {
        console.log("Something went wrong with regex, searched '" + text + "', got " + re_result);
        return;
    }
    var amountStr = re_result[1];

    // todo: str to int compariosn??
    if (amountStr > maxTotalAllowed) {
        console.log("i is " + i + " amountStr "  + amountStr);

        console.dir(candidateLeaf);
        var outerDivNode = getOuterDiv(candidateLeaf);
        if (outerDivNode === null) {
            console.log("Didn't find outer div, quitting");
            return;
        }

        console.log("About to remove:");
        console.log(outerDivNode); // console.dir shows it as a javascript object (if you want to see all properties etc)
        console.log("Amount is " + amountStr);
        // $(outerDivNode).find("*").hide();
        // $(outerDivNode).hide();

        $(outerDivNode).attr("style", "display: none !important");
        $(outerDivNode).find("*").attr("style", "display: none !important");
    }
});

