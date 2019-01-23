var NAME = "Bobdole";
var EMAIL = "BobDole123@gmail.com";

/**
 * Populate all input boxes that look name-related with a fake name, and similarly
 * with a fake email address. Check checkboxes indicate the acceptance of terms.
 * 
 * We consider an input box "name-related" if it has an attribute value
 * containing the case-insensitive substring "name" (and likewise with "email").
 */
$("input").each(function(i, node) {

    for (var attrName of node.getAttributeNames()) {
        var attrVal = node.getAttribute(attrName);

        if (node.type === "checkbox" && /accept/i.test(attrVal)) {
            console.log("Checkbox match on attr=" + attrName + " value=" + attrVal); 
            node.checked = true;
            console.log(node);
            return;
        }

        if (/name/i.test(attrVal)) {
            console.log("Name match on attr=" + attrName + " value=" + attrVal);
            node.value = NAME;
            console.log(node);
            return;
        }

        if (/mail/i.test(attrVal)) {
            console.log("Email match on attr=" + attrName + " value=" + attrVal);
            node.value = EMAIL;
            console.log(node);
            return;
        }
    }
});
