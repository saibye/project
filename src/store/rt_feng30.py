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


def rt_feng_df_to_db(_stock_id, _df, _db):
    dt = get_today()
    tm = get_time()

    for row_index, row in _df.iterrows():
        date2, time2 = row_index.split()
        sql = row_to_sql(_stock_id, row_index, row, dt, tm)
        sql_to_db_nolog(sql, _db)

    return


def rt_feng_one(_stock_id, _db):
    log_info("rt_feng_one begin")

    # today 30min data
    minute     = '30'
    start_date = get_date_by(0)
    end_date   = get_date_by(1)
    log_debug("stock: %s, %s, %s", _stock_id, start_date, end_date)

    begin = get_micro_second()

    df = ts.get_hist_data(_stock_id, ktype=minute, start=start_date, end=end_date)

    # calc cost time
    diff = get_micro_second() - begin;
    log_info("get_hist_data costs %d us", diff)

    if df is None :
        log_error("warn: stock %s is None, next", _stock_id)
        return -1

    if df.empty:
        log_error("warn: stock %s is empty, next", _stock_id)
        return -2

    #log_debug("df: \n%s", df)

    begin = get_micro_second()

    # import dataframe to db
    rt_feng_df_to_db(_stock_id, df, _db)

    diff = get_micro_second() - begin;
    log_info("df_to_db costs %d us", diff)

    log_info("rt_feng_one end")

    return 


def rt_save(_stocks, _db):

    for row_index, row in _stocks.iterrows():
        #log_debug("stock: %s",  row_index)
        rt_feng_one(row_index, _db)

    return


"""
从10点开始，每半小时执行一次
"""

def rt_timer(_stocks, _db):
    end_time = '16:00:00'
    time_map = {'10:05:00':0, '10:35:00':0,
        '11:05:00':0, '11:35:00':0,
        '13:35:00':0, '14:05:00':0,
        '14:35:00':0, '15:05:00':0}

    """ -- test data
    time_map = {'10:05:00':0, '10:35:00':0,
        '11:05:00':0, '11:35:00':0,
        '13:35:00':0, '14:05:00':0,
        '14:35:00':0, '15:05:00':0,
        '15:32:00':0, '15:33:00':0}
    """

    counter = 0

    while 1:
        counter = counter + 1
        to_run = check_time_to_run(time_map)

        if to_run:
            log_info(">>>>>let's run here")

            begin = get_micro_second()

            # step2: insert to db
            rt_save(_stocks, _db)

            diff = get_micro_second() - begin;
            log_info("rt_save costs %d us", diff)

        else:
            # log every 10 minutes(20s * 30).
            if counter == 30:
                log_debug(">>>>>sorry, no need to run")
                counter = 0

        curr = get_time()
        if curr >= end_time:
            log_info("'%s' means end today", curr)
            break

        time.sleep(20)

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
    sailog_set("rt_feng30.log")

    log_info("let's begin here!")

    work()

    log_info("main ends, bye!")
    return

main()
exit()
print "can't arrive here"

#######################################################################


# rt_feng30.py
