#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb

# �����ݿ�����
db = MySQLdb.connect("127.0.0.1", "tudev", "wangfei", "tu" )

# ʹ��cursor()������ȡ�����α� 
cursor = db.cursor()

# SQL ��ѯ���
sql = "SELECT * FROM EMPLOYEE \
       WHERE INCOME > '%d'" % (1000)
try:
   # ִ��SQL���
   cursor.execute(sql)
   # ��ȡ���м�¼�б�
   results = cursor.fetchall()
   for row in results:
      fname = row[0]
      lname = row[1]
      age = row[2]
      sex = row[3]
      income = row[4]
      # ��ӡ���
      print "fname=%s,lname=%s,age=%d,sex=%s,income=%d" % \
             (fname, lname, age, sex, income )
except:
   print "Error: unable to fecth data"

# �ر����ݿ�����
db.close()
