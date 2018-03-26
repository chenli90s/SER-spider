var system = require('system'),
    page = require("webpage").create();

var fs = require('fs');
var cookiesStr = system.args[1];
phantom.cookiesEnabled = true;
// page.settings.resourceTimeout = system.args[2];
page.settings.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
window.navigator.userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36"

function parseCookie() {
    var cooks = cookiesStr.split('; ')
    cooks.forEach(function (value) {
        var kvs = value.split('=');
        var obs = {};
        obs.name = kvs[0];
        obs.value = kvs[1];
        obs.domain = 'amc.xcar.com.cn';
        obs.path = '/';
        page.addCookie(obs);
        // console.log(JSON.stringify(obs))
    })
}

parseCookie();

page.onLoadFinished = function () {
    if (page.url === 'http://amc.xcar.com.cn/index.php?r=ams/DealerOrder/Index') {
        // page.render('result' + new Date().toDateString() + '.png');
        page.evaluate(function () {
            document.getElementById('yw1').children[2].click()
        })
    }
};


page.onResourceRequested = function (request) {
    // console.log('Request (#' + requestData.id + '): ' + JSON.stringify(requestData));
    // console.log(request.url)
    if (request.url === 'http://amc.xcar.com.cn/index.php?AmsOrder_page=2&ajax=order-index&r=ams%2FdealerOrder%2FIndex'){
        var cookies = page.cookies;
        cookies.map(function (value) {
            value.httponly = '';
            value.secure = '';
        });
        console.log(JSON.stringify(cookies));
        phantom.exit();
    }
};

// page.onResourceReceived = function(response) {
//
//   if (response.url === 'http://amc.xcar.com.cn/index.php?AmsOrder_page=2&ajax=order-index&r=ams%2FdealerOrder%2FIndex'){
//         console.log('Response (#' + response.id + ', stage "' + response.stage + '"): ' + JSON.stringify(response));
//         phantom.exit();
//     }
// };

page.open('http://amc.xcar.com.cn/index.php?r=ams/DealerHome/Index', function (status) {
    if (status === "success") {
        // page.render('result' + new Date().toDateString() + '.png');
        // console.log(status)
        page.evaluate(function () {
            document.getElementById('leftBox').children[0].children[2].children[1].children[0].children[1].children[0].children[0].click()
        })
    }else {
        // page.render('result' + new Date().toDateString() + '.png');
        console.log(status)
        phantom.exit();
    }
});