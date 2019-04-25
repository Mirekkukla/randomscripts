/**
 * Remove adblock detector popup for the daily beast / washington post
 */
(function() {
   "use strict";
   if (!$) {
       // code works even if '$' is jQuery
       $ = document.querySelector.bind(document);
   }

   function deleteElem(domElem) {
        domElem.parentNode.removeChild(domElem);
   }

   // the washington post
   // https://www.washingtonpost.com/outlook/2019/04/23/more-states-are-forcing-students-study-personal-finance-its-waste-time
   let wpModal = $(".modal-mask")[0];
   if (wpModal) {
       console.log("Removing Washing post adblock modal");
       deleteElem(wpModal);
   } else {
       console.log("Washington Post modal not detected");
   }

   // the daily beast
   let dbModal = $(".tp-modal")[0];
   let dbBackdrop = $(".tp-backdrop.tp-active")[0];
   if (dbModal && dbBackdrop) {
       console.log("Removing Daily Beast adblock modal");
       deleteElem(dbModal);
       deleteElem(dbBackdrop);
   } else {
       console.log("Daily Beast modals not detected");
   }

   // re-enable scrolling
   document.body.style.setProperty("overflow", "visible", "important");
   document.documentElement.style.setProperty("overflow", "visible", "important");

})();
