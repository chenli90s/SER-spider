import requests
from lxml import etree
from optparse import OptionParser
import sys
import platform
from headers import yiche_auth_headers as auth_headers
from tools import exc_cmd, History, getlog
import remote
from datetime import datetime

log = getlog('yiche')





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
        cmd = "%s .\\js\\loadpage.js  \"%s\" \"30\"" % (
            bash, cookie)
    else:
        cmd = "./%s ./js/loadpage.js  \"%s\" \"30\"" % (
            bash, cookie)
    return cmd

def getPage(cookie, page):
    resp = requests.post('http://crm.yichehuoban.cn/Customer/CustomerList', data={'pageIndex': page},
                        headers=construct_header(cookie))
    return resp.text


def start(cookie, history):
    log.info('收集cookie信息')
    cmd = construct_cmd(cookie)
    # print(cmd)
    log.info('验证cookie信息...')
    cook = exc_cmd(cmd, 20)
    log.info('验证cookie信息成功！数据抓取中...')
    cookies = eval(cook)
    # page_size = get_page_size(getPage(cookies, 2))
    # iter_data(cookies, page_size)
    # parse_page(getPage(cookies, 5))
    file_name = '易车_%s.csv'%datetime.now().strftime(history.format)
    with open(file_name, 'w') as f:
        run_spider(cookies, history, f)
    # todo: 上传并通知
    remote.upload(file_name)
    remote.get('易车', history.index)
    # os.remove(file_name)
    history.save()
    # print(history.index)
    log.info("本次共抓取数据%d, 最后更新时间为"%(history.index, history.ic_endtime_tmp))


def run_spider(cookies, history, f):
    page_size, dat = get_page_size(getPage(cookies, 1))
    history.yc_endtime_tmp = dat
    iter_data(cookies, page_size, history, f)

def get_page_size(context):
    el = etree.HTML(context)
    res = el.xpath('//div[@class="pagination"]/ul/li')[-1]
    href = res.xpath('./a/@href')[0];
    page = href.split('=')[1]
    tr = el.xpath('//table/tbody/tr')[0]
    times = tr.xpath('./td[4]/text()')
    datetimes = " ".join(times)
    return int(page), datetimes

import time
def iter_data(cookies, page_size, history, f):
    for i in range(page_size):
        flag = parse_page(getPage(cookies, i+1), history, f)
        if flag:
           return
        time.sleep(1)


def parse_page(context, history, f):
    els = etree.HTML(context)
    trs = els.xpath('//table/tbody/tr')
    for tr in trs:
        name_phone = tr.xpath('./td[1]/text()')
        name = name_phone[0].strip()
        phone = name_phone[2].strip()
        times = tr.xpath('./td[4]/text()')
        datetimes = " ".join(times)
        log.info("%s %s %s"%(name, phone, datetimes))
        if history.vild_yiche(datetimes):
            f.write("%s, %s, %s,\n"%(name, phone, datetimes))
            history.index +=1
        else:
            return True



def main(cookie):
    if not cookie:
        cookie = 'isAuto=False; currentLoginPage=/IMS/Login.aspx; 5255=; ASP.NET_SessionId=yeh0bguwlgg022fk5mphjn3h; EasySystem=F7187890872F451DDFC412D24B9C28CAFE99CFCDC26047B321D0E63675CA465181783CCBCA13F203B4F9514A7E3ACFAD08E69A0B8FF57A7A741AC2F19C8E798E2B5F2A4A018B92691CB1F680811C05ED305663C6; UserToken=gaSaoTEOKfQIBPBjhRn0RqanI/+dfI2FRJaQZ/8COyHnt/ydyA9UArjtW7bStGRQXxOgOrG5muhB+Qsv1DyG0HK8si8tZwaxp4RoQOHv7Z4=; newLoginName=5255; loginKey=6D0BDE95B8858FAC8055F2815B0E289C; loginName=873518796@qq.com'
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
            remote.send('易车')


if __name__ == '__main__':
    main(None)
