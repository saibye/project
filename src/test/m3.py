#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb

# �����ݿ�����
db = MySQLdb.connect("127.0.0.1", "tudev", "wangfei", "tu" )

# ʹ��cursor()������ȡ�����α� 
cursor = db.cursor()

# SQL �������
sql = """INSERT INTO EMPLOYEE(FIRST_NAME,
         LAST_NAME, AGE, SEX, INCOME)
         VALUES ('Mac', 'Mohan', 20, 'M', 2000)"""
try:
   # ִ��sql���
   cursor.execute(sql)
   # �ύ�����ݿ�ִ��
   db.commit()
except:
   # Rollback in case there is any error
   db.rollback()

# �ر����ݿ�����
db.close()
