
// for detecting when the daily beast detects our adblocker\
/* global MutationObserver */
(function() {
    "use strict";
    console.log("Monitoring DOM changes to detect adblock detection");

    // MUTATION OBSERVER

    let observerConfig = {
      childList : true,
      subtree: true
    };

    let mutationObserver = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            for (let child of mutation.addedNodes) {
                let cName = child.className;
                if (isSuspectClass(cName)) {
                    console.log("Removing " + cName);
                    console.log(child);
                    removeNode(child);
                }
            }
        }); 
    });

    mutationObserver.observe(document.querySelector("body"), observerConfig );


    // HELPERS

    function isSuspectClass(cName) {
        return cName && (cName.includes("tp-backdrop") || cName.includes("tp-modal"));
    }

    function removeNode(node) {
        node.parentNode.removeChild(node);
    }
})();

