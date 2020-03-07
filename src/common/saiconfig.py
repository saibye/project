#!/usr/bin/env python
# -*- encoding: utf8 -*-

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import json
import configparser

from sailog  import *

# saiconfig.py is newer than saiconf.py. 2019-3-3


g_cf_user       = configparser.ConfigParser()


def _sai_config_load_inner(_parser, _file_name):

    if os.getenv("CFG") is None:
        log_error("error: env: CFG not configured")
        return -1

    path = "%s/%s" % (os.getenv("CFG"), _file_name)
    log_debug("user-config-file: <%s>", path)

    if os.path.isfile(path):
        _parser.read(path)
        return 0
    else:
        log_error("error: invalid path: %s", path)
        return -1


def _sai_config_get_inner(_parser, _section, _key):

    val = ""
    if _parser.has_section(_section):
        if _parser.has_option(_section, _key):
            val = _parser.get(_section, _key)
        else:
            log_error("error: option[%s] in section[%s] is not found", _key, _section)
    else:
        log_error("error: section[%s] is not found", _section)

    return val


#-----------------------------------------------------------------------
# 1.user defined config
def sai_config_load_user(_file_name):
    return _sai_config_load_inner(g_cf_user, _file_name)


def sai_config_get_user(_section, _key):
    return _sai_config_get_inner(g_cf_user, _section, _key)



########################################################################


if __name__=="__main__":
    sailog_set("saiconfig.log")


    sai_config_load_user("wine.cfg")
    log_debug("[%s]", sai_config_get_user("case",   "all"))
    log_debug("[%s]", sai_config_get_user("X",      "all")) # fail case
    log_debug("[%s]", sai_config_get_user("case",   "Y"))   # fail case


# saiconfig.py
