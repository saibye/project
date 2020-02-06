#!/usr/bin/env python
# -*- encoding: utf8 -*-

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import json
import ConfigParser

from sailog  import *

# saiconf.py is older. 2019-3-3

g_sai_conf = None

cf = ConfigParser.ConfigParser()

def sai_load_conf2(_file_name):
    global cf
    sai_conf_path = "%s/project/cfg/%s" % (os.getenv('HOME'), _file_name)
    cf.read(sai_conf_path)

def sai_conf_get2(_section, _key):
    global cf
    return cf.get(_section, _key)

def sai_load_conf():
    sai_conf_path = "%s/.local/sai.json" % os.getenv('HOME')
    # log_debug("loading config [%s]", sai_conf_path)
    if os.path.isfile(sai_conf_path):
        json_file_fd = open(sai_conf_path)
        return json.load(json_file_fd)
    else :
        log_error("error: invalid sai_conf_path[%s]!", sai_conf_path)
        return -1


def sai_conf_get(_section, _key):
    global g_sai_conf

    if g_sai_conf is None:
        g_sai_conf = sai_load_conf()
        if g_sai_conf == -1:
            log_error("error: sai_load_conf failure")
            return -1
        else:
            # log_debug("config load succeed")
            pass
    else:
        # log_debug("already loaded")
        pass

    val = ""
    if _section in g_sai_conf:
        if _key in g_sai_conf[_section]:
            val = g_sai_conf[_section][_key]
        else:
            log_error("error: key[%s] in [%s] not found", _key, _section)
    else:
        log_error("error: section[%s] not found", _section)

    return val


def sai_conf_get_mysql_host():
    return sai_conf_get("mysql", "host")

def sai_conf_get_mysql_database():
    return sai_conf_get("mysql", "database")

def sai_conf_get_mysql_user():
    return sai_conf_get("mysql", "user")

def sai_conf_get_mysql_passwd():
    return sai_conf_get("mysql", "passwd")

def sai_conf_get_mysql_encode():
    return sai_conf_get("mysql", "encode")


if __name__=="__main__":
    sailog_set("saiconf.log")

    """
    host    = sai_conf_get("mysql", "host")
    log_debug("host: [%s]", host)

    database= sai_conf_get("mysql", "database")
    log_debug("database: [%s]", database)

    user    = sai_conf_get("mysql", "user")
    log_debug("user: [%s]", user)

    passwd    = sai_conf_get("mysql", "passwd")
    log_debug("passwd: [%s]", passwd)

    encode    = sai_conf_get("mysql", "encode1")
    log_debug("encode: [%s]", encode)
    """

    log_debug("[%s]", sai_conf_get_mysql_host())
    log_debug("[%s]", sai_conf_get_mysql_database())
    log_debug("[%s]", sai_conf_get_mysql_user())
    log_debug("[%s]", sai_conf_get_mysql_passwd())
    log_debug("[%s]", sai_conf_get_mysql_encode())

    sai_load_conf2('lihua.cfg')
    log_debug('[%s]', sai_conf_get2('wine', 'start_rate'))


# saiconf.py
