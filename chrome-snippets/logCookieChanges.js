(function() {
    "use strict";

    function getCookieMap(cookiesStr) {
        // return a map from "cookie name" -> "cookie value"
        let cookieList = cookiesStr.split(";").map((s) => s.trim()); 
        let cookieKeyValues = cookieList.map((s) => [s.split("=")[0], s.split("=")[1]]);
        return new Map(cookieKeyValues);
    }

    function logCookieChanges(lastCookies, currentCookies) {
        let lastCookiesMap = getCookieMap(lastCookies);
        let currentCookiesMap = getCookieMap(currentCookies);

        // check for new or changed cookies
        for (let [key, value] of currentCookiesMap) {
            if (!lastCookiesMap.has(key)) {
                console.log(`New cookie: ${key}=${value}`);
                continue;
            }

            let oldValue = lastCookiesMap.get(key);
            if (value !== oldValue) {
                console.log(`Value for cookie with key ${key} changed`);
                console.log(`Old value: '${oldValue}'`);
                console.log(`New value: '${value}'`);
            }
        }

        // check for deleted cookies
        for (let [lastKey, lastValue] of lastCookiesMap) {
            if (!currentCookiesMap.has(lastKey)) {
                console.log(`Cookie has been deleted: ${lastKey}=${lastValue}`);
            }
        }
    }

    let lastCookies = document.cookie; // initialize
    let checkCookies = function() {
        var currentCookies = document.cookie;
        if (currentCookies != lastCookies) {
            logCookieChanges(lastCookies, currentCookies);
            lastCookies = currentCookies;
        }
    };

    console.log("Starting to log cookie changes");
    console.log("Initial cookies:");
    console.log(lastCookies);
    window.setInterval(checkCookies, 100); // run every 100 ms

})();
