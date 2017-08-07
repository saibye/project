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


def rt_dadan_save(_stock_id, _good_type, _key1, _key2, _key3, _key4, _db):
    global g_stock_date

    inst_date = get_today()
    inst_time = get_time()

    sql = "insert into tbl_good \
(pub_date, stock_id, stock_loc, \
holder, good_type, good_reason, \
v1, v2, v3, v4, \
is_valid, inst_date, inst_time) \
values ('%s', '%s', '%s', \
'%s', '%s', '%s', \
'%d', '%.2f', '%d', '%s', \
'%s', '%s', '%s')" % \
    (g_stock_date, _stock_id, 'cn', 
     'sai', _good_type, 'sweet',
     _key1, _key2, _key3, _key4,
     '1', inst_date, inst_time)

    log_debug("sql: [%s]", sql)
    rv = sql_to_db(sql, _db)

    return rv


def rt_dadan_check_buy(_stock_id, _df, _db, _vol_base, _count_base, _noticed, _list, _price):

    good = 0

    buy  = "买盘"
    sell = "卖盘"

    con1 = 0

    subject = ""
    body    = ""

    stock_id  = _stock_id

    global g_stock_date

    good_volume = 0
    good_tm     = ""
    good_price  = 0.0
    good_con    = 1

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

                if good == 1:
                    break
                else:
                    body = ""
                # log_info("有卖盘: 重置 [%d, %s, %d, %s]", con1, tm, volume, direction)

            if direction == buy and price >= _price:
                body   += u"%s, %s: p: %.2f,  v: %d, t: %d\n" % (stock_id, tm, price, volume, con1)

            if con1 >= _count_base and price >= _price :
                # log_info("nice: buy [%s]: at [%s, %.2f, %d] %dth", stock_id, tm, price, volume, con1)
                good = 1
                good_volume = volume
                good_tm     = tm
                good_price  = price
                good_con    = con1

    if good == 1:
        if _noticed.has_key(stock_id) :
            pass
        else :
            body += get_basic_info_all(stock_id, _db)  # 2017-2-24 find (2006, 'MySQL server has gone away')
            body += "++++++++++++++++++++++++++++++++\n"
            _noticed[stock_id] = body
            _list.append(body)
            log_info("nice:\n%s", body)

            #  超大单实时通知 2016/8/17
            if _vol_base >= 120000:
                log_info("let's mail3 immediately")
                subject = "#dadan3 [%s] %s" % (_stock_id, g_stock_date)
                body    = "%s -- (%.2f%%) -- p%.2f\n" % (g_stock_date, get_chg_rate(_stock_id), get_curr_price(_stock_id))
                for item in _list:
                    body   +=  item
                log_info("mail3 %s", body)
                saimail_dev(subject, body)
                if volume >= 300000:
                    saimail2(subject, body)


    if good == 1:
        # 1. get good-type
        if _vol_base == 3000:
            good_type = "dadan1"
        elif _vol_base == 10000:
            good_type = "dadan2"
        elif _vol_base > 100000:
            good_type = "dadan3"
        else:
            good_type = "unknown %d" % _vol_base

        # 2. insert
        rt_dadan_save(_stock_id, good_type, good_volume, good_price, good_con, good_tm, _db)

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


    # buy
    vol_base = 3000
    df_buy = df[df.volume >= vol_base]

    # check df
    vol = 3000
    cnt = 20
    pri = 7.00
    if g_has_noticed.has_key(_stock_id):
        pass
    else:
        good = rt_dadan_check_buy(_stock_id, df_buy, _db, vol, cnt, g_has_noticed,  g_good_list, pri)

    vol = 10000
    cnt = 12
    pri = 6.00
    if g_has_noticed2.has_key(_stock_id):
        pass
    else: 
        good = rt_dadan_check_buy(_stock_id, df_buy, _db, vol, cnt, g_has_noticed2, g_good_list2, pri)

    vol = 120000
    cnt = 1
    pri = 6.00
    g_good_list3 = []    # 2017-4-3
    if g_has_noticed3.has_key(_stock_id):
        pass
    else:
        good = rt_dadan_check_buy(_stock_id, df_buy, _db, vol, cnt, g_has_noticed3, g_good_list3, pri)


    return 


def rt_dadan_rank_one(_stock_id, _dd_date, _db):

    buy  = 0
    sell = 0
    mid  = 0

    # 100手起
    base_vol = 100

    df = None

    try:
        df = ts.get_sina_dd(_stock_id, date=_dd_date, vol=base_vol)
    except Exception:
        log_error("warn: %s get_sina_dd exception!", _stock_id)
        time.sleep(5)
        return -4,-4,-4

    if df is None :
        # log_error("warn: stock %s is None, next", _stock_id)
        return -1,-1,-1

    if df.empty:
        # log_error("warn: stock %s is empty, next", _stock_id)
        return -2,-2,-2

    if len(df) <= 5:
        # log_error("warn: stock %s is short, next", _stock_id)
        return -3,-3,-3

    # convert to 手
    df['volume'] = df['volume'] / 100

    log_debug("ranking: %s, size: %d", _stock_id, len(df))

    # 保持 升序
    df = df.sort_index(ascending=False)

    # rank 2016/8/28
    rank, content = get_df_rank(df)
    # if rank >= 300 or (rank >= 209 and rank % 100 == 9):
    # if rank >= 100 or (rank >= 209 and rank % 100 == 9):
    if rank >= 309:
        subject = "rank: %d 净流入 %s (%.2f%%)" % (rank, _stock_id, get_chg_rate(_stock_id))
        content += get_basic_info_all(_stock_id, _db)
        log_info("nice: %s, %s", subject, content)
        # saimail_dev(subject, content)

    buy, sell, mid = get_buy_sell_sum2(df)

    return buy, sell, mid


# 收盘前检查一次
def rt_dadan_rank(_stocks, _trade_date, _db):

    buy0  = 0
    sell0 = 0
    mid0  = 0

    buy  = 0
    sell = 0
    mid  = 0

    for row_index, row in _stocks.iterrows():
        stock_id = row_index

        buy0, sell0, mid0 = rt_dadan_rank_one(stock_id, _trade_date, _db)
        if buy0 > 0:
            buy  = buy + buy0
            sell = sell + sell0
            mid  = mid + mid0
            # log_debug("adding: buy[%d], sell[%d], mid[%d]", buy, sell, mid)

    diff = buy - sell
    if buy > 0 and sell > 0:
        subject = "尾盘统计 %s" % (_trade_date)
        content = "净: %.2f (unit)\n" % ((buy-sell) / 10000)
        content+= "买: %.2f (unit)\n" % (buy / 10000)
        content+= "卖: %.2f (unit)\n" % (sell / 10000)
        content+= "中: %.2f (unit)\n" % (mid / 10000)
        saimail_dev(subject, content)


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

    day_rank_checked = 0

    end_time  = '15:05:00'
    lun_time1 = '11:35:00'
    lun_time2 = '13:00:00'

    pre_end_time  = '14:30:00'

    global g_stock_date


    if sai_is_product_mode():
        g_stock_date = get_date_by(0)
    else:
        g_stock_date = "2016-12-09"
        g_stock_date = "2017-03-24"
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

        """
        global g_check_count
        if g_check_count == 0:
            log_info("all stock no data, exit")
            saimail_dev("dadan: no data at all", "take a rest2")
            break
        """

        # 策略1: mail
        if len(g_good_list) > 0 :
            log_info("let's mail1")
            subject = "dadan1-buy %s" % g_stock_date
            body    = ""
            for item in g_good_list :
                body   +=  item
            saimail_dev(subject, body)
            saimail2(subject, body)

        # 策略2: mail
        if len(g_good_list2) > 0 :
            log_info("let's mail2")
            subject = "dadan2-buy %s" % g_stock_date
            body    = ""
            for item in g_good_list2 :
                body   +=  item
            saimail_dev(subject, body)
            saimail2(subject, body)

        # 策略3: mailed at realtime

        """
        # 测试模式
        break
        """

        if sai_is_product_mode():
            # 收盘前分析资金流向 2016/8/28
            if curr >= pre_end_time and day_rank_checked == 0:
                day_rank_checked = 1
                rt_dadan_rank(_stocks, g_stock_date, _db)

        # 当日结束
        curr = get_time()
        if curr >= end_time:
            log_info("'%s' means end today", curr)
            break

        # 降低频率
        time.sleep(600)

    return


def work():
    db = db_init()

    # step1: get from web
    stocks = get_stock_list_df_tu()

    # step2: loop the list
    rt_timer(stocks, db)

    """
    rt_dadan_rank(stocks, "2017-04-21", db)
    """

    db_end(db)


#######################################################################

def main():
    sailog_set("rt_dadan.log")

    log_info("let's begin here!")

    saimail_init()

    if sai_is_product_mode():
        # check holiday
        if today_is_weekend():
            log_info("today is weekend, exit")
            # saimail_dev("dadan: weekend", "take a rest1")
        else:
            log_info("today is workday, come on")
            work()
    else:
        log_info("test mode, come on")
        work()


    log_info("main ends, bye!")
    return

main()
exit()

#######################################################################

# rt_dadan.py
