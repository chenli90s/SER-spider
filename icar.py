import requests
from lxml import etree
from optparse import OptionParser
import sys
import platform
from headers import icar_auth_header as auth_headers
import os
from tools import exc_cmd, History, getlog
import remote

log = getlog('icar')

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
        cookie += cook['name']+'='
        cookie += cook['value']+'; '
    auth_headers['Cookie'] = cookie
    return auth_headers

def construct_cmd(cookie):
    bash = get_platform()
    if 'win' in bash:
        cmd = "%s .\\js\\loadpage3.js  \"%s\" \"30\"" % (
            bash, cookie)
    else:
        cmd = "./%s ./js/loadpage3.js  \"%s\" \"30\"" % (
            bash, cookie)
    return cmd

def getPage(cookie, page):
    try:
        resp = requests.get('http://amc.xcar.com.cn/index.php', params={'AmsOrder_page': page, 'ajax': 'order-index', 'r':'ams/dealerOrder/Index'},
                        headers=construct_header(cookie))
        return resp.text
    except:
        pass


def start(cookie, history):
    cmd = construct_cmd(cookie)
    log.info(cmd)
    log.info('收集cookie信息')
    # cook = os.popen(cmd).read()
    log.info('验证cookie信息...')
    cook = eval(exc_cmd(cmd, 20))
    log.info('验证cookie信息成功！数据抓取中...')
    content = getPage(cook, 1)
    page_size, edt = get_page_size(content)
    history.ic_endtime_tmp = edt
    iter_item(cook, page_size, history)
    # todo 通知

    history.save()
    # print(history.index)
    log.info("本次共抓取数据%d, 最后更新时间为%s"%(history.index, history.ic_endtime_tmp))

def get_page_size(content):
    con_el = etree.HTML(content)
    a = con_el.xpath('//p[@id="yw1"]/a')[-2]
    line = con_el.xpath('//div[@class="subject_main"]/table/tbody/tr')[0]
    size = int(a.xpath('./text()')[0])
    dt = " ".join(line.xpath('./td[7]/text()'))
    # print(size)
    return size, dt

import time
from datetime import datetime
from setting import icar_username, crawl_delay
def iter_item(cook, page_size, history):
    file_name = icar_username+'_xcar_%s.csv' % datetime.now().strftime(history.formats)
    with open(file_name, 'wb') as f:
        f.write('类型, 姓名, 联系方式, 上牌城市, 意向车型, 订单产生时间, 负责销售, 分配时间, \n'.encode())
        for i in range(page_size):
            content = getPage(cook, i+1)
            flag = ''
            if content:
                flag = parse_page(content, history, f)
            if flag:
                return

    if history.index > 0:
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
    con_el = etree.HTML(content)
    line_els = con_el.xpath('//div[@class="subject_main"]/table/tbody/tr')
    for line in line_els:
        type = line.xpath('./td[2]/text()')[0]
        name = line.xpath('./td[3]/text()')[0]
        phone = line.xpath('./td[4]/text()')[0]
        city = line.xpath('./td[5]/text()')[0]
        hope_car = line.xpath('./td[6]/text()')
        if hope_car:
            hope_car = hope_car[0]
        else:
            hope_car = ''
        datetimes = line.xpath('./td[7]/text()')
        datetime = " ".join(datetimes)
        leader = line.xpath('./td[8]/text()')[0]
        create_dt = " ".join(line.xpath('./td[9]/text()'))
        if history.vild_icar(datetime):
            log.info("%s %s %s" % (name, phone, datetime))
            strf = "%s, %s, %s,%s, %s, %s,%s, %s,\n"%(type, name, phone,city,hope_car, datetime, leader,create_dt)
            f.write(strf.encode())
            history.index += 1
        else:
            return True
        time.sleep(crawl_delay)


def main(cookie):
    if not cookie:
        cookie = '_Xdwuv=5aa3f3f5c151a; _fwck_www=842fde100ecfbdf8fa27901fadf2da9f; _appuv_www=1a4462481c8e671fd603e8b31363a34d; _Xdwnewuv=1; _PVXuv=5aa3f3fab1a00; Hm_lvt_53eb54d089f7b5dd4ae2927686b183e0=1520694267,1520750841; _fwck_dealer=a505f398f7d60e5690b937321295739a; _appuv_dealer=152bca6c80df2d70a67ee1705667c992; _qddaz=QD.z85y46.rds6bw.jf50et0f; tencentSig=4275013632; BIGipServerpool-c26-xcar-dealeradmin-80=2009665290.20480.0000; PHPSESSID=8ofn379ac5dcgbafpdngmilop4; _qddamta_800816118=4-0; _qdda=4-1.480uz5; _qddab=4-dtvwqg.jf6lenj6'
        parser = OptionParser()
        parser.add_option("--cookie", dest="cookie", default=cookie,
                          help="Set a cookie.", metavar="cookie")
        (options, args) = parser.parse_args()
        if options.cookie:
            try:
                start(options.cookie, History())
            except:
                log.exception('cookie信息不正确')
        else:
            parser.print_help()
            sys.exit()
    else:
        try:
            start(cookie, History())
        except:
            log.exception('cookie信息不正确')
            remote.send("爱卡")

if __name__ == '__main__':
    main(None)
