import ftplib
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
from setting import *
import requests
from lxml import etree, objectify

class Ftp:

    def __init__(self):
        self.ftp = ftplib.FTP()
        self.ftp.connect(HOST, PORT)
        self.ftp.login(USERNAME, PASSWD)
        self.ftp.cwd(PATH)

    def ftp_upload(self, r_file, n_file):
        '''以二进制形式上传文件'''
        file_remote = r_file
        file_local = n_file
        bufsize = 1024  # 设置缓冲器大小
        fp = open(file_local, 'rb')
        self.ftp.storbinary('STOR ' + file_remote, fp, bufsize)
        fp.close()

    def __del__(self):
        self.ftp.close()

def upload(path):
    ftp = Ftp()
    ftp.ftp_upload('', path)


def send(title):
    msg = MIMEText(title+'cookie失效请尽快处理', 'html', 'utf-8')
    msg['Subject'] = Header('%scookie失效' % title, 'utf-8').encode()
    msg['From'] = 'Spider'
    msg['To'] = Header('管理员')
    smtpObj = smtplib.SMTP_SSL('smtp.qq.com', 465)
    smtpObj.login('admin@chenli90s.cn', 'dpnrgroavcuoichj')
    smtpObj.sendmail('admin@chenli90s.cn', E_MAIL, msg.as_string())

def get(name, count):
    # msg = '%s更新了%d'%(count, name)
    E = objectify.ElementMaker(annotate=False)
    anno_tree = E.request(E.key('1602d45596492ee231fa9bfeadb2e168'), E.filename(name))
    data = etree.tostring(anno_tree).decode()
    resp = requests.post(CALLBACK_URL, data=data)
    if resp.status_code == 200:
        return resp.text


if __name__ == '__main__':
    send('haha')
