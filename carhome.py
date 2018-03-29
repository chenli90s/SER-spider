import requests
from lxml import etree
from optparse import OptionParser
import sys
import platform
from headers import homecar_auth_header as auth_headers
import os
import pendulum
import json
from tools import exc_cmd
from tools import History, getlog
import remote

log = getlog('carhome')


def construct_param(page):
    now = pendulum.now()
    st = now.subtract(days=91).format('YYYY.M.D', formatter='alternative')
    et = now.format('YYYY.M.D', formatter='alternative')
    # print(st)
    # print(et)
    return {'appid': 'dms',
            'orderType': -1,
            'priPub': -1,
            'factoryId': '0',
            'seriesId': '0',
            'specId': '0',
            'areaType': '0',
            'provinceId': -2,
            'cityId': -2,
            'status': -1,
            'startTime': st,
            'endtime': et,
            'pageIndex': page,
            'pageSize': 10,
            'customerPhone': '',
            'salesid': '0',
            'dealerId': '0',
            'productId': '0',
            'taskName': '',
            'assignDealerId': '0',
            'siteId': '0'}


def get(url, page, header):
    resp = requests.get(url, params=construct_param(page), headers=header)
    if resp.status_code == 200:
        return resp.text
    else:
        print(url, resp.status_code)


def get_page(page, cookie):
    resp = requests.get('https://ics.autohome.com.cn/Dms/Order/SearchOrderList',
                        params=construct_param(page), headers=construct_header(cookie))
    if resp.status_code == 200:
        return resp.text
    else:
        print(resp.status_code)


def get_platform():
    if platform.system() == 'Darwin':
        phjs = "bin/phantomjs4mac"
    elif platform.system() == 'Linux':
        phjs = "bin/phantomjs4linux"
    elif platform.system() == 'Windows':
        phjs = "bin\\phantomjs4win.exe"
    else:
        phjs = "bin/phantomjs4linux"
    return phjs


def construct_header(cookies):
    cookie = ''
    for cook in cookies:
        cookie += cook['name'] + '='
        cookie += cook['value'] + '; '
    auth_headers['cookie'] = cookie
    return auth_headers


def construct_cmd(cookie):
    bash = get_platform()
    if 'win' in bash:
        cmd = "%s .\\js\\loadpage2.js  \"%s\" \"30\"" % (
            bash, cookie)
    else:
        cmd = "./%s ./js/loadpage2.js  \"%s\" \"30\"" % (
            bash, cookie)
    return cmd


def start(cookie, history):
    log.info('收集cookie信息')
    cmd = construct_cmd(cookie)
    # cook = os.popen(cmd).read()
    log.info('验证cookie信息...')
    cook = exc_cmd(cmd, 20)
    log.info('验证cookie信息成功！数据抓取中...')
    cook = eval(cook)
    load_data(cook, history)
    # todo 通知
    remote.get("汽车之家", history.index)
    history.save()
    log.info("本次共抓取数据%d, 最后更新时间为"%(history.index, history.ic_endtime_tmp))


def load_data(cook, history):
    data = get_page(1, cook)
    print(data)
    dt = json.loads(data)
    if not dt['returncode']:
        result = dt['result']['list']
        print(result)
        history.ch_endtime_tmp = result[0]['LeadTimeStr']
        rowcount = int(dt['result']['rowcount'])
        if rowcount % 10 > 0:
            page_size = rowcount // 10 + 1
        else:
            page_size = rowcount // 10
    iter_page(cook, page_size, history)
    # todo 通知

    # os.remove('carhome.csv')
    print(history.index)
    history.save()

import time
from datetime import datetime
def iter_page(cook, page_size, history):
    file_name = '汽车之家_%s.csv' % datetime.now().strftime(history.format)
    with open(file_name, 'w') as f:
        for i in range(page_size):
            flag = parse_page(get_page(i+1, cook), history, f)
            if flag:
                return
            time.sleep(4)
    try:
        remote.upload(file_name)
        os.remove(file_name)
    except:
        pass



def parse_page(content, history, f):
    dt = json.loads(content)
    if not dt['returncode']:
        result = dt['result']['list']
        for rt in result:
            customerNameStr = rt['CustomerNameStr']
            name = etree.HTML(customerNameStr).xpath('//a/text()')[0]
            phone = rt['CustomerPhoneStr'].split('<br/>')[0]
            datetimes = rt['LeadTimeStr']
            log.info("%s %s %s" % (name, phone, datetimes))
            if history.vild_carhome(datetimes):
                f.write(name + ',' + phone + "," + datetimes + ',\n')
                history.index += 1
            else:
                return True



def main(cookie):
    if not cookie:
        cookie = 'fvlid=1521556861448CIWs9Hohfq; sessionip=180.175.144.138; sessionid=328B27DC-F12F-4B8E-96DE-4FB492E838C5%7C%7C2018-03-20+22%3A41%3A09.296%7C%7C0; area=310199; ahpau=1; __RequestVerificationToken_L3Bhc3Nwb3J00=2KvCwDFcMjRgEjProvQc1L9vYXK8_KkPaqJUg3QQNyo7-vi57-KKTPmjKaNkXILGwUQL5_9OCkC_F0238BFEvKg7ldE1; precurrent=; login_%e5%be%b7%e8%be%be%e6%b1%bd%e8%bd%a6=3%2f25%2f2018+12%3a09%3a10+AM; MCH_Auth=JfVTJiuf8LqwBnaHO1eQMOfEKlOJBmG7DOjcNrOCHao1Nb3JlaPP5iL7Xe39w2U0v4QrA7KexZq1ZIYtO2pexK2hCAhkU350Z1ZKdTzTlkm_JcXjH-JTMA$149872A437654719301E23555D4F5A42; DealerUniqueLoginInfo=kaOtLOVksdvB33I7q1hmqGkoBvYZf/ETW6+ZQHVMz9OSLXDYkftFmG1hygu4+pkadPv12qhGQk9+1FIUMPnw0wpp5r61nlomISdI+g6YYwU=; sessionvid=4767A426-5DDB-4406-AF77-EBC259783832; ahpvno=34; ref=0%7C0%7C0%7C0%7C2018-03-25+00%3A09%3A14.808%7C2018-03-23+21%3A53%3A48.585; ahrlid=1521907754480fzKy5s9pmp-1521907762038'
        parser = OptionParser()
        parser.add_option("--cookie", dest="cookie", default=cookie,
                          help="Set a cookie.", metavar="cookie")
        (options, args) = parser.parse_args()
        if options.cookie:
            start(options.cookie, History())
        else:
            parser.print_help()
            sys.exit()
    else:
        try:
            start(cookie, History())
        except:
            log.exception('cookie信息不正确')
            remote.send("汽车之家")


if __name__ == '__main__':
    main(None)
