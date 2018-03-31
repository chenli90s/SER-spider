from threading import Thread
import datetime, time
import os
from datetime import datetime
import pickle
import logging
import sys

# logger = logging.getLogger('spider')

# 指定logger输出格式
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

# 控制台日志
console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter  # 也可以直接给formatter赋值

def getlog(name):
    logger = logging.getLogger(name)
    # 文件日志
    file_handler = logging.FileHandler("./log/%s.log"%name)
    file_handler.setFormatter(formatter)  # 可以通过setFormatter指定输出格式

    # 为logger添加的日志处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # 指定日志的最低输出级别，默认为WARN级别
    logger.setLevel(logging.INFO)
    return logger

class Result:

    def __init__(self):
        self.data = ''


def exc_cmd(cmd, timeout):
    data = Result()
    t = Thread(target=run_cmd, args=(cmd, data))
    t.start()
    start = datetime.now()
    while not data.data:
        time.sleep(0.2)
        now = datetime.now()
        if (now - start).seconds > timeout:
            t.join(5)
            return None
    return data.data


def run_cmd(cmd, data):
    result = os.popen(cmd).read()
    data.data = result

start = datetime(1970, 4, 19, 12, 20).strftime('%Y-%m-%d %H:%M:%S')

class History:

    def __init__(self):
        self.yc_endtime = datetime(1970, 4, 19, 12, 20).strftime('%Y-%m-%d %H:%M')
        self.ch_endtime = start
        self.ic_endtime = start
        self.format = '%Y-%m-%d %H:%M:%S'
        self.formats = '%Y%m%d%H%M%S'
        self.yc_endtime_tmp = ''
        self.ch_endtime_tmp = ''
        self.ic_endtime_tmp = ''
        self.index = 0
        try:
            f = open('tp.plk', 'rb')
            dt = pickle.load(f)
            self.yc_endtime = dt.get('yc',datetime(1970, 4, 19, 12, 20).strftime('%Y-%m-%d %H:%M'))
            self.ch_endtime = dt.get('ch', start)
            self.ic_endtime = dt.get('ic', start)
            f.close()
        except:
            pass

    def vild_yiche(self, dt):
        format = '%Y-%m-%d %H:%M'
        end_time = datetime.strptime(self.yc_endtime, format)
        now = datetime.strptime(dt, format)
        return end_time < now

    def vild_carhome(self, dt):
        end_time = datetime.strptime(self.ch_endtime, self.format)
        now = datetime.strptime(dt, self.format)
        # print(end_time, now, end_time < now)
        return end_time < now

    def vild_icar(self, dt):
        end_time = datetime.strptime(self.ic_endtime, self.format)
        now = datetime.strptime(dt, self.format)
        return end_time < now

    def test(self):
        f = open('tp.plk', 'rb')
        dt = pickle.load(f)
        if self.yc_endtime_tmp:
            dt['yc'] = self.yc_endtime_tmp
        if self.ch_endtime_tmp:
            dt['ch'] = self.ch_endtime_tmp
        if self.ic_endtime_tmp:
            dt['ic'] = self.ic_endtime_tmp
        print(dt)
        f.close()

    def save(self):
        try:
            f = open('tp.plk', 'rb')
            dt = pickle.load(f)
            if self.yc_endtime_tmp:
                dt['yc'] = self.yc_endtime_tmp
            if self.ch_endtime_tmp:
                dt['ch'] = self.ch_endtime_tmp
            if self.ic_endtime_tmp:
                dt['ic'] = self.ic_endtime_tmp
            f.close()
            tmp = dt
        except Exception as e:
            tmp = {}
            if self.yc_endtime_tmp:
                tmp['yc'] = self.yc_endtime_tmp
            if self.ch_endtime_tmp:
                tmp['ch'] = self.ch_endtime_tmp
            if self.ic_endtime_tmp:
                tmp['ic'] = self.ic_endtime_tmp
        with open('tp.plk', 'wb') as f:
            pickle.dump(tmp, f)

    def __del__(self):
        # tmp = None
        # self.save()
        pass


if __name__ == '__main__':
    history = History()
    print(history.ch_endtime)
    print(history.yc_endtime)
    print(history.ic_endtime)
    history.ch_endtime_tmp = '2018-03-23 12:20:00'
    # print(history.vild_carhome('1977-04-19 12:20:00'))
    # print(history.yc_endtime)
    # print(history.vild_yiche('1977-04-19 12:20'))
    history.save()
    # history.test()