(function() {
    "use strict";
    if (!$) {
        $ = document.querySelector.bind(document);
    }
    
    let modal = $(".tp-modal");
    modal.parentNode.removeChild(modal);

    let backdrop = $(".tp-backdrop.tp-active");
    backdrop.parentNode.removeChild(backdrop);

    document.body.style.setProperty("overflow", "visible", "important");

})();


