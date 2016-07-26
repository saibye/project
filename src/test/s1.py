#!/usr/bin/env python
# -*- encoding: utf8 -*-

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))

#from_addr = raw_input('From: ')
from_addr = "sai"
#user= raw_input('From: ')
user= "18600129523@163.com"
password = raw_input('Password: ')
#to_addr = raw_input('To: ')
to_addr = "673888528@qq.com"
#smtp_server = raw_input('SMTP server: ')
smtp_server = "smtp.163.com"

msg = MIMEText('hello, send by Python...', 'plain', 'utf-8')
msg['From']    = _format_addr(u'Pythoner <%s>' % from_addr)
msg['To']      = _format_addr(u'管理员 <%s>' % to_addr)
msg['Subject'] = Header(u'来自SMTP的问候……', 'utf-8').encode()

server = smtplib.SMTP(smtp_server, 25)
server.set_debuglevel(1)
server.login(user, password)
server.sendmail(user, [to_addr], msg.as_string())
server.quit()

#end
