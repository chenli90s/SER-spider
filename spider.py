from apscheduler.schedulers.background import BackgroundScheduler
from yiche import main as yiche
from carhome import main_tmp as carhome
from icar import main as icar
from optparse import OptionParser
import sys
from queue import Queue
from datetime import datetime
import time
# def test_func(cc):
#     print(cc, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def run_forever(func, cookie):
    # print(cookie, '----------')
    func(cookie)
    back = BackgroundScheduler()
    back.add_job(func, 'cron', minute="*/20", hour="7-19", args=[cookie, ] )
    # back.add_job(func, 'cron', args=[cookie, ], second="*/1")
    back.start()
    try:
        while True:
            # try:
            #     qun.get(block=True, timeout=1)
            # except:
            time.sleep(1)
            pass
    except:
        pass


def main():
    cookie = ''
    parser = OptionParser()
    parser.add_option('-y',"--yiche", dest="yiche", default=cookie,
                      help="易车.", metavar="yiche", nargs=2)
    parser.add_option('-c',"--carhome", dest="carhome", default=cookie,
                      help="汽车之家.", metavar="carhome", nargs=2)
    parser.add_option('-i',"--icar", dest="icar", default=cookie,
                      help="爱卡.", metavar="icar", nargs=2)
    (options, args) = parser.parse_args()
    # print(options, args)
    if options.yiche:
        run_forever(yiche, options.yiche)
    elif options.carhome:
        run_forever(carhome, options.carhome)
    elif options.icar:
        run_forever(icar, options.icar)
    else:
        parser.print_help()
        sys.exit()

if __name__ == '__main__':
    main()
