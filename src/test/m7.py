#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb

# �����ݿ�����
db = MySQLdb.connect("182.92.239.6", "tudev", "wangfei", "tu" )

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
