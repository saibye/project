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

g_goods = {}

# 0: free
# 1: bought
def validate_ma20(_stock_id, _trades, _db):
    status = 0
    total  = 0.0
    bought_date  = ""
    bought_price = 0.0

    global g_goods

    for row_index, row in _trades.iterrows():
        stock_id = row_index
        # log_debug("--------------------------------------------")
        pub_date    = row['pub_date']
        open_price  = row['open_price']
        close_price = row['close_price']
        ma20        = row['ma20']
        # log_debug("%s - close %.2f -- %.2f ma20", pub_date, close_price, ma20)
        if status == 0:
            # log_debug("free status")
            if close_price >= ma20:
                log_debug("nice: buy at [%s, %.2f]", pub_date, close_price)
                status = 1
                bought_date  = pub_date
                bought_price = close_price
            else:
                # log_debug("ohho, keep free")
                pass
        else:
            if close_price >= ma20:
                # log_debug("ok, keep full")
                pass
            else:
                log_debug("warn: sell at [%s, %.2f]", pub_date, close_price)
                status = 0
                diff   = close_price-bought_price
                rate   = diff / bought_price * 100
                total += rate
                log_debug("%s: from(%s - %s)", _stock_id, bought_date, pub_date)
                log_debug("bought(%.2f => %.2f) diff: %.2f, rate: %.2f%%",
                        bought_price, close_price, diff, diff/bought_price*100)

    g_goods[_stock_id] = total
    log_debug("%s: summary %.2f%%", _stock_id, total)

    return


def get_stock_trade(_stock_id, _db):
    sql = "select a.stock_id stock_id, a.pub_date pub_date, a.open_price open_price, \
a.close_price close_price, b.ma5 ma5, b.ma10 ma10, b.ma20 ma20, b.ma30 ma30 \
from tbl_day a, tbl_day_tech b \
where 1=1 \
and a.stock_id=b.stock_id \
and a.pub_date=b.pub_date \
and a.stock_id='%s' \
and a.pub_date >= '2016-01-01' \
order by a.pub_date" % (_stock_id)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in tbl_day", _stock_id)
        return None
    else:
        # log_debug("df: \n%s", df)
        return df


def get_all_stocks(_db):
    sql = "select distinct a.stock_id stock_id from tbl_day a order by 1"

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in tbl_day", _stock_id)
        return None
    else:
        log_debug("df: \n%s", df)
        return df


def work():
    db = db_init()

    stock_id = '000001'
    stock_id = '000002'
    stock_id = '000029'

    stocks = get_all_stocks(db)
    if stocks is None:
        log_error("get_all_stocks: not found!")
        return
    stocks.set_index('stock_id', inplace=True)

    for row_index, row in stocks.iterrows():
        stock_id = row_index
        log_debug("%s: ++++++++++++++++++++++++++++++++++++++++++++", stock_id)

        trades = get_stock_trade(stock_id, db)

        log_debug("len(df): %d", len(trades))

        if trades is None:
            log_info("not found!")
        else:
            trades.set_index('stock_id', inplace=True)
            validate_ma20(stock_id, trades, db)

    global g_goods
    log_debug("result:\n%s", g_goods)

    db_end(db)


#######################################################################

def main():
    sailog_set("ma20.log")

    log_info("let's begin here!")

    # check holiday
    """
    if today_is_weekend():
        log_info("today is weekend, exit")
    else:
        log_info("today is workday, come on")
        work()
    """
    work()

    log_info("main ends, bye!")
    return

main()
exit()

#######################################################################


# ma20.py
