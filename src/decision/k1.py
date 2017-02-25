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

# 超级模式  2017-2-11
# 002346 -- 2016-12-26
# 300311 -- 2017-1-17
# 600698 -- 2017-1-17
def citou2():
    rate1 = (ref_close(1) - ref_close(2)) / ref_close(2) * 100
    rate2 = (ref_close(0) - ref_close(1)) / ref_close(1) * 100

    if rate1 <= -8 and rate2 >= 8 and ref_open(0) < ref_low(1) and ref_close(0) > ref_high(1):
        rv = 1
        # log_debug("nice: citou2")
        log_debug("rate1: %.2f", rate1)
        log_debug("rate2: %.2f", rate2)
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


# 要求len >= 6
def up_sanfa():
    if ref_len() < 6:
        log_info("data not enough: 6")
        return -1
    rate1 = (ref_close(4) - ref_close(5)) / ref_close(5) * 100  # day1 涨幅
    zt1   = (ref_close(4) - ref_open(4))  / ref_close(5) * 100  # day1 柱体

    rate2 = (ref_close(3) - ref_close(4)) / ref_close(4) * 100  # day2
    md2   = (ref_close(3) + ref_open(3))/ 2
    rate3 = (ref_close(2) - ref_close(3)) / ref_close(3) * 100  # day3
    md3   = (ref_close(2) + ref_open(2))/ 2
    rate4 = (ref_close(1) - ref_close(2)) / ref_close(2) * 100  # day4
    md4   = (ref_close(1) + ref_open(1))/ 2

    rate5 = (ref_close(0) - ref_close(1)) / ref_close(1) * 100  # day5 涨幅
    zt5   = (ref_close(0) - ref_open(0))  / ref_close(1) * 100  # day5 柱体


    # 1. day1 大涨
    # 2. day2,3,4 连跌3天
    # 3. day5 大涨
    if rate1 >=2 and zt1 >= 3 \
                and md2 <= ref_high(4)  and abs(rate2) <= 0.8 \
                and md3 <= md2          and abs(rate3) <= 0.8 and ref_close(2) < ref_close(3) \
                and md4 <= md3          and abs(rate4) <= 0.8 and ref_close(1) < ref_close(2) \
                and ref_open(0)  >= ref_open(4) \
                and ref_close(0) >= ref_close(4) \
                and ref_open(0)  <= ref_close(1) \
                and rate5 >= 2 and zt5 >= 3:
        rv = 1
        log_debug("nice: sanfa")

        log_debug("rate1: %.2f pk %.2f => %.2f", ref_close(4), ref_close(5), rate1)
        log_debug("rate5: %.2f pk %.2f => %.2f", ref_close(0), ref_close(1), rate5)
        log_debug("%.2f , %.2f , %.2f", md2, md3, md4)
    else:
        rv = 0
        # log_debug("not match")

    return rv


def work_one(_trade_date, _db):

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
    content3 = "" # sanfa 2016-12-3
    for s_index, s_val in stocks.iteritems():
        rownum = rownum + 1
        stock_id = s_index
        # log_debug("%s-%s", stock_id, _trade_date)
        rv = ref_set(stock_id)
        if rv < 0:
            log_error("error: ref_set: %s", stock_id)
            return rv
        elif rv < 5:
            log_error("warn: %s small %d", stock_id, rv)
            continue

        # rv = citou()  # citou  
        rv = citou2()
        if rv == 1:
            one  = "%s -- %s\n" % (_trade_date, stock_id)
            one += get_basic_info_all(stock_id, _db)
            log_info("nice1: %s", one)
            content1 += one
        else:
            # log_debug("wait...")
            pass

        rv = qiming()
        if rv == 1:
            two = "%s -- %s\n" % (_trade_date, stock_id)
            two += get_basic_info_all(stock_id, _db)
            log_info("nice2: %s", two)
            content2 += two
        else:
            # log_debug("wait...")
            pass

        rv = up_sanfa()
        if rv == 1:
            three = "%s -- %s\n" % (_trade_date, stock_id)
            three += get_basic_info_all(stock_id, _db)
            log_info("nice3: %s", three)
            content3 += three
        else:
            # log_debug("wait...")
            pass

    log_info("%d costs %d us", rownum, get_micro_second() - begin)

    mailed = 0
    if len(content1) > 0:
        subject = "##citou: %s" % (_trade_date)
        log_info(subject)
        log_info("\n%s", content1)
        if sai_is_product_mode():
            mailed = 1
            saimail(subject,  content1)

    else:
        log_info("sorry1: %s", _trade_date)

    if len(content2) > 0:
        subject = "qiming: %s" % (_trade_date)
        log_info(subject)
        log_info("\n%s", content2)
        if sai_is_product_mode():
            mailed = 1
            saimail(subject,  content2)
    else:
        log_info("sorry2: %s", _trade_date)

    if len(content3) > 0:
        subject = "sanfa: %s" % (_trade_date)
        warning = "需要均线发散!!!\n"
        content3 = warning + content3
        log_info(subject)
        log_info("\n%s", content3)
        if sai_is_product_mode():
            mailed = 1
            saimail(subject,  content3)
    else:
        log_info("sorry3: %s", _trade_date)


    if sai_is_product_mode():
        if mailed == 0:
            subject = "No Good K: %s" % (_trade_date)
            # saimail(subject, "the last chance in your life?")

    return


def regression(_db):

    max_date = "2016-11-08"
    max_date = get_date_by(0)
    max_date = "2016-11-04"
    days = 10
    max_date = "2016-11-25"
    days = 1
    max_date = "2017-02-11"
    days = 60
    max_date = "2016-12-31"
    days = 10

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
        trade_date = "2016-12-26"   # 002346
        trade_date = get_date_by(0)
        work_one(trade_date, db)
    else:
        regression(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("k1.log")

    log_info("let's begin here!")

    if sai_is_product_mode():
        # check holiday
        if today_is_weekend():
            log_info("today is weekend, exit")
            # work() # XXX
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
