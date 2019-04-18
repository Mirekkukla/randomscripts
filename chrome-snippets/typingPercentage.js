/**
 * Log the % of letters you got right on a typing study drill
 * e.g. https://www.typingstudy.com/lesson/3/extra_key_drill
 */
(function() {
    "use strict";
    let totalCorrect = 0;
    let total = 0;

    for (let listItem of $(".graph").children) {
        for (let cellDiv of listItem.children) {
            if (cellDiv.className != "result") {
                continue;
            }
            let fractionStr = cellDiv.innerText;
            let fractionArr = fractionStr.split("/");

            totalCorrect += parseInt(fractionArr[0]);
            total += parseInt(fractionArr[1]);
        }
    }

    let percent = totalCorrect * 100.0 / total;
    console.log(`Total: ${totalCorrect}/${total} = ${percent}%`);
})();
