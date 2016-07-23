#!/usr/bin/env python
# -*- encoding: utf8 -*-

import tushare as ts
import time
import pandas as pd
import numpy as np

from saiutil import *
from sailog  import *

def row_to_sql(_stock_id, _row_index, _row, _dt, _tm):
    date1, time1 = _row_index.split()

    sql = "insert into tbl_30min \
(pub_date, pub_time, stock_id, stock_loc, \
open_price, high_price, close_price, low_price, \
price_change, change_rate, deal_total_count, \
ma5, ma10, ma20, \
vma5, vma10, vma20, \
turnover, \
inst_date, inst_time) \
values ('%s', '%s', '%s', '%s',  \
'%.02f', '%.2f', '%.2f', \
'%.2f', '%.2f', '%.2f', \
'%.2f', '%.2f', '%.2f', \
'%.2f', \
'%.2f', '%.2f', '%.2f', '%.2f', \
'%s', '%s')" % \
    (date1, time1, _stock_id, 'cn', 
     _row.loc['open'], _row.loc['high'], _row.loc['close'], _row.loc['low'],
     _row.loc['price_change'], _row.loc['p_change'], _row.loc['volume'],
     _row.loc['ma5'], _row.loc['ma10'], _row.loc['ma20'],
     _row.loc['v_ma5'], _row.loc['v_ma10'], _row.loc['v_ma20'],
     _row.loc['turnover'],
     _dt, _tm)

    return sql


def sql_to_db(_sql, _db):

    # 使用cursor()方法获取操作游标 
    cursor = _db.cursor()

    rv = 0

    try:
        # 执行sql语句
        cursor.execute(_sql)
        # 提交到数据库执行
        _db.commit()
    except Exception, e:
        # 发生错误时回滚
        print "execute sql failed: %s" % _sql
        print "error: sql failure for: ", e
        _db.rollback()
        rv = -1
    return rv


def df_to_db(_stock_id, _df, _db):
    print "i'm importing %s" % _stock_id

    dt = get_today()
    tm = get_time()

    for row_index, row in _df.iterrows():
        #print "-----------index is ",  row_index
        date2, time2 = row_index.split()
        #print ("date: %s, time: %s" % (date2, time2))
        #print "close is ", row.loc['close'], ", ma5 is ", row.loc['ma5'], ", change: ", row['p_change']
        sql = row_to_sql(_stock_id, row_index, row, dt, tm)
        #print sql
        sql_to_db(sql, _db)

    return


def clear_stock_from_db(_stock_id, _db):
    sql = "delete from tbl_30min where stock_id = '%s'" % _stock_id
    print sql
    sql_to_db(sql, _db)


def get_stock_list_df_tu():
    df = ts.get_stock_basics()
    return df.sort_index()


def get_stock_list_df_db(_db):
    sql = "select distinct stock_id from tbl_30min order by 1"

    df = pd.read_sql_query(sql, _db);

    return df.set_index('stock_id')

# saisql.py
