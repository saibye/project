#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb

# �����ݿ�����
# db = MySQLdb.connect("localhost", "hqdev", "wangfei", "hq" ) # bad

#db = MySQLdb.connect("127.0.0.1", "hqdev", "wangfei", "hq" ) # good 
db = MySQLdb.connect("182.92.239.6", "hqdev", "wangfei", "hq" ) # good

# ʹ��cursor()������ȡ�����α� 
cursor = db.cursor()

# ʹ��execute����ִ��SQL���
cursor.execute("SELECT VERSION()")

# ʹ�� fetchone() ������ȡһ�����ݿ⡣
data = cursor.fetchone()

print "Database version : %s " % data

# �ر����ݿ�����
db.close()
