#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb

# �����ݿ�����
db = MySQLdb.connect("127.0.0.1", "tudev", "wangfei", "tu") 

# ʹ��cursor()������ȡ�����α� 
cursor = db.cursor()

# SQL �������
sql = "UPDATE EMPLOYEE SET AGE = AGE + 1 WHERE SEX = '%c'" % ('M')
try:
   # ִ��SQL���
   cursor.execute(sql)
   # �ύ�����ݿ�ִ��
   db.commit()
except:
   # ��������ʱ�ع�
   db.rollback()

# �ر����ݿ�����
db.close()
