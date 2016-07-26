#!/usr/bin/env python
# -*- encoding: utf8 -*-


from sqlalchemy import create_engine
import tushare as ts
import MySQLdb
import time
import pandas as pd
import numpy as np

from saiutil import *
from saidb   import *
from saisql  import *
from saicalc import *
from sailog  import *

#######################################################################


"""
"""

g_map   = {}

def get_df_from_db1(_stock_id, _db):
    #sql = "select * from tbl_30min t where stock_id='%s' order by pub_date desc, pub_time desc limit 300" % _stock_id
    #sql = "select * from tbl_30min t where stock_id='%s' order by pub_date desc, pub_time desc limit 10" % _stock_id
    sql = "select * from tbl_30min t where stock_id='%s' and ( pub_date='2016-07-25' or pub_date= '2016-07-22') \
           order by pub_date desc, pub_time desc limit 10" % _stock_id

    df = pd.read_sql_query(sql, _db);

    return df

def get_df_from_db2(_stock_id, _db):
    sql = "select * from tbl_30min t where stock_id='%s' and ( pub_date='2016-07-26' or pub_date= '2016-07-25' )\
           order by pub_date desc, pub_time desc limit 10" % _stock_id

    df = pd.read_sql_query(sql, _db);

    return df


def choose_init_one(_stock_id, _db):

    begin = get_micro_second()

    df = get_df_from_db1(_stock_id, _db)

    diff = get_micro_second() - begin
    log_debug("get_df_from_db costs %d", diff)

    if df is None:
        print "stock %s no data, exit" % _stock_id
        return

    df = df.set_index(['pub_date', 'pub_time'])
    df = df.sort_index(ascending=True)

    global g_map
    g_map[_stock_id] = df

    log_debug("df: \n%s", df.tail())

    return

def choose_init(_stocks, _db):

    for row_index, row in _stocks.iterrows():
        log_debug("---index1 is %s",  row_index)
        stock_id = row_index
        choose_init_one(stock_id, _db)
        break

    return


def choose_merge_one(_stock_id, _db):

    begin = get_micro_second()

    df = get_df_from_db2(_stock_id, _db)

    diff = get_micro_second() - begin
    log_debug("get_df_from_db costs %d", diff)

    if df is None:
        print "stock %s no data, exit" % _stock_id
        return

    df = df.set_index(['pub_date', 'pub_time'])
    df = df.sort_index(ascending=True)

    log_debug("df-merge1: \n%s", df)

    global g_map
    df_prev = g_map[_stock_id]

    log_debug("df-merge2: \n%s", df_prev)

    #df = pd.merge(df, df_prev) # bad
    #df = pd.concat([df, df_prev]) #bad
    #df = pd.merge(df, df_prev, how='inner', on=['pub_date', 'pub_time']) # bad
    df = pd.concat([df, df_prev]).drop_duplicates().sort_index(ascending=True) # nice, 2016/7/26

    log_debug("df-merge: \n%s", df)
    g_map[_stock_id] = df

    return

def choose_loop(_stocks, _db):

    for row_index, row in _stocks.iterrows():
        log_debug("---index2 is %s",  row_index)
        stock_id = row_index
        choose_merge_one(stock_id, _db)
        break

    return


def work():
    db = db_init()

    #  compute and update
    stocks = get_stock_list_df_db(db)
    log_debug("get stock list: %s",  stocks)

    choose_init(stocks, db)

    log_debug("init succeeds")

    choose_loop(stocks, db)
    log_debug("loop accomplished")

    db_end(db)


#######################################################################

def main():
    print "let's begin here!"

    sailog_set("choose.log")
    work()

    log_debug("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    for item in sorted(g_map.keys()):
        log_debug("key: %s", item)
        df = g_map[item]
        log_debug("df2: \n%s", df)

    print "main ends, bye!"
    return

main()
exit()
print "can't arrive here"

#######################################################################

# choose.py
