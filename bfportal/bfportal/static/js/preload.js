function defer(method) {
    "use strict";
    if (window.jQuery) {
        method();
        console.log(`loaded ${method.name}`)
    } else {
        setTimeout(function() { defer(method) }, 50);
    }
}
