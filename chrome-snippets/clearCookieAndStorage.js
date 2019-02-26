(function() {
    "use strict";

    let count = document.cookie.split("=").length - 1
    console.log(`Initially ${count} cookies: '${document.cookie}'`)
    for (let raw_cookie of document.cookie.split(";")) {
        let cookie = raw_cookie.trim();

        let name = cookie.split("=")[0]
        let oldDateStr = new Date(0).toGMTString();

        let domainWithDot = "." + document.domain;
        let cookieDeletor = `${name}=; expires=${oldDateStr}; path=/; domain=${domainWithDot}`;
        console.log(`Using deletor '${cookieDeletor}'`);
        document.cookie = cookieDeletor;
    }

    count = document.cookie.split("=").length - 1
    console.log(`Finally ${count} cookies: '${document.cookie}'`)

    console.log("Local storage prior to clear:");
    console.dir(localStorage);
    localStorage.clear();
})();
