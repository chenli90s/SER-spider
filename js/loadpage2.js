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
        obs.domain = 'ics.autohome.com.cn';
        obs.path = '/';
        page.addCookie(obs);
        // console.log(JSON.stringify(obs))
    })
}

parseCookie();


page.onLoadFinished = function () {
    if (page.url === 'https://ics.autohome.com.cn/dms') {
        // page.render('result' + new Date().toDateString() + '.png');
        // var cookies = page.cookies;
        // cookies.map(function (value) {
        //     value.httponly = '';
        //     value.secure = ''
        // });
        // console.log(JSON.stringify(cookies));
        // phantom.exit();
        setTimeout(function () {
            // page.render('result' + new Date().toDateString() + '.png');
            page.evaluate(function () {
                document.getElementsByClassName('J_levelTwo')[2].children[0].click()
            })
        }, 3000);

    }

    if(page.url === 'https://ics.autohome.com.cn/Dms/Order/Search'){
        // page.render('result' + new Date().toDateString() + '.png');
        // console.log(JSON.stringify(cookies));
        phantom.exit();
    }
};

page.onResourceRequested = function (request) {
    var path = request.url.split('?')[0];
    if(path === 'https://ics.autohome.com.cn/Dms/Order/SearchOrderList'){
        // page.render('result' + new Date().toDateString() + '.png');
        var cookies = page.cookies;

        cookies.map(function (value) {
            value.httponly = '';
            value.secure = '';
            value.expires = '';
        });
        var coo = JSON.stringify(cookies);
        // var path = 'output.txt';
        // // var content = 'Hello World!';
        // fs.write(path, coo, 'w');
        console.log(coo);
        phantom.exit();
    }
};

page.open('https://ics.autohome.com.cn/passport/Home/Index', function (status) {
    if (status === "success") {
        // page.render('result' + new Date().toDateString() + '.png');
        // console.log(status)
        page.evaluate(function () {
            document.getElementsByClassName('ics_nav')[0].children[2].children[0].click()
        })
    }else {
        page.render('result' + new Date().toDateString() + '.png');
        console.log(status)
        phantom.exit();
    }
});