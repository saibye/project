#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb

from sailog  import *

def db_init():
    # 打开数据库连接
    db = MySQLdb.connect("182.92.239.6", "tudev", "wangfei", "tu" )
    return db

def db_end(_db):
    # 关闭数据库连接
    _db.close()

# saidb.py
