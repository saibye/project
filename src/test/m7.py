#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb

# �����ݿ�����
db = MySQLdb.connect("127.0.0.1", "tudev", "wangfei", "tu" )

# ʹ��cursor()������ȡ�����α� 
cursor = db.cursor()

# SQL ɾ�����
sql = "DELETE FROM EMPLOYEE WHERE AGE > '%d'" % (20)
try:
   # ִ��SQL���
   cursor.execute(sql)
   # �ύ�޸�
   db.commit()
except:
   # ��������ʱ�ع�
   db.rollback()

# �ر�����
db.close()
