#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb

from sailog  import *

def db_init():
    # 打开数据库连接
    # db = MySQLdb.connect("127.0.0.1", "tudev", "wangfei", "tu" )
    db = MySQLdb.connect(host="127.0.0.1", user="tudev", passwd="wangfei", db="tu", charset="utf8") 
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
