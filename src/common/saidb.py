#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb

from sailog  import *
from saiconf import *

def db_init():
    # 打开数据库连接
    host    = sai_conf_get_mysql_host()
    dbname  = sai_conf_get_mysql_database()
    user    = sai_conf_get_mysql_user()
    passwd  = sai_conf_get_mysql_passwd()
    encode  = sai_conf_get_mysql_encode()
    db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=dbname, charset=encode)  # 111
    if db is None:
        log_error("error: db_init failure")

    return db

def db_end(_db):
    # 关闭数据库连接
    _db.close()

if __name__ == "__main__":
    sailog_set("saidb.log")
    db = db_init()
    if db is None:
        log_debug("error: db_init")
    else :
        log_debug("nice: db_init")

# saidb.py
