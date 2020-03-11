#!/usr/bin/env python
# -*- encoding: utf8 -*-

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

from email.message import EmailMessage
from email.utils import make_msgid
import mimetypes

import smtplib
import json
import saiobj


from sailog  import *
from saiconf import *


def saimail_set_subject_prefix(_v):
    saiobj.g_subject_prefix = _v
    return

def saimail_init():
    return



def analy_mail_conf():
    mail_conf_path = "%s/.local/mail.conf.json" % os.getenv('HOME')
    if os.path.isfile(mail_conf_path):
        json_file_fd = open(mail_conf_path)
        return json.load(json_file_fd)
    else :
        log_error("mail_conf_path[%s] 错误!", mail_conf_path)
        return -1

def saimail_old(_subject, _body):

    mail_conf_js = analy_mail_conf()
    if mail_conf_js == -1:
        log_error("邮箱地址配置文件解析错误!")
        return -1

    smtp_server = mail_conf_js['smtp_server']['host']
    from_addr   = mail_conf_js['from_addr']['mail']
    mail_pass   = mail_conf_js['from_addr']['passwd']
    to_list = []
    for item in mail_conf_js['to_addrs']:
        to_list.append(item['mail'])

    to_addr = ''
    to_addr = ",".join(to_list)

    msg = MIMEText(_body, 'plain', 'utf-8')
    msg['From']     = from_addr
    msg['Bcc']      = to_addr
    msg['Subject']  = Header(_subject, 'utf-8')

    # server = smtplib.SMTP(smtp_server, 25)
    server = smtplib.SMTP_SSL(smtp_server, 465) 
    ##server.set_debuglevel(1)
    server.login(from_addr, mail_pass)
    server.sendmail(from_addr, to_list, msg.as_string())
    server.quit()


def saimail2(_subject, _body):

    smtp_server = sai_conf_get("smtp_server", "host")
    from_addr   = sai_conf_get("from_addr",   "mail")
    mail_pass   = sai_conf_get("from_addr",   "passwd")

    to_addr = ''
    to_addr = sai_conf_get("to_addr2",  "mail")
    to_list = []
    to_list.append(to_addr)

    msg = MIMEText(_body, 'plain', 'utf-8')
    msg['From']     = from_addr
    msg['Bcc']      = to_addr
    msg['Subject']  = Header(_subject, 'utf-8')

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

    smtp_server = mail_conf_js['smtp_server']['host']
    from_addr   = mail_conf_js['from_addr']['mail']
    mail_pass   = mail_conf_js['from_addr']['passwd']

    to_list = []
    for item in mail_conf_js['to_addrs']:
        to_list.append(item['mail'])
        break

    to_addr = ''
    to_addr = ",".join(to_list)

    msg = MIMEText(_body, 'html', 'utf-8')
    msg['From']     = from_addr
    msg['Bcc']      = to_addr
    msg['Subject']  = Header(_subject, 'utf-8')

    # server = smtplib.SMTP(smtp_server, 25)
    server = smtplib.SMTP_SSL(smtp_server, 465)
    ##server.set_debuglevel(1)
    server.login(from_addr, mail_pass)
    server.sendmail(from_addr, to_list, msg.as_string())
    server.quit()


def saimail_inner(_subject, _body, _to_addr, _mail_type):
    encoding = 'utf-8'

    smtp_server = sai_conf_get("smtp_server", "host")
    from_addr   = sai_conf_get("from_addr",   "mail")
    mail_pass   = sai_conf_get("from_addr",   "passwd")

    to_addr = _to_addr
    to_list = []
    to_list.append(to_addr)

    msg = MIMEText(_body, _mail_type, encoding)
    msg['From']     = from_addr
    msg['Bcc']      = to_addr
    msg['Subject']  = Header(_subject, encoding)

    try :
        # server = smtplib.SMTP(smtp_server, 25)
        server = smtplib.SMTP_SSL(smtp_server, 465)
        server.login(from_addr, mail_pass)
        server.sendmail(from_addr, to_list, msg.as_string())
        server.quit()
        return 0
    except Exception as e:
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


def saimail_photo_inner(_subject, _body, _photo_file_path, _to_addr):

    smtp_server = sai_conf_get("smtp_server", "host")
    from_addr   = sai_conf_get("from_addr",   "mail")
    mail_pass   = sai_conf_get("from_addr",   "passwd")

    to_addr = _to_addr
    to_list = []
    to_list.append(to_addr)

    msg = EmailMessage()

    # generic email headers
    msg['From']     = 'SAI <%s>' % from_addr
    msg['Subject']  = _subject

    # set the plain text body
    msg.set_content('This is a plain text body.')

    # now create a Content-ID for the image
    image_cid = make_msgid(domain='sai.com')
    # if `domain` argument isn't provided, it will 
    # use your computer's name

    html = """\
    <html>
        <body>
            <p>%s<br>
            </p>
            <img src="cid:{image_cid_x}">
        </body>
    </html>"""  % (_body)

    # set an alternative html body
    msg.add_alternative(html.format(image_cid_x=image_cid[1:-1]), subtype='html')
    # image_cid looks like <long.random.number@sai.com>
    # to use it as the img src, we don't need `<` or `>`
    # so we use [1:-1] to strip them off


    # now open the image and attach it to the email
    with open(_photo_file_path, 'rb') as img:

        # know the Content-Type of the image
        maintype, subtype = mimetypes.guess_type(img.name)[0].split('/')

        # attach it
        msg.get_payload()[1].add_related(img.read(), 
                                             maintype=maintype, 
                                             subtype=subtype, 
                                             cid=image_cid)


    try :
        # server = smtplib.SMTP(smtp_server, 25)
        server = smtplib.SMTP_SSL(smtp_server, 465)
        server.login(from_addr, mail_pass)
        server.sendmail(from_addr, to_list, msg.as_string())
        server.quit()
        return 0
    except Exception as e:
        log_error("error: send mail failure: %s", e)
        return -1



def saimail_photos_inner(_subject, _body, _photo_file_path_list, _to_addr):

    smtp_server = sai_conf_get("smtp_server", "host")
    from_addr   = sai_conf_get("from_addr",   "mail")
    mail_pass   = sai_conf_get("from_addr",   "passwd")

    to_addr = _to_addr
    to_list = []
    to_list.append(to_addr)

    msg = EmailMessage()

    # generic email headers
    msg['From']     = 'SAI <%s>' % from_addr
    msg['Subject']  = _subject

    # set the plain text body
    msg.set_content('This is a plain text body.')


    html_image = ''
    cid_map = {}
    for one in _photo_file_path_list:

        # image_cid looks like <long.random.number@sai.com>
        # to use it as the img src, we don't need `<` or `>`
        # so we use [1:-1] to strip them off
        image_cid = make_msgid(domain='sai.com')[1:-1]

        # later use
        cid_map[one] = image_cid

        html_image += '\n<p><img src="cid:{image_cid}"><br></p>\n'.format(image_cid=image_cid)


    html = """\
    <html>
        <body>
            <p>%s<br>
            </p>
            %s
        </body>
    </html>"""  % (_body, html_image)

    # set an alternative html body
    msg.add_alternative(html, subtype='html')

    for one in _photo_file_path_list:
        image_cid = cid_map[one]

        # now open the image and attach it to the email
        with open(one, 'rb') as img:

            # know the Content-Type of the image
            maintype, subtype = mimetypes.guess_type(img.name)[0].split('/')

            # attach it
            msg.get_payload()[1].add_related(img.read(), 
                                                 maintype=maintype, 
                                                 subtype=subtype, 
                                                 cid=image_cid)

    try :
        # server = smtplib.SMTP(smtp_server, 25)
        server = smtplib.SMTP_SSL(smtp_server, 465)
        server.login(from_addr, mail_pass)
        server.sendmail(from_addr, to_list, msg.as_string())
        server.quit()
        return 0
    except Exception as e:
        log_error("error: send mail failure: %s", e)
        return -1



# the message is ready now
# you can write it to a file
# or send it using smtplib




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


# 2020-3-8
# one photo
def saimail_photo(_subject, _body, _photo_file_path):

    mail_conf_js = analy_mail_conf()
    if mail_conf_js == -1:
        log_error("邮箱地址配置文件解析错误!")
        return -1

    # mail_type = 'plain'

    to_addr = ""
    for item in mail_conf_js['to_addrs']:
        to_addr = item['mail']
        log_info("send photo to DEV: %s", to_addr)
        saimail_photo_inner(_subject, _body, _photo_file_path, to_addr)

# 2020-3-11
# photo-list
def saimail_photos(_subject, _body, _photo_file_path_list):

    mail_conf_js = analy_mail_conf()
    if mail_conf_js == -1:
        log_error("邮箱地址配置文件解析错误!")
        return -1

    # mail_type = 'plain'

    to_addr = ""
    for item in mail_conf_js['to_addrs']:
        to_addr = item['mail']
        log_info("send photo to DEV: %s", to_addr)
        saimail_photos_inner(_subject, _body, _photo_file_path_list, to_addr)


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
    # saimail_dev(subject, body)

    subject   = u"DEV subject你好"
    body      = u"hello, world, buy buy buy你好"
    # saimail_dev(subject, body)

    subject   = u"DEV 照片"
    body      = u"你好 photo\nnew line"
    photo_file_path = '/home/sai3/project/src/trace/000725.png'
    photo_file_path = '/home/sai3/project/src/trace/601066.png'
    # saimail_photo(subject, body, photo_file_path)

    subject   = u"DEV 照片s"
    body      = u"你好 Photos\nnew line"
    photo_file_path = '/home/sai3/project/src/trace/000725.png'
    photo_file_path = '/home/sai3/project/src/trace/601066.png'
    photo_list = []
    photo_list.append('/home/sai3/project/tmp/000725.png')
    photo_list.append('/home/sai3/project/tmp/002594.png')
    saimail_photos(subject, body, photo_list)


# saimail.py
