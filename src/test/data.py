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
from saimail import *
from sairank import *
from saitu   import *


"""
"""
#######################################################################


def data_15min(_stock_id, _db):
    df = None

    try:
        df = ts.get_k_data(_stock_id, ktype='15', autype='qfq')
    except Exception:
        log_error("warn: %s get_sina_dd exception!", _stock_id)
        time.sleep(5)
        return -1

    if df is None :
        log_error("warn: stock %s is None, next", _stock_id)
        return -2

    if df.empty:
        log_error("warn: stock %s is empty, next", _stock_id)
        return -3

    log_info("15min: length: %d", len(df))
    log_info("15min: df:\n%s", df)
 
    return 0


def data_day(_stock_id, _db):
    df = None

    start_date = "2017-08-31"
    end_date   = get_date_by(0)

    try:
        df = ts.get_k_data(_stock_id, autype='qfq', start=start_date, end=end_date)
    except Exception:
        log_error("warn: %s get_sina_dd exception!", _stock_id)
        time.sleep(5)
        return -1

    if df is None :
        log_error("warn: stock %s is None, next", _stock_id)
        return -2

    if df.empty:
        log_error("warn: stock %s is empty, next", _stock_id)
        return -3

    log_info("day: length: %d", len(df))
    log_info("day: df:\n%s", df)
 
    return 0



"""
从9点半开始
"""

def rt_timer(_stock_id, _db):

    end_time  = '15:05:00'
    lun_time1 = '11:35:00'
    lun_time2 = '13:00:00'


    counter  = 0
    while 1:
        g_good_list  = []
        g_good_list2 = []
        g_good_list3 = []
        counter = counter + 1

        curr = get_time()

        # 中午休息
        if curr >= lun_time1 and curr <= lun_time2:
            log_info("'%s' means noon time", curr)
            time.sleep(300)
            continue

        log_info(">>>>>let's run here")

        rv = data_15min(_stock_id, _db)

        rv = data_day(_stock_id, _db)


        # 当日结束
        curr = get_time()
        if curr >= end_time:
            log_info("'%s' means end today", curr)
            break

        # 降低频率
        time.sleep(300)

    return


def work():
    db = db_init()

    stock_id = "000002"

    rt_timer(stock_id, db)

    db_end(db)


#######################################################################

def main():
    sailog_set("data.log")

    log_info("let's begin here!")

    if sai_is_product_mode():
        if today_is_weekend():
            log_info("today is weekend, exit")
        else:
            log_info("today is workday, come on")
            work()
    else:
        log_info("test mode, come on")
        work()


    log_info("main ends, bye!")
    return

main()

#######################################################################

# data.py
