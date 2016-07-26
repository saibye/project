#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 第三方 SMTP 服务
mail_host="smtp.163.com"  #设置服务器
mail_user="18600129523"    #用户名
mail_user="18600129523@163.com"    #用户名
mail_pass="wangfei"   #口令 


sender = '18600129523@163.com'
receivers = ['673888528@qq.com']  # 接收邮件

message = MIMEText('Python... ...', 'plain', 'utf-8')
message['From'] = Header("FromFrom", 'utf-8')
message['To']   = Header("ToTo", 'utf-8')

subject = 'a subject'
message['Subject'] = Header(subject, 'utf-8')


try:
    smtpObj = smtplib.SMTP() 
    smtpObj.set_debuglevel(1)
    smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
    smtpObj.login(mail_user, mail_pass)  
    smtpObj.sendmail(sender, receivers, message.as_string())
    print "邮件发送成功"
except smtplib.SMTPException as e:
    print "Error: 无法发送邮件"
    print e

#end
