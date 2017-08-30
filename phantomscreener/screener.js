var system = require('system');
var webserver = require('webserver');
var server = webserver.create();
console.log('starting');

function parseGET(url) {
    // adapted from http://stackoverflow.com/a/8486188
    var query = url.substr(url.indexOf("?") + 1);
    var result = {};
    query.split("&").forEach(function(part) {
        var e = part.indexOf("=")
        var key = part.substr(0, e);
        var value = part.substr(e + 1);
        result[key] = decodeURIComponent(value);
    });
    return result;
}





var service = server.listen(8000, function(request, response) {
    var page = require('webpage').create();
    page.viewportSize = {
        width: 800,
        height: 720
    };
    var requestsArray = [];
    page.onResourceRequested = function(requestData, networkRequest) {
        requestsArray.push(requestData.id);
    };

    page.onResourceReceived = function(response) {
        var index = requestsArray.indexOf(response.id);
        requestsArray.splice(index, 1);
    };
    response.statusCode = 200;
    console.log('got request');
    urlParams = parseGET(request.url);
    pic = ''
    url = decodeURIComponent(urlParams['url'])
        /*
	page.open(url, function (status) {
    var interval = setInterval(function() {
      if (requestsArray.length === 0) {
        clearInterval(interval);
        pic = page.renderBase64();
        response.write(pic);
        response.close();
      }
    });
  }); */
    var resourceWait = 300,
        maxRenderWait = 10000;

    var page = require('webpage').create(),
        count = 0,
        forcedRenderTimeout,
        renderTimeout;

    page.viewportSize = { width: 1280, height: 1024 };

    function doRender() {
        pic = page.renderBase64();
        response.write(pic);
        response.close();

    }

    page.onResourceRequested = function(req) {
        count += 1;
        console.log('> ' + req.id + ' - ' + req.url);
        clearTimeout(renderTimeout);
    };

    page.onResourceReceived = function(res) {
        if (!res.stage || res.stage === 'end') {
            count -= 1;
            console.log(res.id + ' ' + res.status + ' - ' + res.url);
            if (count === 0) {
                renderTimeout = setTimeout(doRender, resourceWait);
            }
        }
    };

    page.open(url, function(status) {
        if (status !== "success") {
            console.log('Unable to load url');
        } else {
            forcedRenderTimeout = setTimeout(function() {
                console.log(count);
                doRender();
            }, maxRenderWait);
        }
    });

});