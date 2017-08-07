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


# 002695 
# 1. 涨幅递增
# 2. 成交量递增
# 3. 阳柱递增
# 4. 收复MA20 -- TODO
def up_accum():
    if ref_len() < 6:
        log_info("data not enough: 6")
        return -1

    rate1 = (ref_close(4) - ref_close(5)) / ref_close(5) * 100  # day1 涨幅
    zt1   = (ref_close(4) - ref_open(4))  / ref_close(5) * 100  # day1 柱体
    vol1  = ref_vol(4)

    rate2 = (ref_close(3) - ref_close(4)) / ref_close(4) * 100  # day2 涨幅
    zt2   = (ref_close(3) - ref_open(3))  / ref_close(4) * 100  # day2 柱体
    vol2  = ref_vol(3)                                          # day2 成交量

    rate3 = (ref_close(2) - ref_close(3)) / ref_close(3) * 100  # day3 涨幅
    zt3   = (ref_close(2) - ref_open(2))  / ref_close(3) * 100  # day3 柱体
    vol3  = ref_vol(2)                                          # day3 成交量

    rate4 = (ref_close(1) - ref_close(2)) / ref_close(2) * 100  # day4 涨幅
    zt4   = (ref_close(1) - ref_open(1))  / ref_close(2) * 100  # day4 柱体
    vol4  = ref_vol(1)                                          # day4 成交量

    rate5 = (ref_close(0) - ref_close(1)) / ref_close(1) * 100  # day5 涨幅
    zt5   = (ref_close(0) - ref_open(0))  / ref_close(1) * 100  # day5 柱体
    vol5  = ref_vol(0)                                          # day5 成交量


    # rule1: 5
    # 1. 涨幅递增
    # 2. 成交量递增
    # 3. 阳柱递增
    rule1_sub1 = rate5>rate4 and rate4>rate3 and rate3>rate2 and rate2 > rate1
    rule1_sub2 = vol5>vol4   and vol4>vol3   and vol3>vol2   and vol2 > vol1
    rule1_sub3 = zt5>zt4     and zt4>zt3     and zt3>zt2     and zt2 > zt1

    rule1 = (rule1_sub1 and rule1_sub2 and rule1_sub3)

    # rule2: 4
    # 1. 涨幅递增
    # 2. 成交量递增
    # 3. 阳柱递增
    rule2 = False
    rule2_sub1 = rate5>rate4 and rate4>rate3 and rate3>rate2
    rule2_sub2 = vol5>vol4   and vol4>vol3   and vol3>vol2
    rule2_sub3 = zt5>zt4     and zt4>zt3     and zt3>zt2
    rule2 = False and (rule2_sub1 and rule2_sub2 and rule2_sub3)

    rule3 = False

    if rule1:
        rv = 1
        log_debug("nice: up-accumulate rule1")

        log_debug("1-rate:%.3f, zt:%.3f, vol: %.3f", rate1, zt1, vol1)
        log_debug("2-rate:%.3f, zt:%.3f, vol: %.3f", rate2, zt2, vol2)
        log_debug("3-rate:%.3f, zt:%.3f, vol: %.3f", rate3, zt3, vol3)
        log_debug("4-rate:%.3f, zt:%.3f, vol: %.3f", rate4, zt4, vol4)
        log_debug("5-rate:%.3f, zt:%.3f, vol: %.3f", rate5, zt5, vol5)
    elif rule2:
        rv = 2
        log_debug("nice: up-accumulate rule2")

        log_debug("1-rate:%.3f, zt:%.3f, vol: %.3f", rate1, zt1, vol1)
        log_debug("2-rate:%.3f, zt:%.3f, vol: %.3f", rate2, zt2, vol2)
        log_debug("3-rate:%.3f, zt:%.3f, vol: %.3f", rate3, zt3, vol3)
        log_debug("4-rate:%.3f, zt:%.3f, vol: %.3f", rate4, zt4, vol4)
        log_debug("5-rate:%.3f, zt:%.3f, vol: %.3f", rate5, zt5, vol5)
    else:
        rv = 0
        # log_debug("not match")

    return rv


# 2017-6-16
# 000025
# 1. 三个涨停
# 2. 第四天十字
def up_fly():
    if ref_len() < 6:
        log_info("data not enough: 6")
        return -1

    # 连续5天数据
    # 可以取最近4天，即不用rate1
    rate1 = (ref_close(4) - ref_close(5)) / ref_close(5) * 100  # day1 涨幅
    zt1   = (ref_close(4) - ref_open(4))  / ref_close(5) * 100  # day1 柱体
    vol1  = ref_vol(4)

    rate2 = (ref_close(3) - ref_close(4)) / ref_close(4) * 100  # day2 涨幅
    zt2   = (ref_close(3) - ref_open(3))  / ref_close(4) * 100  # day2 柱体
    vol2  = ref_vol(3)                                          # day2 成交量

    rate3 = (ref_close(2) - ref_close(3)) / ref_close(3) * 100  # day3 涨幅
    zt3   = (ref_close(2) - ref_open(2))  / ref_close(3) * 100  # day3 柱体
    vol3  = ref_vol(2)                                          # day3 成交量

    rate4 = (ref_close(1) - ref_close(2)) / ref_close(2) * 100  # day4 涨幅
    zt4   = (ref_close(1) - ref_open(1))  / ref_close(2) * 100  # day4 柱体
    vol4  = ref_vol(1)                                          # day4 成交量

    rate5 = (ref_close(0) - ref_close(1)) / ref_close(1) * 100  # day5 涨幅
    zt5   = (ref_close(0) - ref_open(0))  / ref_close(1) * 100  # day5 柱体
    vol5  = ref_vol(0)                                          # day5 成交量


    # rule1: 5
    # 1.
    # 2.
    rule1_sub1 = rate4 > 9.8 and rate3 > 9.8 and rate2 > 9.8
    rule1_sub2 = rate5 > 1 and abs(zt5) < 1
    rule1_sub3 = zt2 > 9.8 and zt3 > 9.8 and zt4 > 6.8
    rule1_sub4 = vol4 > vol3 and vol3 > vol2 and vol2 > vol1

    rule1 = rule1_sub1 and rule1_sub2 and rule1_sub3 and rule1_sub4

    # rule2: 4
    rule2 = False

    rule3 = False

    if rule1:
        rv = 1
        log_debug("nice: up-fly rule1")

        log_debug("1-rate:%.3f, zt:%.3f, vol: %.3f", rate1, zt1, vol1)
        log_debug("2-rate:%.3f, zt:%.3f, vol: %.3f", rate2, zt2, vol2)
        log_debug("3-rate:%.3f, zt:%.3f, vol: %.3f", rate3, zt3, vol3)
        log_debug("4-rate:%.3f, zt:%.3f, vol: %.3f", rate4, zt4, vol4)
        log_debug("5-rate:%.3f, zt:%.3f, vol: %.3f", rate5, zt5, vol5)
        log_debug("zt5: %.3f", zt5)
    elif rule2:
        rv = 2
        log_debug("nice: up-fly rule2")

        log_debug("rate:%.3f, vol:%.3f, zt: %.3f", rate1, zt1, vol1)
        log_debug("rate:%.3f, vol:%.3f, zt: %.3f", rate2, zt2, vol2)
        log_debug("rate:%.3f, vol:%.3f, zt: %.3f", rate3, zt3, vol3)
        log_debug("rate:%.3f, vol:%.3f, zt: %.3f", rate4, zt4, vol4)
        log_debug("rate:%.3f, vol:%.3f, zt: %.3f", rate5, zt5, vol5)
    else:
        rv = 0
        # log_debug("not match")

    return rv


# 2017-6-16
# 300506
# 1. 一串白武士
# 2. 收复ma20
def up_warrior():
    if ref_len() < 6:
        log_info("data not enough: 6")
        return -1

    # 连续5天数据
    # 可以取最近4天，即不用rate1
    rate1 = (ref_close(4) - ref_close(5)) / ref_close(5) * 100  # day1 涨幅
    zt1   = (ref_close(4) - ref_open(4))  / ref_close(5) * 100  # day1 柱体
    vol1  = ref_vol(4)

    rate2 = (ref_close(3) - ref_close(4)) / ref_close(4) * 100  # day2 涨幅
    zt2   = (ref_close(3) - ref_open(3))  / ref_close(4) * 100  # day2 柱体
    vol2  = ref_vol(3)                                          # day2 成交量

    rate3 = (ref_close(2) - ref_close(3)) / ref_close(3) * 100  # day3 涨幅
    zt3   = (ref_close(2) - ref_open(2))  / ref_close(3) * 100  # day3 柱体
    vol3  = ref_vol(2)                                          # day3 成交量

    rate4 = (ref_close(1) - ref_close(2)) / ref_close(2) * 100  # day4 涨幅
    zt4   = (ref_close(1) - ref_open(1))  / ref_close(2) * 100  # day4 柱体
    vol4  = ref_vol(1)                                          # day4 成交量

    rate5 = (ref_close(0) - ref_close(1)) / ref_close(1) * 100  # day5 涨幅
    zt5   = (ref_close(0) - ref_open(0))  / ref_close(1) * 100  # day5 柱体
    vol5  = ref_vol(0)                                          # day5 成交量

    log_debug("1-rate:%.3f, zt:%.3f, vol: %.3f", rate1, zt1, vol1)
    log_debug("2-rate:%.3f, zt:%.3f, vol: %.3f", rate2, zt2, vol2)
    log_debug("3-rate:%.3f, zt:%.3f, vol: %.3f", rate3, zt3, vol3)
    log_debug("4-rate:%.3f, zt:%.3f, vol: %.3f", rate4, zt4, vol4)
    log_debug("5-rate:%.3f, zt:%.3f, vol: %.3f", rate5, zt5, vol5)

    # rule1: 5
    # 1.
    # 2.
    rule1_sub1 = rate1 > 0 and rate2 > 0 and rate3 > 0 and rate4 > 0 and rate5 > 0
    rule1_sub2 = rate1 < 4 and rate2 < 4 and rate3 < 4 and rate4 < 4 and rate5 < 4
    rule1_sub3 = vol5 > vol4 and vol4 > vol3
    rule1_sub4 = zt5 > zt4 and zt4 > zt3 and zt3 > 0

    rule1 = False and rule1_sub1 and rule1_sub2 and rule1_sub3 and rule1_sub4

    # rule2: 4
    rule2 = False

    rule3 = False

    if rule1:
        rv = 1
        log_debug("nice: up-warrior rule1")

        log_debug("1-rate:%.3f, zt:%.3f, vol: %.3f", rate1, zt1, vol1)
        log_debug("2-rate:%.3f, zt:%.3f, vol: %.3f", rate2, zt2, vol2)
        log_debug("3-rate:%.3f, zt:%.3f, vol: %.3f", rate3, zt3, vol3)
        log_debug("4-rate:%.3f, zt:%.3f, vol: %.3f", rate4, zt4, vol4)
        log_debug("5-rate:%.3f, zt:%.3f, vol: %.3f", rate5, zt5, vol5)
        log_debug("zt5: %.3f", zt5)
    elif rule2:
        rv = 2
        log_debug("nice: up-warrior rule2")

        log_debug("rate:%.3f, vol:%.3f, zt: %.3f", rate1, zt1, vol1)
        log_debug("rate:%.3f, vol:%.3f, zt: %.3f", rate2, zt2, vol2)
        log_debug("rate:%.3f, vol:%.3f, zt: %.3f", rate3, zt3, vol3)
        log_debug("rate:%.3f, vol:%.3f, zt: %.3f", rate4, zt4, vol4)
        log_debug("rate:%.3f, vol:%.3f, zt: %.3f", rate5, zt5, vol5)
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
    content1 = "" # up-accu
    content2 = "" # up-fly
    content3 = "" # up-warrior
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


        rv = up_accum()
        if rv == 1:
            one = "%s -- %s\n" % (_trade_date, stock_id)
            """
            if tech_is_cross5(stock_id, _trade_date, _db):
                good = "+++bingo with一阳5线\n"
            elif tech_is_cross4(stock_id, _trade_date, _db):
                good = "++good with 一阳4线\n"
            else:
                good = "NEED一阳5线\n"
            """
            one += good
            one += get_basic_info_all(stock_id, _db)
            one += "--------------------------------\n"
            log_info("nice1-up_accum:\n%s", one)
            content1 += one
        else:
            # log_debug("wait...")
            pass

        rv = up_fly()
        if rv == 1:
            two = "%s -- %s\n" % (_trade_date, stock_id)
            two += good
            two += get_basic_info_all(stock_id, _db)
            two += "--------------------------------\n"
            log_info("nice2-up_accum:\n%s", two)
            content2 += two
        else:
            # log_debug("wait...")
            pass

        rv = up_warrior()
        if rv == 1:
            three = "%s -- %s\n" % (_trade_date, stock_id)
            three += good
            three += get_basic_info_all(stock_id, _db)
            three += "--------------------------------\n"
            log_info("nice3-up_warrior:\n%s", three)
            content3 += three
        else:
            # log_debug("wait...")
            pass


    log_info("%d costs %d us", rownum, get_micro_second() - begin)

    mailed = 0

    if len(content1) > 0:
        subject = "up_accum: %s" % (_trade_date)
        log_info(subject)
        log_info("\n%s", content1)
        if sai_is_product_mode():
            mailed = 1
            saimail_dev(subject,  content1)
    else:
        log_info("sorry1: %s", _trade_date)

    if len(content2) > 0:
        subject = "up_fly: %s" % (_trade_date)
        log_info(subject)
        log_info("\n%s", content2)
        if sai_is_product_mode():
            mailed = 1
            saimail_dev(subject,  content2)
    else:
        log_info("sorry1: %s", _trade_date)

    if len(content3) > 0:
        subject = "up_warrior: %s" % (_trade_date)
        log_info(subject)
        log_info("\n%s", content3)
        if sai_is_product_mode():
            mailed = 1
            saimail_dev(subject,  content3)
    else:
        log_info("sorry1: %s", _trade_date)


    if sai_is_product_mode():
        if mailed == 0:
            subject = "No Good K: %s" % (_trade_date)
            # saimail(subject, "the last chance in your life?")

    return


def regression(_db):

    # 002695
    max_date = "2017-06-09"
    days = 1

    max_date = "2017-06-14"
    days = 20

    # 000025
    max_date = "2017-06-13"
    days = 1

    # 000506
    max_date = "2017-06-09"
    days = 1

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
        work_one(trade_date, db)
    else:
        regression(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("k2.log")

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


# k2.py
