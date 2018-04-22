from apscheduler.schedulers.background import BackgroundScheduler
from yiche import main as yiche
from carhome import main_tmp as carhome
from icar import main as icar
from optparse import OptionParser
import sys
from queue import Queue
from datetime import datetime

# def test_func(cc):
#     print(cc, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def run_forever(func, cookie):
    # print(cookie, '----------')
    func(cookie)
    back = BackgroundScheduler()
    back.add_job(func, 'cron', minute="*/30", hour="7-19", args=[cookie, ] )
    # back.add_job(func, 'cron', args=[cookie, ], second="*/1")
    back.start()
    try:
        while True:
            # try:
            #     qun.get(block=True, timeout=1)
            # except:
            pass
    except:
        pass

def main():
    cookie = ''
    parser = OptionParser()
    parser.add_option("--yiche", dest="yiche", default=cookie,
                      help="Set a cookie.", metavar="yiche")
    parser.add_option("--carhome", dest="carhome", default=cookie,
                      help="Set a cookie.", metavar="carhome")
    parser.add_option("--icar", dest="icar", default=cookie,
                      help="Set a cookie.", metavar="icar")
    (options, args) = parser.parse_args()
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
