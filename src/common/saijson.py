#!/usr/bin/env python
# -*- encoding: utf8 -*-

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import json

from sailog  import *

# saijson.py is newer. 2019-3-3


# order is as importance.
g_cf_system     = None
g_cf_secret     = None
g_cf_mail       = None
g_cf_instance   = None


def _sai_json_load(_json_file):

    if os.getenv("CFG") is None:
        log_error("error: env: CFG not jsonured")
        return -1


    path = "%s/%s" % (os.getenv("CFG"), _json_file)


    # log_debug("loading json [%s]", path)
    if os.path.isfile(path):
        fd = open(path)
        return json.load(fd)
    else :
        log_error("error: invalid path[%s]", path)
        return -1


def _sai_json_get(_parser, _section, _key):

    val = ""
    if _section in _parser:
        if _key in _parser:
            val = _parser[_section][_key]
        else:
            log_error("error: key[%s] is not found in section[%s]", _key, _section)
    else:
        log_error("error: section[%s] is not found", _section)

    return val


def _sai_json_get_list(_parser, _section):

    val = []
    if _section in _parser:
        val = _parser[_section]
    else:
        log_error("error: section[%s] is not found", _section)

    return val

#-----------------------------------------------------------------------
# 1.system json
def sai_json_load_system():
    global g_cf_system

    file_name = "system.json"

    g_cf_system  = _sai_json_load(file_name)


def sai_json_get_system(_section, _key):
    global g_cf_system

    if g_cf_system is None:
        if sai_json_load_system() == -1:
            log_error("error: sai_json_load_system")
            return ""

    return _sai_json_get(g_cf_system, _section, _key)


#-----------------------------------------------------------------------
# 2.secret json
def sai_json_load_secret():
    global g_cf_secret

    file_name = "secret.json"

    g_cf_secret  = _sai_json_load(file_name)


def sai_json_get_secret(_section, _key):
    global g_cf_secret

    if g_cf_secret is None:
        if sai_json_load_secret() == -1:
            log_error("error: sai_json_load_secret")
            return ""

    return _sai_json_get(g_cf_secret, _section, _key)


#-----------------------------------------------------------------------
# 3.instance json
def sai_json_load_instance():
    global g_cf_instance

    file_name = "instance.json"

    g_cf_instance  = _sai_json_load(file_name)


def sai_json_get_instance(_section, _key):
    global g_cf_instance

    if g_cf_instance is None:
        if sai_json_load_instance() == -1:
            log_error("error: sai_json_load_instance")
            return ""

    return _sai_json_get(g_cf_instance, _section, _key)


#-----------------------------------------------------------------------
# 4. mail list json
def sai_json_load_mail():
    global g_cf_mail

    file_name = "mail_list.json"

    g_cf_mail  = _sai_json_load(file_name)


def sai_json_get_mail(_section):
    global g_cf_mail

    if g_cf_mail is None:
        if sai_json_load_mail() == -1:
            log_error("error: sai_json_load_mail")
            return ""

    val_list = []
    sec_list = _sai_json_get_list(g_cf_mail, _section)
    for item in sec_list:
        if "email" not in item:
            continue

        mail = item["email"]
        # log_debug("[%s]", mail)
        val_list.append(mail)

    return val_list


########################################################################


def sai_json_get_mysql_host():
    return sai_json_get_system("mysql", "host")

def sai_json_get_mysql_database():
    return sai_json_get_system("mysql", "database")

def sai_json_get_mysql_username():
    return sai_json_get_system("mysql", "username")

def sai_json_get_mysql_password():
    return sai_json_get_system("mysql", "password")

def sai_json_get_mysql_encoding():
    return sai_json_get_system("mysql", "encoding")


if __name__=="__main__":
    sailog_set("saijson.log")

    """
    host    = sai_json_get("mysql", "host")
    log_debug("host: [%s]", host)

    database= sai_json_get("mysql", "database")
    log_debug("database: [%s]", database)

    user    = sai_json_get("mysql", "user")
    log_debug("user: [%s]", user)

    passwd    = sai_json_get("mysql", "passwd")
    log_debug("passwd: [%s]", passwd)

    encode    = sai_json_get("mysql", "encode1")
    log_debug("encode: [%s]", encode)


    sai_load_json2('lihua.cfg')
    log_debug('[%s]', sai_json_get2('wine', 'start_rate'))
    """

    log_debug("sys: [%s]", sai_json_get_mysql_host())
    log_debug("sys: [%s]", sai_json_get_mysql_database())
    log_debug("sys: [%s]", sai_json_get_mysql_username())
    log_debug("sys: [%s]", sai_json_get_mysql_password())
    log_debug("sys: [%s]", sai_json_get_mysql_encoding())


    sai_json_load_system()
    log_debug("system -- [%s]", sai_json_get_system("mysql",    "host"))
    log_debug("system -- [%s]", sai_json_get_system("log",      "level"))

    sai_json_load_secret()
    log_debug("secret -- [%s]", sai_json_get_secret("smtp_server",    "host"))
    log_debug("secret -- [%s]", sai_json_get_secret("from_mail",      "password"))

    sai_json_load_instance()
    log_debug("instance -- [%s]", sai_json_get_instance("instance",   "product_mode"))
    log_debug("INSTANCE -- [%s]", sai_json_get_instance("instance",   "product_MODE"))

    sai_json_load_mail()
    log_debug("mail -- %s", sai_json_get_mail("to_addr_prd"))
    log_debug("mail -- %s", sai_json_get_mail("to_addr_dev"))


# saijson.py
