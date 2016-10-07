#!/usr/bin/env python
# -*- encoding: utf8 -*-

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import json

from sailog  import *



def saimail_init():
    return


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))

def analy_mail_conf():
    mail_conf_path = "%s/.local/mail.conf.json" % os.getenv('HOME')
    if os.path.isfile(mail_conf_path):
        json_file_fd = file(mail_conf_path)
        return json.load(json_file_fd)
    else :
        log_error("mail_conf_path[%s] 错误!", mail_conf_path)
        return -1

def saimail(_subject, _body):

    mail_conf_js = analy_mail_conf()
    if mail_conf_js == -1:
        log_error("邮箱地址配置文件解析错误!")
        return -1

    smtp_server = mail_conf_js['smtp_server']['host'].encode('utf-8')
    from_addr   = mail_conf_js['from_addr']['mail'].encode('utf-8')
    mail_pass   = mail_conf_js['from_addr']['passwd'].encode('utf-8')
    to_list = []
    for item in mail_conf_js['to_addrs']:
        to_list.append(item['mail'])

    to_addr = ''
    to_addr = ",".join(to_list)

    msg = MIMEText(_body, 'plain', 'utf-8')
    msg['From']     = from_addr
    msg['Bcc']      = to_addr
    msg['Subject']  = Header(_subject, 'utf-8').encode()

    server = smtplib.SMTP(smtp_server, 25)
    ##server.set_debuglevel(1)
    server.login(from_addr, mail_pass)
    server.sendmail(from_addr, to_list, msg.as_string())
    server.quit()

if __name__=="__main__":
    sailog_set("saimail.log")
    subject   = u"goodbye subject"
    body      = u"hello, world, buy buy buy"
    saimail(subject, body)

# saimail.py
