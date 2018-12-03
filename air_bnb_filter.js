// https://www.airbnb.com/s/Prague--Czech-Republic/homes?refinement_paths%5B%5D=%2Fhomes&checkin=2018-11-30&checkout=2018-12-04&adults=2&price_min=23&price_max=52&query=Prague%2C%20Czech%20Republic&place_id=ChIJi3lwCZyTC0cRkEAWZg-vAAQ&allow_override%5B%5D=&s_tag=duuZACVT

// include jqury
var script = document.createElement('script');
script.src = "https://ajax.googleapis.com/ajax/libs/jquery/2.2.0/jquery.min.js";
document.getElementsByTagName('head')[0].appendChild(script);

// TODO: wait for it to load

// POSSIBLE TODO: extract the class name instead of hard-coding it
// For now, relying on the hard-coded class name might be less fragile than trying to exract it
var OUTER_DIV_CLASS_NAME = "_fhph4u";

// TODO: ask use in popup
var maxTotalAllowed = 80;

////////////// BULK OF SCRIPT ////////////////////

function main() {
    // see if hardcoded outer div still exists / has the right number of children
    if (!checkOutDivClassName()) {
        console.error("Hard-coded div no longer exists, quitting");
        return;
    }

    // This gets us not just the leaf nodes, but all of their parent nodes. We'll need to filter them out.
    // This is a little tricky since AirBnb seems to have to version of the site.
    // - In one, the 'total' string gets its own container
    // - In another, the total amount gets its own container, and sits next to an invisible "price" container
    // This results in a different text rendering, e.g. "$215total" vs "Price$215 total"
    var candidateLeafNodes = $("span:contains($):contains(total)");
    var leafNodes = candidateLeafNodes.filter(function(i, node) {

        // all intermediate elements have more than one child
        if (node.childElementCount != 1) {
            return false;
        }

        // the following is just a sanity check to make sure text formatting looks as expected
        var text = node.textContent;
        var leafTextRe = /^Price\$[0-9]+\ total$|^\$[0-9]+total$/
        var reResult = text.match(leafTextRe);
        if (reResult === null || reResult.length !== 1) {
            console.warn("Something went wrong with regex, searched '" + text + "', got " + reResult);
            console.warn("Something like '$215total' or 'Price$215 total'");
        }

        return true;
    });

    var numListingsInSummary = getNumberOfListings();
    if (numListingsInSummary !== leafNodes.length) {
        console.warn("Number of leaf nodes (%s) doesn't match listings in summary (%s)",
            leafNodes.length, numListingsInSummary);
    }

    leafNodes.each(function(i, leafNode) {

        // As explained above, leaf string can be either e.g. "$215total" or "Price$215 total"
        var text = leafNode.textContent;
        var innerDigitsRe = /[^0-9$]*\$([0-9]+)[^0-9]*/;
        var reResult = text.match(innerDigitsRe);
        if (reResult === null || reResult.length !== 2) {
            console.error("Something went wrong with regex, searched '" + text + "', got " + reResult);
            return;
        }

        var listingTotal = parseInt(reResult[1], 10);
        if (listingTotal > maxTotalAllowed) {
            var outerDivNode = getOuterDiv(leafNode);
            if (outerDivNode === null) {
                console.warn("Didn't find outer div, skipping %o", leafNode);
                return;
            }

            console.log("About to hide %o", outerDivNode);
            console.log("Amount is " + listingTotal);

            // WONT WORK due to !important
            // $(outerDivNode).find("*").hide();
            // $(outerDivNode).hide();

            // $(outerDivNode).attr("style", "display: none !important");
            // $(outerDivNode).find("*").attr("style", "display: none !important");
        }
    });
}


////////////// HLEPERS ////////////////////

/** Get the number of listings currently displayed on the page (or null on error) */
function getNumberOfListings() {
    var listingSummaryNode = $("nav + div:contains(' Rentals')")
    if (listingSummaryNode.length !== 1) {
        console.warn("Expected a single 'listing summary' node:");
        console.warn(listingSummaryNode);
        return null;
    }

    // e.g. "1 – 18 of 237 Rentals" or "1 – 18 of 300+ Rentals"
    var listingSummary = listingSummaryNode[0].textContent;
    // '.'' for the dash character (it's in a fancy format that doesn't match a plaintext '-')
    var listingSummaryRe = /[0-9]+\ .\ ([0-9]+)\ of\ [0-9]+\+?\ Rentals/;
    var listingSummaryMatch = listingSummary.match(listingSummaryRe);
    if (listingSummaryMatch === null || listingSummaryMatch.length !== 2) {
        console.warn("Something went wrong with regex '%s'", listingSummaryRe);
        console.warn("Expected something like '1 – 18 of 237 Rentals', saw '%s'. Match result:", listingSummary);
        console.warn(listingSummaryMatch);
        return null;
    }

    var numListingsStr = listingSummaryMatch[1];
    return parseInt(numListingsStr, 10); // specify base in case theres a leading 0 (treated as octal)
}


/**
  * Sanity check our hard-coded outer div class name. Return true if outer class name still exists
  * Run a sanity check on the number of listings, printing warnings along the way
  */
function checkOutDivClassName() {
    var outerDivNode = $('div.' + OUTER_DIV_CLASS_NAME);
    if (outerDivNode.length !== 1) {
        console.error("Didn't find a div with class name " + OUTER_DIV_CLASS_NAME);
        return false;
    }

    var numOfListingsInDiv = outerDivNode.children().length;
    var numListingsInSummary = getNumberOfListings();
    if (numListingsInSummary !== numOfListingsInDiv) {
        console.warn("Number of listings in div ('%s') != number of listings in summary ('%s')",
            numOfListingsInDiv, numListingsInSummary);
    }

    return true;
}


/** 
  * Return the node that:
  * - contains the given 'total amount' node, and
  * - is a direct child of 'the outer div node'
  * Return null if no such node is found
  */
function getOuterDiv(totalAmountNode) {
    var node = totalAmountNode;
    while (node.parentNode.className !== OUTER_DIV_CLASS_NAME) {
        node = node.parentNode;
        if (node === null) {
            console.error("Couldn't find parent for");
            console.error(totalAmountNode);
            return null;
        }
    }
    return node;
}

main();