#!/usr/bin/env python
# -*- encoding: utf8 -*-

import tushare as ts
import pandas as pd
import numpy as np

from saiutil import *
from saidb   import *
from saisql  import *
from saicalc import *
from sailog  import *

#######################################################################


def sina_row_to_sql(_stock_id, _row_index, _row, _dt, _tm):
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

def sina_df_to_db(_stock_id, _df, _db):
    print "i'm importing %s" % _stock_id

    dt = get_today()
    tm = get_time()

    for row_index, row in _df.iterrows():
        #print "-----------index is ",  row_index
        date2, time2 = row_index.split()
        #print ("date: %s, time: %s" % (date2, time2))
        #print "close is ", row.loc['close'], ", ma5 is ", row.loc['ma5'], ", change: ", row['p_change']
        sql = sina_row_to_sql(_stock_id, row_index, row, dt, tm)
        #print sql
        sql_to_db(sql, _db)

    return

def work_one_more(_stock_list, _db):
    log_info("work_one_more begin: \n%s", _stock_list)

    begin = get_micro_second()

    df = ts.get_realtime_quotes(_stock_list)
    if df is None :
        log_error("stock %s no data, next", _stock_list)
        return

    diff = get_micro_second() - begin;
    log_debug("tu costs %d us", diff)

    log_debug("df: \n%s", df)

    # DO NOT clear previous data

    # import dataframe to db
    #sina_df_to_db(_stock_list, df, _db)

    log_info("work_one_more end")

    return 

def import_real(_stocks, _db):

    list1 = []
    group = 100
    for row_index, row in _stocks.iterrows():
        #log_debug("---index is %s", row_index)
        list1.append(row_index)
        if len(list1) == group:
            work_one_more(list1, _db)
            break

    return


def work():
    db = db_init()

    # step1: get from web
    stocks = get_stock_list_df_tu()

    # step2: insert to db
    import_real(stocks, db)

    # test data
    #stock_id = '300028'
    #work_one_more(stock_id, db)

    # step3:
    # TODO: 复权数据 rehabilitation

    db_end(db)


#######################################################################

def main():
    sailog_set("realtime.log")

    log_info("let's begin here!")

    work()

    log_info("main ends, bye!")
    return

main()
exit()
print "can't arrive here"

#######################################################################


# rt_sina.py
