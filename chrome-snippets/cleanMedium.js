// Medium pages use a TON of screen real estate for
// the header and footer. Hide this for easier reading
(function() {
    "use strict";

    console.log("Hiding header");
    document.querySelector(".js-metabar").style.display = "none";

    console.log("Hiding footer");
    document.querySelector(".js-stickyFooter").style.display = "none";
})();
