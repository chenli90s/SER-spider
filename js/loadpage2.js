var system = require('system'),
    page = require("webpage").create();

// var fs = require('fs');
var cookiesStr = system.args[1];
phantom.cookiesEnabled = true;

// page.settings.resourceTimeout = system.args[2];
page.settings.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
window.navigator.userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36"

function parseCookie() {
    var cooks = cookiesStr.split('; ');
    cooks.forEach(function (value) {
        var kvs = value.split('=');
        var obs = {};
        obs.name = kvs[0];
        obs.value = kvs[1];
        obs.domain = 'ics.autohome.com.cn';
        obs.path = '/';
        page.addCookie(obs);
        // console.log(JSON.stringify(obs))
    })
}

parseCookie();


page.onLoadFinished = function () {
    if (page.url === 'https://ics.autohome.com.cn/dms') {

        setTimeout(function () {
            // page.render('result' + new Date().toDateString() + '.png');
            page.evaluate(function () {
                document.getElementsByClassName('J_levelTwo')[2].children[0].click()
            })
        }, 3000);

    }


};

page.onResourceRequested = function (request) {
    var path = request.url.split('?')[0];
    if (path === 'https://ics.autohome.com.cn/Dms/Order/SearchOrderList') {
        var cookies = page.cookies;

        cookies.map(function (value) {
            value.httponly = '';
            value.secure = '';
            value.expires = '';
        });
        var coo = JSON.stringify(cookies);
        console.log(coo);
        phantom.exit();
    }
    var re = new RegExp('https://x.autoimg.cn/dealer/ics/20180412B/Scripts/newics/pv.js?(.+)');
    if (re.test(request.url)) {

        page.evaluate(function (url) {


        })
    }
};



page.open('https://ics.autohome.com.cn/passport/Home/Index', function (status) {

    if (status === "success") {
        // page.render('result' + new Date().toDateString() + '.png');
        // console.log(status)
        page.evaluate(function () {
            document.getElementsByClassName('ics_nav')[0].children[2].children[0].click()
        })
        // phantom.exit();
    } else {
        // page.render('result' + new Date().toDateString() + '.png');
        console.log(status);
        phantom.exit();
    }
});

