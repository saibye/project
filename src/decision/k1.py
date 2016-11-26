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

#######################################################################
# 不需要macd等,  所以只使用tbl_day表 2016/11/26
#######################################################################

# 1. 生产模式； 0.测试模式
g_product_mode = 0
g_product_mode = 1


def citou():
    rate1 = (ref_close(1) - ref_close(2)) / ref_close(2) * 100
    rate2 = (ref_close(0) - ref_close(1)) / ref_close(1) * 100
    mid   = (ref_open(1)  + ref_close(1)) / 2

    # if rate1 <= -5 and rate2 >= 5 and ref_open(0) < ref_low(1) and ref_close(0) > mid: # 2016-11-20
    if rate1 <= -5 and rate2 >= 4 and ref_open(0) <= ref_close(1) and ref_close(0) >= mid:
        rv = 1
        # log_debug("nice: citou")
        log_debug("rate1: %.2f", rate1)
        log_debug("rate2: %.2f", rate2)
        log_debug("mid:   %.2f", mid)
        log_debug("low:   %.2f", ref_low(1))
        log_debug("close: %.2f", ref_close(0))
        log_debug("open:  %.2f", ref_open(0))
    else:
        rv = 0
        # log_debug("not match")

    return rv


def qiming():
    rate1 = (ref_close(2) - ref_close(3)) / ref_close(3) * 100  # 第一天 前天
    rate3 = (ref_close(0) - ref_close(1)) / ref_close(1) * 100  # 第三天 today
    md1   = (ref_open(2)*2 + ref_close(2))/ 3
    zt1   = (ref_close(2) - ref_open(2)) / ref_close(3) * 100 # 第一天
    zt2   = (ref_close(1) - ref_open(1)) / ref_close(2) * 100 # 第二天
    zt3   = (ref_close(0) - ref_open(0)) / ref_close(1) * 100 # 第三天 today


    # 1. 前天大幅下跌
    # 2. 昨天低开
    # 3. 今天高开
    # 4. 今天收盘超过前天2/3
    if rate1 <= -4 and rate3 >= 4\
                and ref_open(1) < ref_close(2) \
                and ref_open(0)*1.01 > ref_close(1) \
                and ref_close(0) >= md1 \
                and zt1 <= -4 \
                and zt3 >=  3 \
                and abs(zt2) <= 5:
        rv = 1
        log_debug("nice: qiming")

        log_debug("rate1: %.2f pk %.2f => %.2f", ref_close(2), ref_close(3), rate1)
        log_debug("rate3: %.2f pk %.2f => %.2f", ref_close(0), ref_close(1), rate3)
        log_debug("%.2f <  %.2f", ref_open(1), ref_close(2))
        log_debug("%.2f >  %.2f", ref_open(0), ref_close(1))
        log_debug("%.2f >= %.2f", ref_close(0), md1)
        log_debug("%.2f , %.2f , %.2f", zt1, zt2, zt3)
    else:
        rv = 0
        # log_debug("not match")

    return rv


def work_one(_trade_date, _db):
    global g_product_mode

    log_info("date: %s", _trade_date)
    ref_set_date(_trade_date)

    rv = ref_init(_db)
    if rv != 0:
        log_error("error: ref_init")
        return rv

    begin = get_micro_second()

    stocks = ref_get_list()
    rownum = 0
    content1 = "" # citou
    content2 = "" # qiming
    for s_index, s_val in stocks.iteritems():
        rownum = rownum + 1
        stock_id = s_index
        log_debug("%s-%s", stock_id, _trade_date)
        rv = ref_set(stock_id)
        if rv < 0:
            log_error("error: ref_set: %s", stock_id)
            return rv
        elif rv < 5:
            log_error("warn: small %d", rv)
            continue

        rv = citou()
        if rv == 1:
            one = "%s -- %s\n" % (_trade_date, stock_id)
            log_info("nice1: %s", one)
            content1 += one
        else:
            # log_debug("wait...")
            pass

        rv = qiming()
        if rv == 1:
            two = "%s -- %s\n" % (_trade_date, stock_id)
            log_info("nice2: %s", two)
            content2 += two
        else:
            # log_debug("wait...")
            pass

    log_info("%d costs %d us", rownum, get_micro_second() - begin)

    mailed = 0
    if len(content1) > 0:
        subject = "citou: %s" % (_trade_date)
        log_info(subject)
        log_info("\n%s", content1)
        if g_product_mode == 1:
            mailed = 1
            saimail(subject,  content1)

    else:
        log_info("sorry1: %s", _trade_date)

    if len(content2) > 0:
        subject = "qiming: %s" % (_trade_date)
        log_info(subject)
        log_info("\n%s", content2)
        if g_product_mode == 1:
            mailed = 1
            saimail(subject,  content2)
    else:
        log_info("sorry2: %s", _trade_date)


    if g_product_mode == 1:
        if mailed == 0:
            subject = "No Good K: %s" % (_trade_date)
            saimail(subject, "the last chance in your life?")

    return


def regression(_db):

    max_date = "2016-11-08"
    max_date = get_date_by(0)
    max_date = "2016-11-04"
    days = 10
    max_date = "2016-11-18"
    days = 1

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
    global g_product_mode
    db = db_init()

    if g_product_mode == 1:
        # trade_date = "2016-08-02"
        trade_date = get_date_by(0)
        work_one(trade_date, db)
    else:
        regression(db)

    db_end(db)


#######################################################################

def main():
    global g_product_mode
    sailog_set("k1.log")

    log_info("let's begin here!")

    if g_product_mode == 1:
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


# k1.py
