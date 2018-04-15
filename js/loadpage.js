var system = require('system'),
    page = require("webpage").create();

var cookiesStr = system.args[1];
phantom.cookiesEnabled = true;
// page.settings.resourceTimeout = system.args[2];
page.settings.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
window.navigator.userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36"

// headers = {}
// headers['Referer'] = 'http://crm.yichehuoban.cn/Customer/CustomerList';
// headers['Host'] = 'dealer.yichehuoban.cn';
// headers['Upgrade-Insecure-Requests'] = '1';
// page.customHeaders = headers;


function parseCookie() {
    var cooks = cookiesStr.split('; ')
    cooks.forEach(function (value) {
        var kvs = value.split('=');
        var obs = {};
        obs.name = kvs[0];
        obs.value = kvs[1];
        obs.domain = 'dealer.yichehuoban.cn';
        obs.path = '/';
        page.addCookie(obs);
        // console.log(JSON.stringify(obs))
    })
}

parseCookie();

// page.onNavigationRequested = function (request) {
//     console.log(request)
// }

page.onLoadFinished = function () {
    if (page.url === 'http://crm.yichehuoban.cn/Customer/CustomerList') {
        // page.render('result' + new Date().toDateString() + '.png');
        var cookies = page.cookies;
        cookies.map(function (value) {
            value.httponly = ''
            value.secure = ''
        });
        console.log(JSON.stringify(cookies));
        phantom.exit();
    }
    if (page.url === 'http://app.easypass.cn/lmsnew/Default.aspx'){
        page.evaluate(function () {
            document.getElementsByClassName('change-new')[0].click()
        })
    }
};

page.onResourceRequested = function (request) {
    // console.log(request.url)
    if(request.url === 'http://crm.yichehuoban.cn/Scripts/common.js'){
        // page.render('result' + new Date().toDateString() + '.png');
        // console.log(JSON.stringify(page.cookies));
        // phantom.exit();
        page.evaluate(function () {
            console.log(Object.keys(document))
        })

    }
};



page.open('http://dealer.yichehuoban.cn/Home/Index', function (status) {

    if (status === "success") {
        // page.render('result' + new Date().toDateString() + '.png');
        // console.log(status)
        page.evaluate(function () {
            document.getElementsByClassName('nav_layer')[0].children[0].children[1].click()
        })
    }else {
        page.render('result' + new Date().toDateString() + '.png');
        console.log(status)
        phantom.exit();
    }
});

// page.onResourceError = function(resourceError) {
//   console.log('Unable to load resource (#' + resourceError.id + 'URL:' + resourceError.url + ')');
//   console.log('Error code: ' + resourceError.errorCode + '. Description: ' + resourceError.errorString);
// };
// console.log(window.navigator.userAgent)
// phantom.exit();

