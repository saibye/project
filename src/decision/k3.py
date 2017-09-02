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
from sairef  import *
from saitech import *

#######################################################################
# 
#######################################################################


# 
def thrive():
    if ref_len() < 7:
        log_info("data not enough: 7")
        return -1



    rate1 = (ref_close(3) - ref_close(4)) / ref_close(4) * 100  # day1 涨幅
    zt1   = (ref_close(3) - ref_open(3))  / ref_close(4) * 100  # day1 柱体
    vol1  = ref_vol(3)                                          # day1 成交量

    rate2 = (ref_close(2) - ref_close(3)) / ref_close(3) * 100  # day2 涨幅
    zt2   = (ref_close(2) - ref_open(2))  / ref_close(3) * 100  # day2 柱体
    vol2  = ref_vol(2)                                          # day2 成交量

    rate3 = (ref_close(1) - ref_close(2)) / ref_close(2) * 100  # day3 涨幅
    zt3   = (ref_close(1) - ref_open(1))  / ref_close(2) * 100  # day3 柱体
    vol3  = ref_vol(1)                                          # day3 成交量

    rate4 = (ref_close(0) - ref_close(1)) / ref_close(1) * 100  # day4 涨幅
    zt4   = (ref_close(0) - ref_open(0))  / ref_close(1) * 100  # day4 柱体
    vol4  = ref_vol(0)                                          # day4 成交量


    # rule1: 5
    # 1. 涨幅递增
    # 2. 成交量递增
    # 3. 阳柱递增
    rule1_sub1 = zt1 < 0 and zt2 < 0 and zt3 < 0
    rule1_sub2 = ref_high(3) > ref_high(2) and ref_high(2) > ref_high(1)
    rule1_sub3 = ref_close(0) > ref_high(1) and ref_vol(0) and ref_vol(1)
    rule1_sub4 = (ref_high(4)  - ref_low(6) ) / ref_low(6) * 100 > 15

    rule1 = (rule1_sub1 and rule1_sub2 and rule1_sub3 and rule1_sub4)


    if rule1:
        rv = 1
        log_debug("nice: three-line rule1")

        log_debug("1-rate:%.3f, zt:%.3f, vol: %.3f", rate1, zt1, vol1)
        log_debug("2-rate:%.3f, zt:%.3f, vol: %.3f", rate2, zt2, vol2)
        log_debug("3-rate:%.3f, zt:%.3f, vol: %.3f", rate3, zt3, vol3)
        log_debug("4-rate:%.3f, zt:%.3f, vol: %.3f", rate4, zt4, vol4)
    else:
        rv = 0
        # log_debug("not match")

    return rv


def work_one(_trade_date, _db):

    good = ""

    log_info("date: %s", _trade_date)
    ref_set_date(_trade_date)

    rv = ref_init(_db)
    if rv != 0:
        log_error("error: ref_init")
        return rv

    begin = get_micro_second()

    stocks = ref_get_list()
    rownum = 0
    content1 = "" # 
    for s_index, s_val in stocks.iteritems():
        rownum = rownum + 1
        stock_id = s_index
        log_info("%s -- %s", _trade_date, stock_id)
        rv = ref_set(stock_id)
        if rv < 0:
            log_error("error: ref_set: %s", stock_id)
            return rv
        elif rv < 5:
            log_error("warn: %s small %d", stock_id, rv)
            continue


        rv = thrive()
        if rv == 1:
            one = "%s -- %s\n" % (_trade_date, stock_id)
            one += good
            one += get_basic_info_all(stock_id, _db)
            one += "--------------------------------\n"
            log_info("nice1-thrive:\n%s", one)
            content1 += one
        else:
            # log_debug("wait...")
            pass

    log_info("%d costs %d us", rownum, get_micro_second() - begin)

    mailed = 0

    if len(content1) > 0:
        subject = "thrive: %s" % (_trade_date)
        log_info(subject)
        log_info("mail\n%s", content1)
        if sai_is_product_mode():
            mailed = 1
            saimail_dev(subject,  content1)
    else:
        log_info("sorry1: %s", _trade_date)

    if sai_is_product_mode():
        if mailed == 0:
            subject = "No Good K: %s" % (_trade_date)

    return


def regression(_db):

    # 603357
    max_date = "2017-08-30"
    days = 30

    log_info("regress")

    date_df = get_recent_pub_date(max_date, days, _db)
    if date_df is None:
        log_error("error: get_recent_pub_date failure")
        return -1
    else:
        date_df.set_index("pub_date", inplace=True)

    for row_index, row in date_df.iterrows():
        trade_date = row_index
        log_debug("[%s]------------------", trade_date)
        work_one(trade_date, _db)

    return 0


def work():
    db = db_init()

    if sai_is_product_mode():
        trade_date = get_date_by(0)
        trade_date = "2017-08-10"
        work_one(trade_date, db)
    else:
        regression(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("k3.log")

    log_info("let's begin here!")

    if sai_is_product_mode():
        # check holiday
        if today_is_weekend():
            log_info("today is weekend, exit")
        else:
            log_info("today is workday, come on")
            work()
    else:
        log_debug("test mode")
        work()

    log_info("main ends, bye!")
    return

main()
exit()

#######################################################################


# k3.py
