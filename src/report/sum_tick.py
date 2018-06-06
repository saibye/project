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
策略：
"""
#######################################################################

g_inst_date = ""
g_inst_time = ""


def sum_tick_one(_stock_id, _trade_date, _db):
    global g_inst_date
    global g_inst_time

    # today data
    base_vol = 200

    df = None

    log_debug("processing: %s", _stock_id)

    try:
        df = ts.get_sina_dd(_stock_id, date=_trade_date, vol=base_vol)
        # df = get_tick_sina(_stock_id, _trade_date)
        # df = get_tick_feng(_stock_id, _trade_date)
    except Exception:
        log_error("warn: %s,%s get_sina_dd exception!", _stock_id, _trade_date)
        return -4

    if df is None :
        log_error("warn: stock %s is None, next", _stock_id)
        return -1

    if df.empty:
        log_error("warn: stock %s is empty, next", _stock_id)
        return -2

    if len(df) < 5:
        log_error("warn: stock %s is empty2, next", _stock_id)
        return -3

    # convert to 手
    df['volume'] = df['volume'] / 100

    df = df.sort_index(ascending=False)

    buy1  = 0
    sell1 = 0
    mid1  = 0

    buy2  = 0
    sell2 = 0
    mid2  = 0

    buy3  = 0
    sell3 = 0
    mid3  = 0

    buy4  = 0
    sell4 = 0
    mid4  = 0

    # check df
    vol = 200
    buy1, sell1, mid1 = get_buy_sell_sum3(df, vol)
    if buy1 > 0:
        log_debug("base(%05d):  \tB:%d, S:%d, M:%d", vol, buy1, sell1, mid1)
    else:
        log_info("%s, %s no data", _stock_id, _trade_date)
        return 1

    vol = 1000
    buy2, sell2, mid2 = get_buy_sell_sum3(df, vol)
    if buy2 > 0:
        log_debug("base(%05d):  \tB:%d, S:%d, M:%d", vol, buy2, sell2, mid2)
    else:
        pass

    vol = 3000
    buy3, sell3, mid3 = get_buy_sell_sum3(df, vol)
    if buy3 > 0:
        log_debug("base(%05d):  \tB:%d, S:%d, M:%d", vol, buy3, sell3, mid3)
    else:
        pass

    vol = 10000
    buy4, sell4, mid4 = get_buy_sell_sum3(df, vol)
    if buy4 > 0:
        log_debug("base(%05d): \tB:%d, S:%d, M:%d", vol, buy4, sell4, mid4)
    else:
        pass

    sql = "insert into tbl_tick_sum\
(pub_date, stock_id, stock_loc, \
buy1,  buy1000,  buy3000,  buy10000, \
sell1, sell1000, sell3000, sell10000, \
mid1,  mid1000,  mid3000,  mid10000, \
inst_date, inst_time) \
values ('%s', '%s', '%s', \
'%.2f', '%.2f', '%.2f', '%.2f', \
'%.2f', '%.2f', '%.2f', '%.2f', \
'%.2f', '%.2f', '%.2f', '%.2f', \
'%s', '%s')" % \
    (_trade_date, _stock_id, 'cn', 
     buy1,  buy2,  buy3,  buy4,
     sell1, sell2, sell3, sell4,
     mid1,  mid2,  mid3,  mid4,
     g_inst_date, g_inst_time)

    # log_debug("sql: [%s]", sql)
    rv = sql_to_db(sql, _db)
    if rv:
        log_error("error: sql_to_db: %d", rv)

    return 0


# 收盘前检查一次
def sum_tick_all(_trade_date, _db):

    # step1: get from web
    stocks = get_stock_list_df_tu()

    for row_index, row in stocks.iterrows():
        stock_id = row_index

        rv = sum_tick_one(stock_id, _trade_date, _db)
        if rv != 0:
            log_error("error: sum_tick_one")
        else:
            log_debug("nice:  succeed")

    return 0


def sum_tick_unit_test(_db):
    global g_inst_date
    global g_inst_time

    buy  = 0
    sell = 0
    mid  = 0

    stock_id   = "600016"
    stock_id   = "601003"
    trade_date = "2017-05-05"

    rv = sum_tick_one(stock_id, trade_date, _db)
    if rv != 0:
        log_error("error: sum_tick_one")
    else:
        log_debug("nice:  sum succeeds")

    return 0


def work():
    global g_inst_date
    global g_inst_time

    db = db_init()

    g_inst_date = get_today()
    g_inst_time = get_time()
    log_info("today: %s", g_inst_date)

    # sum_tick_unit_test(db)

    trade_date = "2017-05-05"
    trade_date = "2017-05-04"
    trade_date = "2017-05-03"
    trade_date = "2017-05-02"
    trade_date = "2018-06-01"

    trade_date = g_inst_date
    rv = sum_tick_all(trade_date, db)
    if rv:
        log_error("error: sum_tick_all")


    db_end(db)


#######################################################################

def main():
    sailog_set("sum_tick.log")

    log_info("------------------------------------------------")

    if sai_is_product_mode():
        # check holiday
        if today_is_weekend():
            log_info("today is weekend, exit")
            # work()
        else:
            log_info("today is workday, come on")
            work()
    else:
        log_info("test mode, come on")
        work()


    log_info("main ends, bye!")
    return

main()

#######################################################################

# sum_tick.py
