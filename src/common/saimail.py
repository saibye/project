#!/usr/bin/env python
# -*- encoding: utf8 -*-

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib



g_mail_pass = ""

def saimail_init():
    global g_mail_pass
    g_mail_pass = raw_input('Password: ')
    return


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))


def saimail(_subject, _body):
    global g_mail_pass

    from_addr   = "18600129523@163.com"
    to_addr     = "673888528@qq.com"
    smtp_server = "smtp.163.com"

    msg = MIMEText(_body, 'plain', 'utf-8')
    msg['From'] = _format_addr(u'<%s>' % from_addr)
    msg['To']   = _format_addr(u'<%s>' % to_addr)
    msg['Subject'] = Header(_subject, 'utf-8').encode()

    server = smtplib.SMTP(smtp_server, 25)
    # server.set_debuglevel(1)
    server.login(from_addr, g_mail_pass)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()

if __name__=="__main__":
    saimail_init()
    subject   = u"goodbye subject"
    body      = u"hello, world, buy buy buy"
    saimail(subject, body)


#end
