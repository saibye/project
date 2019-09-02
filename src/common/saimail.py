#!/usr/bin/env python
# -*- encoding: utf8 -*-

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import json

from sailog  import *
from saiconf import *



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

def saimail_old(_subject, _body):

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

    # server = smtplib.SMTP(smtp_server, 25)
    server = smtplib.SMTP_SSL(smtp_server, 465) 
    ##server.set_debuglevel(1)
    server.login(from_addr, mail_pass)
    server.sendmail(from_addr, to_list, msg.as_string())
    server.quit()


def saimail2(_subject, _body):

    smtp_server = sai_conf_get("smtp_server", "host").encode('utf-8')
    from_addr   = sai_conf_get("from_addr",   "mail").encode('utf-8')
    mail_pass   = sai_conf_get("from_addr",   "passwd").encode('utf-8')

    to_addr = ''
    to_addr = sai_conf_get("to_addr2",  "mail")
    to_list = []
    to_list.append(to_addr)

    msg = MIMEText(_body, 'plain', 'utf-8')
    msg['From']     = from_addr
    msg['Bcc']      = to_addr
    msg['Subject']  = Header(_subject, 'utf-8').encode()

    # server = smtplib.SMTP(smtp_server, 25)
    server = smtplib.SMTP_SSL(smtp_server, 465)
    ##server.set_debuglevel(1)
    server.login(from_addr, mail_pass)
    server.sendmail(from_addr, to_list, msg.as_string())
    server.quit()

def saimail_html_old(_subject, _body):

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
        break

    to_addr = ''
    to_addr = ",".join(to_list)

    msg = MIMEText(_body, 'html', 'utf-8')
    msg['From']     = from_addr
    msg['Bcc']      = to_addr
    msg['Subject']  = Header(_subject, 'utf-8').encode()

    # server = smtplib.SMTP(smtp_server, 25)
    server = smtplib.SMTP_SSL(smtp_server, 465)
    ##server.set_debuglevel(1)
    server.login(from_addr, mail_pass)
    server.sendmail(from_addr, to_list, msg.as_string())
    server.quit()


def saimail_inner(_subject, _body, _to_addr, _mail_type):
    encoding = 'utf-8'

    smtp_server = sai_conf_get("smtp_server", "host").encode(encoding)
    from_addr   = sai_conf_get("from_addr",   "mail").encode(encoding)
    mail_pass   = sai_conf_get("from_addr",   "passwd").encode(encoding)

    to_addr = _to_addr
    to_list = []
    to_list.append(to_addr)

    msg = MIMEText(_body, _mail_type, encoding)
    msg['From']     = from_addr
    msg['Bcc']      = to_addr
    msg['Subject']  = Header(_subject, encoding).encode()

    try :
        # server = smtplib.SMTP(smtp_server, 25)
        server = smtplib.SMTP_SSL(smtp_server, 465)
        server.login(from_addr, mail_pass)
        server.sendmail(from_addr, to_list, msg.as_string())
        server.quit()
        return 0
    except Exception, e:
        log_error("error: send mail failure: %s", e)
        return -1


def saimail_html(_subject, _body):

    mail_conf_js = analy_mail_conf()
    if mail_conf_js == -1:
        log_error("邮箱地址配置文件解析错误!")
        return -1

    mail_type = 'html'

    to_addr = ""
    for item in mail_conf_js['to_addrs']:
        to_addr = item['mail']
        log_info("send to mailbox: %s", to_addr)
        saimail_inner(_subject, _body, to_addr, mail_type)

def saimail(_subject, _body):

    mail_conf_js = analy_mail_conf()
    if mail_conf_js == -1:
        log_error("邮箱地址配置文件解析错误!")
        return -1

    mail_type = 'plain'

    to_addr = ""
    for item in mail_conf_js['to_addrs']:
        to_addr = item['mail']
        log_info("send %s to mailbox: %s", mail_type, to_addr)
        saimail_inner(_subject, _body, to_addr, mail_type)

# only to developer user # 2017-7-19
def saimail_dev(_subject, _body):

    mail_conf_js = analy_mail_conf()
    if mail_conf_js == -1:
        log_error("邮箱地址配置文件解析错误!")
        return -1

    mail_type = 'plain'

    to_addr = ""
    for item in mail_conf_js['dev_addrs']:
        to_addr = item['mail']
        log_info("send %s to DEV: %s", mail_type, to_addr)
        saimail_inner(_subject, _body, to_addr, mail_type)


if __name__=="__main__":
    sailog_set("saimail.log")
    subject   = u"xxx subject"
    body      = u"hello, world, buy buy buy"
    log_info("send: [%s, %s]", subject, body)
    """
    saimail2(subject, body)
    """

    """
    subject   = u"subject"
    body      = u"<html>xxello, world, buy buy buy</html>"
    saimail_html(subject, body)
    """

    subject   = u"xxx subject"
    body      = u"hello, world, buy buy buy"
    # saimail(subject, body)

    subject   = u"DEV subject"
    body      = u"hello, world, buy buy buy"
    saimail_dev(subject, body)

# saimail.py
