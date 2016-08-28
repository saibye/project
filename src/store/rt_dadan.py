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
1. vol >= 100000, 连续1笔买
2. vol >= 10000,  连续3笔买
3. vol >= 3000,   连续8笔买
"""
#######################################################################

g_good_list    = []
g_good_list2   = []
g_good_list3   = []

g_has_noticed  = {}
g_has_noticed2 = {}
g_has_noticed3 = {}

g_has_noticed_rank = {}

g_bad_stocks = {}

g_stock_date  = ""
g_check_count = 0  # 检查是否全天无数据

def rt_dadan_check_buy(_stock_id, _df, _db, _vol_base, _count_base, _noticed, _list, _price):

    good = 0

    buy  = "买盘"
    sell = "卖盘"

    con1 = 0

    subject = ""
    body    = ""

    stock_id  = _stock_id

    global g_stock_date

    for row_index, row in _df.iterrows():
        direction = row['type']
        volume    = row['volume']
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
                # log_info("nice: buy [%s]: at [%s, %.2f, %d] %dth", stock_id, tm, price, volume, con1)
                good = 1
                body   += u"%s, %s: price: %.2f,  vol: %d, times: %d\n" % (stock_id, tm, price, volume, con1)

    if len(body) > 0 :
        if _noticed.has_key(stock_id) :
            pass
        else :
            body += "++++++++++++++++++++++++++++++++\n"
            _noticed[stock_id] = body
            _list.append(body)
            log_info("nice:\n%s", body)

            #  超大单实时通知 2016/8/17
            if _vol_base >= 100000:
                log_info("let's mail3 immediately")
                subject = "#dadan3-buy %s" % g_stock_date
                body    = ""
                for item in _list:
                    body   +=  item
                log_info("mail3 %s", body)
                saimail(subject, body)

    return good



def rt_dadan_check_sell(_stock_id, _df, _db, _vol_base, _count_base, _price):

    good = 0

    buy  = "买盘"
    sell = "卖盘"

    con1 = 0

    subject = ""
    body    = ""

    stock_id  = _stock_id

    for row_index, row in _df.iterrows():
        direction = row['type']
        volume    = row['volume']
        tm        = row['time']
        price     = row['price']


        if volume >= _vol_base:
            if direction == sell:
                con1 = con1 + 1
                # log_info("连续sell: [%d, %s, %d, %s]", con1, tm, volume, direction)
            else :
                con1 = 0
                # log_info("有buy盘: 重置 [%d, %s, %d, %s]", con1, tm, volume, direction)

            if con1 >= _count_base and price >= _price :
                #log_info("warn: sell [%s]: at [%s, %.2f, %d] %dth", stock_id, tm, price, volume, con1)
                good = 1
                body   += u"warn: discard: %s, %s: price: %.2f,  vol: %d, times: %d\n" % (stock_id, tm, price, volume, con1)

    if len(body) > 0 :
        global g_bad_stocks
        if g_bad_stocks.has_key(_stock_id):
            pass
        else:
            body += "++++++++++++++++++++++++++++++++\n"
            log_info("warn:\n%s", body)
            g_bad_stocks[_stock_id] = body

    return good


def rt_dadan_one(_stock_id, _dd_date, _db):
    global g_has_noticed
    global g_has_noticed2
    global g_has_noticed3
    global g_good_list
    global g_good_list2
    global g_good_list3

    # today data
    base_vol = 200

    df = None

    try:
        df = ts.get_sina_dd(_stock_id, date=_dd_date, vol=base_vol)
    except Exception:
        log_error("warn: %s get_sina_dd exception!", _stock_id)
        time.sleep(5)
        return -4

    if df is None :
        # log_error("warn: stock %s is None, next", _stock_id)
        return -1

    if df.empty:
        log_error("warn: stock %s is empty, next", _stock_id)
        return -2

    log_debug("processing: %s", _stock_id)

    # convert to 手
    df['volume'] = df['volume'] / 100

    global g_check_count
    g_check_count += 1

    df = df.sort_index(ascending=False)


    """
    # TODO: 2016/8/22
    # sell
    # check df
    vol_base = 1000
    df_sell = df[df.volume >= vol_base]
    vol = 1000
    cnt = 6
    pri = 10.00
    rt_dadan_check_sell(_stock_id, df, _db, vol, cnt, pri)
    """


    # buy
    vol_base = 3000
    df_buy = df[df.volume >= vol_base]

    # check df
    vol = 3000
    cnt = 10
    pri = 10.00
    if g_has_noticed.has_key(_stock_id):
        pass
    else:
        rt_dadan_check_buy(_stock_id, df_buy, _db, vol, cnt, g_has_noticed,  g_good_list, pri)

    vol = 10000
    cnt = 4
    pri = 9.00
    if g_has_noticed2.has_key(_stock_id):
        pass
    else: 
        rt_dadan_check_buy(_stock_id, df_buy, _db, vol, cnt, g_has_noticed2, g_good_list2, pri)

    vol = 100000
    cnt = 1
    pri = 8.00
    if g_has_noticed3.has_key(_stock_id):
        pass
    else:
        rt_dadan_check_buy(_stock_id, df_buy, _db, vol, cnt, g_has_noticed3, g_good_list3, pri)

    """
    # rank 2016/8/19
    rank, rs, ns, mess= check_df_rates(df)
    if rank >= -1000:
        if g_has_noticed_rank.has_key(_stock_id):
            pass
        else:
            subject = "#rank1-buy"
            body    = "%s, rank: %d\n" % (_stock_id, rank)
            for item in mess:
                body += "%s\n" % item
            log_info("%s", body)
            # saimail(subject, body)
    """


    return 


def rt_dadan(_stocks, _trade_date, _db):
    global g_has_noticed
    global g_has_noticed2
    global g_has_noticed3

    global g_bad_stocks

    for row_index, row in _stocks.iterrows():
        stock_id = row_index
        """
        stock_id = '000002'
        """

        if g_bad_stocks.has_key(stock_id):
            log_debug("warn: %s is bad for:\n%s", stock_id, g_bad_stocks[stock_id])
            continue

        rt_dadan_one(stock_id, _trade_date, _db)

        """
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

    end_time  = '15:30:00'
    lun_time1 = '11:35:00'
    lun_time2 = '13:00:00'


    global g_stock_date
    g_stock_date = get_date_by(0)
    log_debug("trade day: %s", g_stock_date)


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

        # 遍历股票列表
        rt_dadan(_stocks, g_stock_date, _db)

        global g_check_count
        if g_check_count == 0:
            log_info("all stock no data, exit")
            saimail("dadan: no data at all", "take a rest2")
            break

        # 策略1: mail
        if len(g_good_list) > 0 :
            log_info("let's mail1")
            subject = "dadan1-buy %s" % g_stock_date
            body    = ""
            for item in g_good_list :
                body   +=  item
            saimail(subject, body)

        # 策略2: mail
        if len(g_good_list2) > 0 :
            log_info("let's mail2")
            subject = "dadan2-buy %s" % g_stock_date
            body    = ""
            for item in g_good_list2 :
                body   +=  item
            saimail(subject, body)

        # 策略3: mailed at realtime

        """
        # 测试模式
        break
        """

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

    # step1: get from web
    stocks = get_stock_list_df_tu()

    # step2: loop the list
    rt_timer(stocks, db)

    db_end(db)


#######################################################################

def main():
    sailog_set("rt_dadan.log")

    log_info("let's begin here!")

    saimail_init()

    # check holiday
    if today_is_weekend():
        log_info("today is weekend, exit")
        saimail("dadan: weekend", "take a rest1")
    else:
        log_info("today is workday, come on")
        work()

    log_info("main ends, bye!")
    return

main()
exit()

#######################################################################

# rt_dadan.py
