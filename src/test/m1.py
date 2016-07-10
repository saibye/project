#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb

# 打开数据库连接
# db = MySQLdb.connect("localhost", "hqdev", "wangfei", "hq" ) # bad

#db = MySQLdb.connect("127.0.0.1", "hqdev", "wangfei", "hq" ) # good 
db = MySQLdb.connect("182.92.239.6", "hqdev", "wangfei", "hq" ) # good

# 使用cursor()方法获取操作游标 
cursor = db.cursor()

# 使用execute方法执行SQL语句
cursor.execute("SELECT VERSION()")

# 使用 fetchone() 方法获取一条数据库。
data = cursor.fetchone()

print "Database version : %s " % data

# 关闭数据库连接
db.close()
