/**
 * Populate all input boxes that look name-related with a fake name, and similarly
 * with a fake email address.
 * 
 * We consider an input box "name-related" if it has an attribute value
 * containing the case-insensitive substring "name" (and likewise with "email").
 */

var NAME = "Bobdole";
var EMAIL = "BobDole123@gmail.com";

$("input").each(function(i, node) {
    var attNames = node.getAttributeNames();
    for (var j = 0; j < attNames.length; j++) {
 
        var attrName = attNames[j];
        var attrVal = node.getAttribute(attrName);

        var nameRegex = /[Nn][Aa][Mm][Ee]/
        if (nameRegex.test(attrVal)) {
            console.log("Name match on attr=" + attrName + " value=" + attrVal);
            node.value = NAME;
            console.log(node);
            return;
        }

        var emailRegex = /[Ee][Mm][Aa][Ii][Ll]/;
        if (emailRegex.test(attrVal)) {
            console.log("Name match on attr=" + attrName + " value=" + attrVal);
            node.value = EMAIL;
            console.log(node);
            return;
        }
    }
});
