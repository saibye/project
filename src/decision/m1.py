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
# k线合并：涨停往前看
#######################################################################


"""
000885
"""
def citou_m1():

    if ref_len() < 6:
        log_info("data not enough: 6")
        return -1

    rate0 = (ref_close(0) - ref_close(1)) / ref_close(1) * 100  # today
    rate1 = (ref_close(1) - ref_close(2)) / ref_close(2) * 100  # yestoday
    rate2 = (ref_close(2) - ref_close(3)) / ref_close(3) * 100  #
    rate3 = (ref_close(3) - ref_close(4)) / ref_close(4) * 100  #

    zt0   = (ref_close(0) - ref_open(0))  / ref_close(1) * 100  # today


    """
    log_debug("rate0: %.2f", rate0)
    log_debug("rate1: %.2f", rate1)
    log_debug("rate2: %.2f", rate2)
    log_debug("rate3: %.2f", rate3)
    """

    # 1. 当日涨停
    # 2. 往前看
    if rate0 > 0 and rate1 > 0 and max(rate0, rate1) > 9.8:
        rateA = ((1+rate1/100.00) * (1+rate0/100.00) - 1) * 100
        log_debug("rateA: %.2f", rateA)

        if rate2 < 0 and rate3 < 0 and min(rate2, rate3) < -7.0:
            rateB = ((1+rate2/100.00) * (1+rate3/100.00) - 1) * 100
            log_debug("rateB: %.2f", rateB)
        else:
            return 0

        # 阳线放量+阴线缩量
        vol_rule0 = ref_vol(0) > ref_vma5(0) and ref_vol(0) > ref_vma10(0)
        vol_rule1 = ref_vol(1) > ref_vma5(1) and ref_vol(1) > ref_vma10(1)
        vol_rule2 = ref_vol(2) < ref_vma5(2) and ref_vol(2) < ref_vma10(2)
        vol_rule3 = ref_vol(3) < ref_vma5(3) and ref_vol(3) < ref_vma10(3)

        vol_rule = (vol_rule0 or vol_rule1) and vol_rule2 and vol_rule3
        if vol_rule:
            log_debug("vol-rule match")
            log_debug("0: %.2f, vma5: %.2f, vma10: %.2f", ref_vol(0), ref_vma5(0), ref_vma10(0))
            log_debug("1: %.2f, vma5: %.2f, vma10: %.2f", ref_vol(1), ref_vma5(1), ref_vma10(1))
            log_debug("2: %.2f, vma5: %.2f, vma10: %.2f", ref_vol(2), ref_vma5(2), ref_vma10(2))
            log_debug("3: %.2f, vma5: %.2f, vma10: %.2f", ref_vol(3), ref_vma5(3), ref_vma10(3))
        else:
            return 0

        if rateA > 15 and rateB < -14:
            rv = 1
            log_debug("nice: citou_m1")
        else:
            rv = 0

    else:
        rv = 0

    return rv


def work_one_day(_trade_date, _db):

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
        rv = ref_set_with_tech(stock_id)
        if rv < 0:
            log_error("error: ref_set_with_tech: %s", stock_id)
            return rv
        elif rv < 5:
            log_error("warn: %s small %d", stock_id, rv)
            continue

        rv = citou_m1()
        if rv == 1:
            one = "%s -- %s\n" % (_trade_date, stock_id)
            if tech_is_cross5(stock_id, _trade_date, _db):
                good = "+++with一阳5线\n"
            elif tech_is_cross4(stock_id, _trade_date, _db):
                good = "++with 一阳4线\n"
            else:
                good = "better if cross\n"

            if len(good) > 0:
                one += good
                one += get_basic_info_all(stock_id, _db)
                one += "--------------------------------\n"
                log_info("nice1-citou_m1:\n%s", one)
                content1 += one
        else:
            pass


    log_info("%d costs %d us", rownum, get_micro_second() - begin)

    mailed = 0

    if len(content1) > 0:
        subject = "citou_m1: %s" % (_trade_date)
        log_info(subject)
        log_info("mail:\n%s", content1)
        if sai_is_product_mode():
            mailed = 1
            saimail(subject, content1)
    else:
        log_info("sorry1: %s", _trade_date)


    return


def regression(_db):


    # 000885
    max_date = "2017-01-18"
    days = 1

    # 603603
    max_date = "2017-05-10"
    days = 1

    # all
    max_date = "2017-06-29"
    days = 200

    log_info("regression")

    date_df = get_recent_pub_date(max_date, days, _db)
    if date_df is None:
        log_error("error: get_recent_pub_date failure")
        return -1
    else:
        date_df.set_index("pub_date", inplace=True)

    for row_index, row in date_df.iterrows():
        trade_date = row_index
        log_debug("[%s]------------------", trade_date)
        work_one_day(trade_date, _db)

    return 0


def work():
    db = db_init()

    if sai_is_product_mode():
        trade_date = get_date_by(0)
        work_one_day(trade_date, db)
    else:
        regression(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("m1.log")

    log_info("let's begin here!")

    if sai_is_product_mode():
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

#######################################################################


# m1.py
