// Script to download the png images that constitue the "pdfs" hosted on secondmarket.com
// EX) https://addepar.secondmarket.com/auth/sign_in
//
// 1. Uncomment the `docInfo` var below next to the document you wish to download.
// 2. Copy and past the script contents into the chrome console in a page where you're logged in.
// 3. Click enter to confirm the download of all the resulting png files.

// Document IDs are found using the chrome inspector to inspect a page in the document you care about
// EX: <img alt="" src="/document_view/45136/view?file=45136_1.png" ...
//     Here the document ID is "45136"

// 1) Addepar - 701 Disclosure Statement - 2011 Plan
// var docInfo = {id: 45136, numberOfPages: 1}

// 2) Exhibit A - Questions and Answers About the Addepar, Inc. 2011 Stock Plan Final
// var docInfo = {id: 95891, numberOfPages: 9}

// 3) Exhibit B - Risk Factors
// var docInfo = {id: 45079, numberOfPages: 24}

// 4) Exhibit C - Explanation of Federal Income Tax Consequences and Section 83(b) Election
// var docInfo = {id: 43693, numberOfPages: 7}

// 5a) Exhibit D - Financial Statements
// var docInfo = {id: 44030, numberOfPages: 1}

// 5b) Report of Independent Auditors and Financial Statements December 2016 and 2017
// var docInfo = {id: 95836, numberOfPages: 41}

// 5c) Financial Data for the Three Months Ended March 31, 2016 (Unaudited)
// var docInfo = {id: 50193, numberOfPages: 6}

// 5d) Financial Data for the Three and Six Months Ended June 30, 2016 (Unaudited)
// var docInfo = {id: 50194, numberOfPages: 6}

// 5e) Financial Data for the Three and Nine Months Ended September 30, 2016 (Unaudited)
// var docInfo = {id: 50196, numberOfPages: 6}

// 5f) Financial Data for the Three Months Ended March 31, 2017 (Unaudited)
//var docInfo = {id: 62886, numberOfPages: 6}

// 5g) Financial Data for the Three and Six Month Ended June 30, 2017 (Unaudited)
// var docInfo = {id: 70496, numberOfPages: 6} 

// 5h) Financial Data as of and for the Three and Nine Months ended September 30, 2017 (Unaudited)
var docInfo = {id: 81822, numberOfPages: 6} 

var tempLink = document.createElement("a");
for (var i = 1; i <= docInfo.numberOfPages; i++) {
    var url = "https://addepar.secondmarket.com/document_view/" + docInfo.id + "/view?file=" + docInfo.id + "_" + i + ".png";
    tempLink.setAttribute('href', url);
    tempLink.setAttribute('download', ''); // download the image instead of just loading it in the browser
    // each download needs to happen in its own tab, otherwise only the most recently request one will go through
    tempLink.setAttribute('target', '_blank');
    console.log("about to download file from " + fileInfo.url);
    tempLink.click();
}