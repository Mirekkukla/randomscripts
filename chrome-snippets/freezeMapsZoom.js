// "Freeze" the current google maps zoom level
// if we detect (google maps) a url change with a newUrl
// new zoom level, re-load with the zoom level set to the
// "frozen" level.
//
// This will only happen once, since the reload call
// will re-initialize the window object (and with it our
// mutation observer / chrome console environment)


(function() {
  'use strict';

  // note that the zoom level can (but doesn't have to) be fractional
  const zoomRE = /(,[0-9]{1,2}\.?[0-9]{0,2})z/;

  let extractZoomLevel = function(url) {
    // return the zoom level, including the leading comma
    // EX) for url = https://www.google.com/maps/@-33.4331625,-70.6603761,15.78z
    // we'll return ',15.78z'
    if (!zoomRE.test(url)) {
      console.error("Failed to extract zoom level for url below");
      console.dir(url); // ".dir" ensure string doesn't get truncated
      return;
    }
    return url.match(zoomRE)[0];
  }

  let replaceZoomLevel = function(url, desiredZoomLevel) {
    // replace the zoom level in url with the given disired zoom level
    let existingZoomLevel = extractZoomLevel(url);
    return url.replace(existingZoomLevel, desiredZoomLevel);
  }

  let desiredZoomLevel = extractZoomLevel(document.location.href);
  console.log("Fixing desired zoom level at " + desiredZoomLevel);

  window.mutationObserver = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
          let currentUrl = document.location.href;
          let newZoomLevel = extractZoomLevel(currentUrl);
          if (newZoomLevel !== desiredZoomLevel) {
              console.log(`Zoom level changed to ${newZoomLevel}`);
              console.log(`Reverting to ${desiredZoomLevel}:`);

              let newUrl = replaceZoomLevel(currentUrl, desiredZoomLevel);
              
              // we need to truncate all the old "data" information
              // otherwise google maps will ignore the zoom level we
              // specified and redirect to a zoom level it deems better
              let fixedNewUrl = newUrl.split("/data")[0]

              console.dir(`Changing URL from ${currentUrl} to ${fixedNewUrl}`);
              location.assign(fixedNewUrl);
          }
      }); 
  });

  window.mutationObserver.observe(document.documentElement, {
    attributes: true,
    characterData: true,
    childList: true,
    subtree: true,
  });

  // to turn off observer call window.mutationObserver.disconnect()

})();
