#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb

from sailog  import *

# 打开数据库连接
db = MySQLdb.connect("127.0.0.1", "tudev", "wangfei", "tu" )

# 使用cursor()方法获取操作游标 
cursor = db.cursor()

# SQL 插入语句
"""
sql = "INSERT INTO EMPLOYEE(FIRST_NAME, \
       LAST_NAME, AGE, SEX, INCOME) \
       VALUES ('%s', '%s', '%d', '%c', '%d' )" % \
       ('Mac', 'Mohan', 20, 'M', 2000)
"""

sql = "show tables"

try:
   # 执行sql语句
   rs = cursor.execute(sql)
   print rs
   # 提交到数据库执行
   db.commit()
except:
   # 发生错误时回滚
   db.rollback()

# 关闭数据库连接
db.close()

# testdb.py