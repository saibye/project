#!/usr/bin/env python
# -*- encoding: utf8 -*-

import tushare as ts
import time
import pandas as pd
import numpy as np

from saiutil import *
from sailog  import *
from saitu   import *


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


def sql_to_db_nolog(_sql, _db):
    cursor = _db.cursor()

    rv = 0

    try:
        cursor.execute(_sql)
        _db.commit()
    except Exception, e:
        _db.rollback()
        rv = -1

    return rv


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
        log_error("error: sql failed for: %s", e)
        log_error("error: [%s]", _sql)
        _db.rollback()
        rv = -1

    return rv


def df_to_db(_stock_id, _df, _db):
    log_debug("i'm importing %s", _stock_id)

    dt = get_today()
    tm = get_time()

    for row_index, row in _df.iterrows():
        date2, time2 = row_index.split()
        #log_debug("date: %s, time: %s", date2, time2)
        #log_deubg("close is %s ", row.loc['close'])
        sql = row_to_sql(_stock_id, row_index, row, dt, tm)
        sql_to_db(sql, _db)

    return


def get_stock_list_df_db(_db):
    sql = "select distinct stock_id from tbl_30min order by 1 limit 200"
    sql = "select distinct stock_id from tbl_30min order by 1 limit 10"
    sql = "select distinct stock_id from tbl_30min where stock_id='000007'"
    sql = "select distinct stock_id from tbl_30min where stock_id='600016'"
    sql = "select distinct stock_id from tbl_30min order by 1"

    df = pd.read_sql_query(sql, _db);

    return df.set_index('stock_id')



"""
2016/8/16
"""
def get_stock_list_table(_table, _db):
    sql = "select distinct stock_id from %s order by 1" % _table

    df = pd.read_sql_query(sql, _db);
    if df is None:
        return None
    else :
        return df.set_index('stock_id')

"""
2016/10/16
"""
def get_xsg_df(_stock_id, _db):
    sql = "select free_date, free_count, ratio from tbl_xsg where stock_id = '%s' order by free_date" % _stock_id
    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in xsg", _stock_id)
        return None
    else:
        # log_debug("df: \n%s", df)
        return df

"""
2016/10/30
"""
def get_max_pub_date_kday(_stock_id, _db):
    sql = "select max(pub_date) pub_date from tbl_day where stock_id='%s'" % _stock_id

    df = pd.read_sql_query(sql, _db);

    return df


def get_one_kday(_stock_id, _pub_date, _db):
    sql = "select * from tbl_day where stock_id='%s' and pub_date='%s'" % (_stock_id, _pub_date)

    df = pd.read_sql_query(sql, _db);

    return df


def get_recent_pub_date(_pub_date, _N, _db):
    sql = "select distinct pub_date from tbl_day_tech x where pub_date <='%s' order by pub_date desc limit %d" % (_pub_date, _N)

    df = pd.read_sql_query(sql, _db);

    return df


def get_xsg_info(_stock_id, _db):
    info = ""

    xsg = get_xsg_df(_stock_id, _db)

    if xsg is None:
        return info

    if len(xsg) > 0:
        info = "解禁   :\n"

    for row_index, row in xsg.iterrows():
        info += "%s - %5s%% - %s 万\n" % (row['free_date'], row['ratio'], row['free_count'])

    log_debug("info:\n%s", info)

    return info



def sai_save_good(_stock_id, _pub_date, _good_type, _key1, _key2, _key3, _key4, _db):
    inst_date = get_today()
    inst_time = get_time()

    sql = "insert into tbl_good \
(pub_date, stock_id, stock_loc, \
holder, good_type, good_reason, \
v1, v2, v3, v4, \
is_valid, inst_date, inst_time) \
values ('%s', '%s', '%s', \
'%s', '%s', '%s', \
'%s', '%s', '%s', '%s', \
'%s', '%s', '%s')" % \
    (_pub_date, _stock_id, 'cn', 
     'sai', _good_type, 'sweet',
     _key1, _key2, _key3, _key4,
     '1', inst_date, inst_time)

    # log_debug("sql: [%s]", sql)
    rv = sql_to_db(sql, _db)

    return rv


# saisql.py
