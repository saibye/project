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

#######################################################################

g_good_list = []

"""
buy策略：
1. vol >= 10000, 连续3笔买
2. vol >= 3000,  连续5笔买
"""
def rt_dadan_check_df(_df, _db, _vol_base, _count_base):
    global g_good_list
    good = 0

    buy  = "买盘"
    sell = "卖盘"

    con1 = 0

    # log_debug("\n%s", _df)
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

            if con1 >= _count_base:
                log_info("nice: buy [%s]: at [%s, %.2f] %dth", stock_id, tm, price, con1)
                good = 1
                # subject = u"dadan1: %s"  % stock_id
                body   += u"dadan: %s, %s: price: %.2f,  vol: %d, times: %d\n" % (stock_id, tm, price, volume, con1)

    if len(body) > 0 :
        # saimail(subject, body)
        log_info("body : \n%s", body)
        g_good_list.append(body)

    return good


def rt_dadan_one(_stock_id, _db):
    # log_info("rt_dadan_one begin")

    # today data
    base_vol = 500
    base_vol = 10000
    base_vol = 3000
    base_vol = 1000
    dd_date  = get_date_by(-2)
    dd_date  = get_date_by(0)
    # log_debug("stock: %s, %s, %s", _stock_id, dd_date, base_vol)

    # begin = get_micro_second()

    df = ts.get_sina_dd(_stock_id, date=dd_date, vol=base_vol)

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
    vol = 10000
    cnt = 3
    vol = 5000
    cnt = 6
    vol = 3000
    cnt = 8
    rt_dadan_check_df(df, _db, vol, cnt)

    # log_info("rt_dadan_check_df costs %d us", get_micro_second() - begin)

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
    end_time = '16:00:00'

    counter  = 0
    while 1:
        g_good_list = []
        counter = counter + 1

        log_info(">>>>>let's run here")

        begin = get_micro_second()

        # step2: iterate the list
        rt_dadan(_stocks, _db)

        diff = get_micro_second() - begin;
        # log_info("rt_dadan costs %d us", diff)

        if len(g_good_list) > 0 :
            log_info("let's mail")
            subject = "dadan1"
            for item in g_good_list :
                body   +=  item
            saimail(subject, body)

        """
        # delete me
        break
        """

        curr = get_time()
        if curr >= end_time:
            log_info("'%s' means end today", curr)
            break

        time.sleep(300)

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
