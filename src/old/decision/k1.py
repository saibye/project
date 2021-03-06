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
# 不需要macd等,  所以只使用tbl_day表 2016/11/26
#######################################################################


###
# 锤子 2017-6-10
# 需要连续两个阳柱
# 300526
# ################
# ################
def hammer():
    rate1 = (ref_close(1) - ref_close(2)) / ref_close(2) * 100 # 昨日涨幅
    rate2 = (ref_close(0) - ref_close(1)) / ref_close(1) * 100 # 今日涨幅
    zt1   = (ref_close(1) - ref_open(1)) / ref_close(2) * 100 # 第一天
    zt2   = (ref_close(0) - ref_open(0)) / ref_close(1) * 100 # 第二天
    hp2   = (ref_high(0)  - ref_close(1)) / ref_close(1) * 100 # 今日 最高点
    amp2  = (ref_high(0)  - ref_low(0)) / ref_close(1) * 100 # 今日振幅

    # 300526
    rule1 = zt2 > 1 and hp2 > 9.8 \
                and amp2 > 14 \
                and rate1 < -9.8 \
                and ref_close(0) > ref_high(1) \
                and ref_open(0) <= ref_close(1)

    rule2 = False

    if rule1 or rule2:
        rv = 1
        log_debug("nice: hammer")
        log_debug("rate1: %.2f", rate1)
        log_debug("rate2: %.2f", rate2)
        log_debug("hp2:   %.2f", hp2)
        log_debug("amp2:  %.2f", amp2)
        log_debug("%.2f, %.2f",  zt1, zt2)
    else:
        rv = 0
        # log_debug("not match")

    return rv


###
# 刺透 2017-4-5
# 需要均线发散
# 600242, 2017-03-14: -6.7%; 2017-03-15: 10%, 阳柱包括阴柱
# 600165, 2017-03-27, -6.6%; 2017-03-28: 8.08%
# bad -- 002634
def citou():
    rate1 = (ref_close(1) - ref_close(2)) / ref_close(2) * 100 # 昨日涨幅
    rate2 = (ref_close(0) - ref_close(1)) / ref_close(1) * 100 # 今日涨幅

    log_debug("rate1: %.2f", rate1)
    log_debug("rate2: %.2f", rate2)

    # if rate1 <= -5 and rate2 >= 5 and ref_open(0) < ref_low(1) and ref_close(0) > mid: # 2016-11-20
    if rate1 <= -6.5 and rate2 >= 8.0 \
                and ref_open(0) <= ref_close(1)*1.01 \
                and ref_close(0) > ref_high(1):
        rv = 1
        log_debug("nice: citou")
        log_debug("rate1: %.2f", rate1)
        log_debug("rate2: %.2f", rate2)
        log_debug("open0: %.2f", ref_open(0))
        log_debug("close0:%.2f", ref_close(0))
        log_debug("close1:%.2f", ref_close(1)*1.01)
        log_debug("high1: %.2f", ref_high(1))
    else:
        rv = 0
        # log_debug("not match")

    return rv


###
# 刺透 2017-5-29
# 需要穿越4线+均线发散
# 603098
# 002158
# ################
# 603896
# 000856
# ################
def citou2():
    rate1 = (ref_close(1) - ref_close(2)) / ref_close(2) * 100 # 昨日涨幅
    rate2 = (ref_close(0) - ref_close(1)) / ref_close(1) * 100 # 今日涨幅
    zt1   = (ref_close(1) - ref_open(1)) / ref_close(2) * 100 # 第一天
    zt2   = (ref_close(0) - ref_open(0)) / ref_close(1) * 100 # 第二天

    # 603098
    # 002158
    rule1 = rate1 <= -9.8 and rate2 >= 9.8 \
                and ref_close(0) >= ref_high(1) \
                and ref_low(0) <= ref_close(1) \
                and zt1 < -5 \
                and zt2 > 8

    # 603896, zt14, 15
    # 000856, zt5,  10
    rule2 = rate1 <= -9.8 and rate2 >= 9.8 \
                and ref_close(0)*1.05 >= ref_high(1) \
                and ref_open(0) <= ref_close(1) \
                and zt1 < -5 \
                and zt2 >= 10
    # 002761
    rule3 = rate1 <= -9.9 and rate2 >= 9.9

    if rule1 or rule2 or rule3:
        rv = 1
        log_debug("nice: citou2")
        log_debug("rate1: %.2f", rate1)
        log_debug("rate2: %.2f", rate2)
        log_debug("low:   %.2f", ref_low(1))
        log_debug("close: %.2f", ref_close(0))
        log_debug("open:  %.2f", ref_open(0))
        log_debug("%.2f, %.2f",  zt1, zt2)
    else:
        rv = 0
        # log_debug("not match")

    return rv


# 超级模式  2017-2-11
# 002346 -- 2016-12-26
# 300311 -- 2017-1-17
# 600698 -- 2017-1-17
#######################
# 第一天跌停：大跌 -8%
# 第二天涨停：大涨 +8%
# 今日开盘 < 昨日最低
# 今日收盘 > 昨日最高
#######################
def fanbao():
    rate1 = (ref_close(1) - ref_close(2)) / ref_close(2) * 100
    rate2 = (ref_close(0) - ref_close(1)) / ref_close(1) * 100

    if rate1 <= -8 and rate2 >= 8 and ref_open(0) < ref_low(1) and ref_close(0) > ref_high(1):
        rv = 1
        log_debug("nice: fanbao")
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
    if rate1 <= -8 and rate3 >= 7\
                and ref_open(1) < ref_close(2) \
                and ref_open(0)*1.01 >= ref_close(1) \
                and ref_close(0) >= md1 \
                and zt1 <= -4 \
                and zt3 >=  6 \
                and abs(zt2) <= 4:
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


"""
002011 - 2017-5-24
"""
def qiming2():
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
    if rate1 <= -6 and rate3 >= 9.8 \
                and ref_open(1) <= ref_close(2) \
                and ref_open(0)*1.01 >= ref_close(1) \
                and ref_close(0) >= ref_high(2) \
                and zt1 <= -5 \
                and zt3 >=  9 \
                and abs(zt2) <= 2:
        rv = 1
        log_debug("nice: qiming2")

        log_debug("rate1: %.2f pk %.2f => %.2f", ref_close(2), ref_close(3), rate1)
        log_debug("rate3: %.2f pk %.2f => %.2f", ref_close(0), ref_close(1), rate3)
        log_debug("%.2f <= %.2f", ref_open(1), ref_close(2))
        log_debug("%.2f >= %.2f", ref_open(0)*1.01, ref_close(1))
        log_debug("%.2f >= %.2f", ref_close(0), ref_high(2))
        log_debug("%.2f , %.2f , %.2f", zt1, zt2, zt3)
    else:
        rv = 0
        # log_debug("not match")

    return rv


"""
002837 - 2017-6-5
"""
def qiming3():
    rate1 = (ref_close(2) - ref_close(3)) / ref_close(3) * 100  # 第一天 前天
    rate3 = (ref_close(0) - ref_close(1)) / ref_close(1) * 100  # 第三天 today
    zt1   = (ref_close(2) - ref_open(2)) / ref_close(3) * 100 # 第一天
    zt2   = (ref_close(1) - ref_open(1)) / ref_close(2) * 100 # 第二天
    zt3   = (ref_close(0) - ref_open(0)) / ref_close(1) * 100 # 第三天 today

    # 1. 前天-10
    # 2. 昨天低开+
    # 3. 今天+10

    # 002837
    rule1 =  rate1 <= -9.8 and rate3 >= 9.8 \
                and zt2 > 0 \
                and ref_open(1) <= ref_close(2) \
                and zt3 > 2 

    # XXX
    rule2 = False

    if rule1 or rule2:
        rv = 1
        log_debug("nice: qiming3")

        log_debug("rate1: %.2f pk %.2f => %.2f", ref_close(2), ref_close(3), rate1)
        log_debug("rate3: %.2f pk %.2f => %.2f", ref_close(0), ref_close(1), rate3)
        log_debug("%.2f <= %.2f", ref_open(1), ref_close(2))
        log_debug("%.2f >= %.2f", ref_open(0)*1.01, ref_close(1))
        log_debug("%.2f >= %.2f", ref_close(0), ref_high(2))
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


"""
000507 - 2017-5-24
"""
def qiming4():
    rate1 = (ref_close(2) - ref_close(3)) / ref_close(3) * 100  # 第一天 前天
    rate3 = (ref_close(0) - ref_close(1)) / ref_close(1) * 100  # 第三天 today
    md1   = (ref_open(2)*2 + ref_close(2))/ 3
    zt1   = (ref_close(2) - ref_open(2)) / ref_close(3) * 100 # 第一天
    zt2   = (ref_close(1) - ref_open(1)) / ref_close(2) * 100 # 第二天
    zt3   = (ref_close(0) - ref_open(0)) / ref_close(1) * 100 # 第三天 today

    log_debug("rate1: %.2f pk %.2f => %.2f", ref_close(2), ref_close(3), rate1)
    log_debug("rate3: %.2f pk %.2f => %.2f", ref_close(0), ref_close(1), rate3)
    log_debug("%.2f <= %.2f", ref_open(1), ref_close(2))
    log_debug("%.2f >= %.2f", ref_open(0)*1.01, ref_close(1))
    log_debug("%.2f >= %.2f", ref_close(0), ref_high(2))
    log_debug("%.2f , %.2f , %.2f", zt1, zt2, zt3)

    # 1. 前天大幅下跌
    # 2. 昨天低开
    # 3. 今天高开
    # 4. 今天收盘超过前天2/3
    if rate1 <= -7 and rate3 >= 9.5 \
                and ref_open(1) <= ref_close(2) \
                and ref_open(0)*1.01 >= ref_close(1) \
                and ref_close(0)*1.01 >= ref_high(2) \
                and zt1 <= -5 \
                and zt3 >=  9 \
                and abs(zt2) <= 2:
        rv = 1
        log_debug("nice: qiming4")

        log_debug("rate1: %.2f pk %.2f => %.2f", ref_close(2), ref_close(3), rate1)
        log_debug("rate3: %.2f pk %.2f => %.2f", ref_close(0), ref_close(1), rate3)
        log_debug("%.2f <= %.2f", ref_open(1), ref_close(2))
        log_debug("%.2f >= %.2f", ref_open(0)*1.01, ref_close(1))
        log_debug("%.2f >= %.2f", ref_close(0), ref_high(2))
        log_debug("%.2f , %.2f , %.2f", zt1, zt2, zt3)
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
    content1 = "" # fanbao
    content2 = "" # qiming
    content3 = "" # sanfa 2016-12-3
    content4 = "" # citou 2017-4-5
    content5 = "" # qiming2 2017-5-29
    content6 = "" # citou2  2017-5-29
    content7 = "" # qiming3 2017-6-8
    content8 = "" # hammer  2017-6-10
    content9 = "" # qiming4 2017-6-25
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

        rv = fanbao()
        if rv == 1:
            one  = "%s -- %s\n" % (_trade_date, stock_id)
            one += get_basic_info_all(stock_id, _db)
            one += "--------------------------------\n"
            log_info("nice1-fanbao: %s", one)
            content1 += one
        else:
            # log_debug("wait...")
            pass

        rv = qiming()
        if rv == 1:
            two = "%s -- %s\n" % (_trade_date, stock_id)
            if tech_is_cross5(stock_id, _trade_date, _db):
                good = "+++with一阳5线\n"
            elif tech_is_cross4(stock_id, _trade_date, _db):
                good = "++with 一阳4线\n"
            else:
                good = "better if could cross\n"
            two += good
            two += get_basic_info_all(stock_id, _db)
            two += "--------------------------------\n"
            log_info("nice2-qiming: %s", two)
            content2 += two
        else:
            # log_debug("wait...")
            pass


        rv = up_sanfa()
        if rv == 1:
            three = "%s -- %s\n" % (_trade_date, stock_id)
            three += get_basic_info_all(stock_id, _db)
            three += "--------------------------------\n"
            log_info("nice3-sanfa: %s", three)
            content3 += three
        else:
            # log_debug("wait...")
            pass

        rv = citou()
        if rv == 1:
            four = "%s -- %s\n" % (_trade_date, stock_id)
            four+= get_basic_info_all(stock_id, _db)
            four+= "--------------------------------\n"
            log_info("nice4-citou: %s", four)
            content4 += four
        else:
            # log_debug("wait...")
            pass

        rv = qiming2()
        if rv == 1:
            five = "%s -- %s\n" % (_trade_date, stock_id)
            five += get_basic_info_all(stock_id, _db)
            five += "--------------------------------\n"
            log_info("nice5-qiming2: %s", five)
            content5 += five
        else:
            # log_debug("wait...")
            pass

        rv = citou2()
        if rv == 1:
            six = "%s -- %s\n" % (_trade_date, stock_id)
            six+= get_basic_info_all(stock_id, _db)
            six+= "--------------------------------\n"
            log_info("nice6-citou2: %s", six)
            content6 += six
        else:
            # log_debug("wait...")
            pass

        rv = qiming3()
        if rv == 1:
            seven = "%s -- %s\n" % (_trade_date, stock_id)
            if tech_is_cross5(stock_id, _trade_date, _db):
                good = "+++bingo with一阳5线\n"
            elif tech_is_cross4(stock_id, _trade_date, _db):
                good = "++good with 一阳4线\n"
            else:
                good = "NEED一阳5线\n"
            seven += good
            seven += get_basic_info_all(stock_id, _db)
            seven += "--------------------------------\n"
            log_info("nice7-qiming3:\n%s", seven)
            content7 += seven
        else:
            # log_debug("wait...")
            pass

        rv = hammer()
        if rv == 1:
            eight = "%s -- %s\n" % (_trade_date, stock_id)
            good  = ""
            eight += good
            eight += get_basic_info_all(stock_id, _db)
            eight += "--------------------------------\n"
            log_info("nice8-hammer:\n%s", eight)
            content8 += eight
        else:
            # log_debug("wait...")
            pass

        rv = qiming4()
        if rv == 1:
            nine = "%s -- %s\n" % (_trade_date, stock_id)
            if tech_is_cross5(stock_id, _trade_date, _db):
                good = "+++with一阳5线\n"
            elif tech_is_cross4(stock_id, _trade_date, _db):
                good = "++with 一阳4线\n"
            else:
                good = ""

            if len(good) > 0:
                nine += good
                nine += get_basic_info_all(stock_id, _db)
                nine += "--------------------------------\n"
                log_info("nice9-qiming4:\n%s", nine)
                content9 += nine
        else:
            # log_debug("wait...")
            pass


    log_info("%d costs %d us", rownum, get_micro_second() - begin)

    mailed = 0
    if len(content1) > 0:
        subject = "##fanbao: %s" % (_trade_date)
        warning = "需要阴柱很长\n"
        content1 = warning + content1
        log_info(subject)
        log_info("\n%s", content1)
        if sai_is_product_mode():
            mailed = 1
            saimail(subject,  content1)
    else:
        log_info("sorry1: %s", _trade_date)

    if len(content2) > 0:
        subject = "qiming: %s" % (_trade_date)
        good = "###一阳5线更佳\n"
        content2 = good + content2
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

    if len(content4) > 0:
        subject = "citou: %s" % (_trade_date)
        warning = "需要均线发散!!!\n"
        content4 = warning + content4
        log_info(subject)
        log_info("\n%s", content4)
        if sai_is_product_mode():
            mailed = 1
            saimail(subject,  content4)
    else:
        log_info("sorry1: %s", _trade_date)

    if len(content5) > 0:
        subject = "qiming2: %s" % (_trade_date)
        # good = "###一阳5线更佳\n"
        # content5 = good + content5
        log_info(subject)
        log_info("\n%s", content5)
        if sai_is_product_mode():
            mailed = 1
            saimail(subject,  content5)
    else:
        log_info("sorry1: %s", _trade_date)

    if len(content6) > 0:
        subject = "citou2: %s" % (_trade_date)
        good    = "穿越4线更佳\n"
        content6 = good + content6
        log_info(subject)
        log_info("\n%s", content6)
        if sai_is_product_mode():
            mailed = 1
            saimail(subject,  content6)
    else:
        log_info("sorry1: %s", _trade_date)


    if len(content7) > 0:
        subject = "qiming3: %s" % (_trade_date)
        log_info(subject)
        log_info("\n%s", content7)
        if sai_is_product_mode():
            mailed = 1
            saimail(subject,  content7)
    else:
        log_info("sorry1: %s", _trade_date)


    if len(content8) > 0:
        subject = "hammer: %s" % (_trade_date)
        log_info(subject)
        log_info("\n%s", content8)
        if sai_is_product_mode():
            mailed = 1
            saimail(subject,  content8)
    else:
        log_info("sorry1: %s", _trade_date)

    if len(content9) > 0:
        subject = "qiming4: %s" % (_trade_date)
        log_info(subject)
        log_info("\n%s", content9)
        if sai_is_product_mode():
            mailed = 1
            saimail(subject,  content9)
    else:
        log_info("sorry1: %s", _trade_date)

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
    max_date = "2017-03-31"
    days = 20
    max_date = "2017-05-19"
    days = 10
    max_date = "2017-05-03"
    days = 3

    max_date = "2017-05-24"
    days = 3

    max_date = "2017-05-09"
    days = 3

    max_date = "2017-04-25"
    days = 2

    max_date = "2017-05-23"
    days = 2

    max_date = "2017-06-05"
    days = 2

    # 000507
    max_date = "2017-05-24"
    days = 2

    # 000852
    max_date = "2017-05-15"
    days = 2

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
        trade_date = "2016-12-26"   # 002346
        trade_date = "2017-04-04"
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
