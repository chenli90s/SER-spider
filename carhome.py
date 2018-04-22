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
from tools import History, getlog, parse_cookie
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
    try:
        resp = requests.get('https://ics.autohome.com.cn/Dms/Order/SearchOrderList',
                            params=construct_param(page), headers=construct_header(cookie))
        if resp.status_code == 200:
            return resp.text
        else:
            print(resp.status_code)
    except Exception as e:
        log.exception(e)


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

def make_simple_header(cookie):
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
    log.info(cmd)
    # cook = os.popen(cmd).read()
    log.info('验证cookie信息...')
    cook = exc_cmd(cmd, 20)
    log.info('验证cookie信息成功！数据抓取中...')
    cook = eval(cook)
    load_data(cook, history)
    # todo 通知
    history.save()
    log.info("本次共抓取数据%d, 最后更新时间为%s"%(history.index, history.ch_endtime_tmp))


def start_tmp(cookie, history):
    log.info('验证cookie信息成功！数据抓取中...')
    cook = parse_cookie(cookie)
    load_data(cook, history)
    history.save()
    log.info("本次共抓取数据%d, 最后更新时间为%s" % (history.index, history.ch_endtime_tmp))

def main_tmp(cookie):
    try:
        start_tmp(cookie, History())
    except:
        log.exception('cookie信息不正确')
        remote.send("汽车之家")


def load_data(cook, history):
    # print(cook)
    data = get_page(1, cook)
    # print(data)
    dt = json.loads(data)
    if not dt['returncode']:
        result = dt['result']['list']
        # print(result)
        history.ch_endtime_tmp = result[0]['LeadTimeStr']
        rowcount = int(dt['result']['rowcount'])
        if rowcount % 10 > 0:
            page_size = rowcount // 10 + 1
        else:
            page_size = rowcount // 10
    iter_page(cook, page_size, history)
    # todo 通知

    # os.remove('carhome.csv')
    # print(history.index)
    history.save()

import time
from datetime import datetime
from setting import carhome_username,crawl_delay
def iter_page(cook, page_size, history):
    file_name = carhome_username+'_autohome_%s.csv' % datetime.now().strftime(history.formats)
    with open(file_name, 'w') as f:
        f.write('客户姓名' + ','
                + '客户号码' + ","
                + '来电归属' + ","
                + '归属店铺' + ","
                + '线索获得时间' + ","
                + '上牌地区' + ","
                + '线索状态' + ","
                + '线索类型' + ","
                + '商业产品来源	' + ","
                + '负责销售	' + ","
                + '线索意向车型	' + ","
                + ',\n')
        for i in range(page_size):
            flag = parse_page(get_page(i+1, cook), history, f)
            if flag:
                return

    if history.index>0:
        try:
            remote.upload(file_name)
            log.info('上传完成')
        except:
            remote.send_msg('sftp服务器失效')
            sys.exit()
        try:
            remote.get(file_name, history.index)
        except:
            remote.send_msg('通知服务器异常，请尽快检查')


def parse_page(content, history, f):
    dt = json.loads(content)
    if not dt['returncode']:
        result = dt['result']['list']
        for rt in result:
            customerNameStr = rt['CustomerNameStr']
            name = etree.HTML(customerNameStr).xpath('//a/text()')[0]
            phone = rt['CustomerPhoneStr'].split('<br/>')[0]
            local = rt['CustomerPhoneStr'].split('<br/>')[1]
            shop = rt['GetLeadDealerNameStr']
            datetimes = rt['LeadTimeStr']
            LicenseCityStr = rt['LicenseCityStr']
            ordstatus = rt['OrderStateStr']
            ordtype = " ".join(rt['OrderTypeStr'].split('<br/>'))
            proname = rt['ProductNameStr']
            SalesNameStr = rt['SalesNameStr']
            SpecNameStr = rt['SpecNameStr']
            if SpecNameStr == "<span class='grey-999'>未标注</span>":
                SpecNameStr = '未标注'
            log.info("%s %s %s" % (name, phone, datetimes))
            if history.vild_carhome(datetimes):
                f.write(name + ','
                        + phone + ","
                        + local + ","
                        + shop + ","
                        + datetimes + ","
                        + LicenseCityStr + ","
                        + ordstatus + ","
                        + ordtype + ","
                        + proname + ","
                        + SalesNameStr + ","
                        + SpecNameStr +
                        ',\n')
                history.index += 1
            else:
                return True
            time.sleep(crawl_delay)



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

# from spider import run_forever
if __name__ == '__main__':
    # cookie_dt = parse_cookie("fvlid=1521556861448CIWs9Hohfq; sessionid=328B27DC-F12F-4B8E-96DE-4FB492E838C5%7C%7C2018-03-20+22%3A41%3A09.296%7C%7C0; area=310199; sessionip=114.95.225.155; ahpau=1; ref=0%7C0%7C0%7C0%7C2018-04-21+17%3A34%3A08.993%7C2018-04-01+23%3A04%3A32.132; __RequestVerificationToken_L3Bhc3Nwb3J00=ggjuVz2L55YsaC-6Ma2mr-0lcVFcN35X_PVRH3jt4Ak14dD2FDZ8R72VQQG0PKIe4F0MLgb9Mw3q2b7Ie3AcIPgF0l01; ahpvno=9; ahrlid=1524377063741NRQl1km0Hv-1524377079722; login_%e5%be%b7%e8%be%be%e6%b1%bd%e8%bd%a6=4%2f22%2f2018+2%3a04%3a41+PM; MCH_Auth=JfVTJiuf8LqwBnaHO1eQMOfEKlOJBmG7DOjcNrOCHao1Nb3JlaPP5iL7Xe39w2U0v4QrA7KexZpL8BASctiff-v4MHGViOyFZ1ZKdTzTlkkVjaOo2_Lodv30CSnP-sQ0$D73F65556CD811ADE269A0C46978C33B; DealerUniqueLoginInfo=kaOtLOVksdvB33I7q1hmqCvximZgNnnBeb+dZ5l1yfORTeRh0VcjsoGpG74R87NiNKF1m0dfYMnuFblaZvKkF9svCYAf2ZkYxoABvK5EwQo=")
    # res = get_page(1, cookie_dt)
    # data = json.loads(res)
    # print(len(data['result']['list']))
    # cook = "fvlid=1521556861448CIWs9Hohfq; sessionid=328B27DC-F12F-4B8E-96DE-4FB492E838C5%7C%7C2018-03-20+22%3A41%3A09.296%7C%7C0; area=310199; sessionip=114.95.225.155; ahpau=1; ref=0%7C0%7C0%7C0%7C2018-04-21+17%3A34%3A08.993%7C2018-04-01+23%3A04%3A32.132; __RequestVerificationToken_L3Bhc3Nwb3J00=ggjuVz2L55YsaC-6Ma2mr-0lcVFcN35X_PVRH3jt4Ak14dD2FDZ8R72VQQG0PKIe4F0MLgb9Mw3q2b7Ie3AcIPgF0l01; ahpvno=9; ahrlid=1524377063741NRQl1km0Hv-1524377079722; login_%e5%be%b7%e8%be%be%e6%b1%bd%e8%bd%a6=4%2f22%2f2018+2%3a04%3a41+PM; MCH_Auth=JfVTJiuf8LqwBnaHO1eQMOfEKlOJBmG7DOjcNrOCHao1Nb3JlaPP5iL7Xe39w2U0v4QrA7KexZpL8BASctiff-v4MHGViOyFZ1ZKdTzTlkkVjaOo2_Lodv30CSnP-sQ0$D73F65556CD811ADE269A0C46978C33B; DealerUniqueLoginInfo=kaOtLOVksdvB33I7q1hmqCvximZgNnnBeb+dZ5l1yfORTeRh0VcjsoGpG74R87NiNKF1m0dfYMnuFblaZvKkF9svCYAf2ZkYxoABvK5EwQo="
    cook = "fvlid=1521556861448CIWs9Hohfq; sessionid=328B27DC-F12F-4B8E-96DE-4FB492E838C5%7C%7C2018-03-20+22%3A41%3A09.296%7C%7C0; area=310199; ahpau=1; __RequestVerificationToken_L3Bhc3Nwb3J00=ggjuVz2L55YsaC-6Ma2mr-0lcVFcN35X_PVRH3jt4Ak14dD2FDZ8R72VQQG0PKIe4F0MLgb9Mw3q2b7Ie3AcIPgF0l01; login_%e5%be%b7%e8%be%be%e6%b1%bd%e8%bd%a6=4%2f22%2f2018+2%3a04%3a41+PM; MCH_Auth=JfVTJiuf8LqwBnaHO1eQMOfEKlOJBmG7DOjcNrOCHao1Nb3JlaPP5iL7Xe39w2U0v4QrA7KexZpL8BASctiff-v4MHGViOyFZ1ZKdTzTlkkVjaOo2_Lodv30CSnP-sQ0$D73F65556CD811ADE269A0C46978C33B; DealerUniqueLoginInfo=kaOtLOVksdvB33I7q1hmqCvximZgNnnBeb+dZ5l1yfORTeRh0VcjsoGpG74R87NiNKF1m0dfYMnuFblaZvKkF9svCYAf2ZkYxoABvK5EwQo=; sessionip=180.175.14.105; sessionvid=06F09F9B-73CA-4481-9E1B-17441F0F53A4; precurrent=; ahpvno=14; ref=0%7C0%7C0%7C0%7C2018-04-22+15%3A08%3A41.358%7C2018-04-01+23%3A04%3A32.132"
    main_tmp(cook)
    # cook = sys.argv[1]
    # run_forever(main_tmp(cook))

