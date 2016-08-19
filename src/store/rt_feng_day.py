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

def rt_feng_row_to_sql(_stock_id, _pub_date, _row, _dt, _tm):


    # 前复权
    sql = "insert into tbl_day \
(pub_date, pub_time, stock_id, stock_loc, \
open_price, high_price, close_price, low_price, \
deal_total_count, deal_total_amount, \
inst_date, inst_time) \
values ('%s', '22:22:22', '%s', '%s',  \
'%.02f', '%.2f', '%.2f', '%.2f', \
'%.2f', '%.2f', \
'%s', '%s')" % \
    (_pub_date, _stock_id, 'cn', 
     _row.loc['open'], _row.loc['high'], _row.loc['close'], _row.loc['low'],
     _row.loc['volume'], _row.loc['amount'],
     _dt, _tm)

    #  不复权
    sql = "insert into tbl_day_orig \
(pub_date, pub_time, stock_id, stock_loc, \
open_price, high_price, close_price, low_price, \
deal_total_count, deal_total_amount, \
inst_date, inst_time) \
values ('%s', '22:22:22', '%s', '%s',  \
'%.02f', '%.2f', '%.2f', '%.2f', \
'%.2f', '%.2f', \
'%s', '%s')" % \
    (_pub_date, _stock_id, 'cn', 
     _row.loc['open'], _row.loc['high'], _row.loc['close'], _row.loc['low'],
     _row.loc['volume'], _row.loc['amount'],
     _dt, _tm)

    return sql

def rt_feng_day_to_db(_stock_id, _df, _db):
    dt = get_today()
    tm = get_time()

    for row_index, row in _df.iterrows():
        pub_date = row_index
        sql = rt_feng_row_to_sql(_stock_id, pub_date, row, dt, tm)
        sql_to_db_nolog(sql, _db)

    return


def rt_feng_one(_stock_id, _db):
    log_info("rt_feng_one begin")

    # today 30min data
    """
    minute     = '30'
    start_date = get_date_by(0)
    end_date   = get_date_by(1)
    log_debug("stock: %s, %s, %s", _stock_id, start_date, end_date)
    df = ts.get_hist_data(_stock_id, ktype=minute, start=start_date, end=end_date)
    """

    begin = get_micro_second()

    df = ts.get_h_data(_stock_id, autype=None)
    # df = ts.get_h_data(_stock_id)

    # calc cost time
    log_info("get_h_data costs %d us", get_micro_second() - begin)

    if df is None :
        log_error("warn: stock %s is None, next", _stock_id)
        return -1

    if df.empty:
        log_error("warn: stock %s is empty, next", _stock_id)
        return -2

    # log_debug("df: \n%s", df)

    """
    """
    begin = get_micro_second()

    # import dataframe to db
    rt_feng_day_to_db(_stock_id, df, _db)

    log_info("rt_feng_day_to_db costs %d us", get_micro_second() - begin)

    log_info("rt_feng_one end")

    return 


def rt_save(_stocks, _db):

    for row_index, row in _stocks.iterrows():
        stock_id = row_index
        log_debug("stock: %s", stock_id)
        rt_feng_one(stock_id, _db)
        """
        break for debug
        break
        """

    return


"""
当日收市，记录
"""

def rt_timer(_stocks, _db):
    end_time = '16:00:00'

    counter = 0

    while 1:
        counter = counter + 1

        curr = get_time()

        if curr >= end_time:

            log_info("'%s' means end today", curr)

            begin = get_micro_second()

            # insert to db
            rt_save(_stocks, _db)

            log_info("rt_save costs %d us", get_micro_second() - begin)

            # bye today
            break

        else:
            # 10 minute
            log_info("~~huhu~~")
            time.sleep(600)

    return




def work():
    db = db_init()

    # step1: get from web
    stocks = get_stock_list_df_tu()

    # step2: record to db at some time
    rt_timer(stocks, db)


    # step3:
    # TODO: 复权数据 rehabilitation

    db_end(db)


#######################################################################

def main():
    sailog_set("rt_feng_day0.log")

    log_info("let's begin here!")

    work()

    log_info("main ends, bye!")
    return

main()
exit()
print "can't arrive here"

#######################################################################


# rt_feng_day.py
