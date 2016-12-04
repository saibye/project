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


def check_ma10_by_tu(_stock_id, _date, _db):
    rv   = 0

    try:
        begin = get_micro_second()
        df = ts.get_hist_data(_stock_id, start=_date, end=_date)
        log_info("get_hist_data for %s costs %d us", _stock_id, get_micro_second() - begin)
    except Exception:
        log_error("warn:error: %s get_hist_data exception!", _stock_id)
        return -3, -3, -3, -3

    if df is None :
        log_error("warn: stock %s is None, next", _stock_id)
        return -1, -1, -1, -1

    if df.empty:
        #  probably tingpai 
        log_error("warn: stock %s is empty, next", _stock_id)
        return -2, -2, -2, -2


    # log_debug("df: \n%s", df)

    # check min(close, open) <= ma10
    head = df.head(1)
    open_price  = head['open'][0]
    close_price = head['close'][0]
    low_price   = head['low'][0]
    high_price  = head['high'][0]
    ma10        = head['ma10'][0]
    ma5         = head['ma5'][0]

    # if close_price <= ma10 or close_price <= ma10:
    if ma10 >= low_price and ma10 <= high_price:
        # good position
        rv = 2
        log_debug("nice: back ma10")
    elif close_price <= ma5 or close_price <= ma10:
        # good position
        rv = 1
        log_debug("nice: back ma5")
    else:
        rv = 0
        log_debug("sorry, not ready!")


    return  rv, close_price, ma5, ma10


def check_chance(_stocks, _db):

    basic_info = ts.get_stock_basics()
    if basic_info is None:
        log_error("error: ts.get_stock_basics")
        return 

    #
    trade_date = get_date_by(0)
    log_debug("trade_date: %s", trade_date)

    content = ""
    for row_index, row in _stocks.iterrows():
        stock_id = row_index
        info_row = basic_info.loc[stock_id, :]
        log_debug("--------------------------------------------")
        one = "%s [%s] [%s]\n" % (stock_id, row['pub_date'], info_row['name'])
        log_debug(one)
        rv, close_price, ma5, ma10 = check_ma10_by_tu(stock_id, trade_date, _db)
        if rv == 2:
            one += "--back10: close: %.2f < ma10: %.2f\n" % (close_price, ma10)
        elif rv == 1:
            one += "--back5:  close: %.2f < ma5: %.2f\n" % (close_price, ma5)
            one += "------------------------------------------------------\n"

        content += one

    subject = "cross6 %s" % get_date_by(0)
    log_debug("%s", subject)
    log_debug("\n%s", content)
    saimail(subject, content)

    return


"""
-- 2016/11/15
and b.macd > 0 \
and b.diff > 0 \
and b.dea  >= 0 \
"""
def get_cross6(_db):
    sql = "select a.stock_id, a.pub_date, a.open_price, a.close_price,  \
b.ma5, b.ma10, b.ma20, b.ma30, b.ma60, b.ma150, macd, diff, dea \
from tbl_day a, tbl_day_tech b \
where a.pub_date in (select * from (select distinct pub_date from tbl_day_tech x order by pub_date desc limit 10) y) \
and a.stock_id=b.stock_id \
and a.pub_date=b.pub_date \
and a.open_price < a.close_price \
and b.ma5   >= a.open_price \
and b.ma10  >= a.open_price \
and b.ma20  >= a.open_price \
and b.ma30  >= a.open_price \
and b.ma60  >= a.open_price \
and b.ma150 >= a.open_price \
and b.ma5   <= a.close_price \
and b.ma10  <= a.close_price \
and b.ma20  <= a.close_price \
and b.ma30  <= a.close_price \
and b.ma60  <= a.close_price \
and b.ma150 <= a.close_price \
and b.macd >= -0.05 \
and b.diff >= -0.02 \
and b.dea  >= -0.02 \
order by 2 desc,1"


    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        log_debug("df: \n%s", df)
        return df


def work():
    db = db_init()

    # step1: get from web
    stocks = get_cross6(db)

    log_debug("df:\n%s", stocks)

    if stocks is None:
        log_info("not found!")
    else:
        stocks.set_index('stock_id', inplace=True)
        check_chance(stocks, db)


    db_end(db)


#######################################################################

def main():
    sailog_set("ma_cross6.log")

    log_info("let's begin here!")

    # check holiday
    if sai_is_product_mode():
        if today_is_weekend():
            log_info("today is weekend, exit")
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


# ma_corss6.py
