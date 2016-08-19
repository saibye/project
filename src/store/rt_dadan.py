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


"""
buy策略：
1. vol >= 80000, 连续1笔买
2. vol >= 10000, 连续3笔买
3. vol >= 3000,  连续8笔买
"""
#######################################################################

g_good_list    = []
g_good_list2   = []
g_good_list3   = []

g_has_noticed  = {}
g_has_noticed2 = {}
g_has_noticed3 = {}



def rt_dadan_check_buy(_df, _db, _vol_base, _count_base, _noticed, _list, _price):

    good = 0

    buy  = "买盘"
    sell = "卖盘"

    con1 = 0

    subject = ""
    body    = ""

    for row_index, row in _df.iterrows():
        stock_id  = row['code']
        direction = row['type']
        volume    = row['volume'] / 100
        tm        = row['time']
        price     = row['price']


        if volume >= _vol_base:
            if direction == buy:
                con1 = con1 + 1
                # log_info("连续买: [%d, %s, %d, %s]", con1, tm, volume, direction)
            else :
                con1 = 0
                # log_info("有卖盘: 重置 [%d, %s, %d, %s]", con1, tm, volume, direction)

            if con1 >= _count_base and price >= _price :
                log_info("nice: buy [%s]: at [%s, %.2f] %dth", stock_id, tm, price, con1)
                good = 1
                # subject = u"dadan1: %s"  % stock_id
                body   += u"dadan: %s, %s: price: %.2f,  vol: %d, times: %d\n" % (stock_id, tm, price, volume, con1)

    if len(body) > 0 :
        if _noticed.has_key(stock_id) :
            pass
        else :
            _noticed[stock_id] = body
            _list.append(body)

            #  超大单实时通知 2016/8/17
            if _vol_base >= 80000:
                log_info("let's mail3 immediately")
                subject = "#dadan3-buy"
                body    = ""
                for item in g_good_list3 :
                    body   +=  item
                saimail(subject, body)

    return good


def rt_dadan_one(_stock_id, _db):
    # log_info("rt_dadan_one begin")
    global g_has_noticed
    global g_has_noticed2
    global g_has_noticed3
    global g_good_list
    global g_good_list2
    global g_good_list3

    # today data
    base_vol = 3000
    dd_date  = get_date_by(0)
    # log_debug("stock: %s, %s, %s", _stock_id, dd_date, base_vol)

    # begin = get_micro_second()

    df = None

    try:
        df = ts.get_sina_dd(_stock_id, date=dd_date, vol=base_vol)
    except Exception:
        log_error("warn: %s get_sina_dd exception!", _stock_id)
        time.sleep(5)
        return -4

    # log_info("get_sina_dd costs %d us", get_micro_second() - begin)

    if df is None :
        # log_error("warn: stock %s is None, next", _stock_id)
        return -1

    if df.empty:
        # log_error("warn: stock %s is empty, next", _stock_id)
        return -2

    df = df.sort_index(ascending=False)

    begin = get_micro_second()

    """
    """
    # check df
    vol = 3000
    cnt = 13
    pri = 12.00
    rt_dadan_check_buy(df, _db, vol, cnt, g_has_noticed,  g_good_list, pri)

    vol = 10000
    cnt = 3
    pri = 10.00
    rt_dadan_check_buy(df, _db, vol, cnt, g_has_noticed2, g_good_list2, pri)

    vol = 100000
    cnt = 1
    pri = 8.00
    rt_dadan_check_buy(df, _db, vol, cnt, g_has_noticed3, g_good_list3, pri)

    """
    log_debug("\n%s", df)
    rank= check_df_rates(df)
    log_debug("rank: %d", rank)
    """

    # log_info("rt_dadan_one end")

    return 


def rt_dadan(_stocks, _db):

    for row_index, row in _stocks.iterrows():
        """
        row_index = '600696'
        row_index = '600739'
        row_index = '002805'

        row_index = '600358'

        row_index = '000002'
        """

        rt_dadan_one(row_index, _db)

        """
        # delete me 2016/8/7
        break
        """

    return


"""
从9点半开始
"""

def rt_timer(_stocks, _db):
    global g_good_list
    global g_good_list2
    global g_good_list3
    end_time = '16:00:00'
    lun_time1 = '11:35:00'
    lun_time2 = '13:00:00'

    counter  = 0
    while 1:
        g_good_list  = []
        g_good_list2 = []
        g_good_list3 = []
        counter = counter + 1

        curr = get_time()
        if curr >= lun_time1 and curr <= lun_time2:
            log_info("'%s' means noon time", curr)
            time.sleep(300)
            continue

        log_info(">>>>>let's run here")

        begin = get_micro_second()

        # step2: iterate the list
        rt_dadan(_stocks, _db)

        diff = get_micro_second() - begin;
        # log_info("rt_dadan costs %d us", diff)

        if len(g_good_list) > 0 :
            log_info("let's mail")
            subject = "dadan1-buy"
            body    = ""
            for item in g_good_list :
                body   +=  item
            saimail(subject, body)

        if len(g_good_list2) > 0 :
            log_info("let's mail2")
            subject = "dadan2-buy"
            body    = ""
            for item in g_good_list2 :
                body   +=  item
            saimail(subject, body)


        """
        if len(g_good_list3) > 0 :
            log_info("let's mail3")
            subject = "#dadan3-buy"
            body    = ""
            for item in g_good_list3 :
                body   +=  item
            saimail(subject, body)
        """

        """
        # delete me
        break
        """

        curr = get_time()
        if curr >= end_time:
            log_info("'%s' means end today", curr)
            break

        time.sleep(180)

    return




def work():
    db = db_init()

    # step1: get from web
    stocks = get_stock_list_df_tu()

    # step2: record to db at some time
    rt_timer(stocks, db)


    db_end(db)


#######################################################################

def main():
    sailog_set("rt_dadan.log")

    log_info("let's begin here!")

    saimail_init()

    work()

    log_info("main ends, bye!")
    return

main()
exit()
print "can't arrive here"

#######################################################################


# rt_dadan.py
