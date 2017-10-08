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

#######################################################################
# thrap trigger
#######################################################################


def get_open_gap_list(_trade_date, _good_type, _db):
    sql = "select * from tbl_watch a \
where  a.pub_date  = '%s' \
and    a.good_type = '%s' " % (_trade_date, _good_type)

    """
    sql = "select * from tbl_watch a \
where  a.good_type = '%s' " % (_good_type)
    """

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        # df.set_index("stock_id", inplace=True)
        return df

def get_that_price(_stock_id, _stock_date, _db):
    sql = "select open_price, close_price, high_price from tbl_day \
where stock_id='%s' \
and pub_date = '%s'" % (_stock_id, _stock_date)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return 0, 0, 0
    elif df.empty:
        return 0, 0, 0
    else:
        open_price  = df.iloc[0, 0]
        close_price = df.iloc[0, 1]
        high_price  = df.iloc[0, 2]
        return open_price, close_price, high_price


def get_next_price(_stock_id, _stock_date, _db):
    sql = "select open_price, close_price, high_price from tbl_day \
where stock_id='%s' \
and pub_date > '%s' order by pub_date limit 1" % (_stock_id, _stock_date)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return 0, 0, 0
    elif df.empty:
        return 0, 0, 0
    else:
        open_price  = df.iloc[0, 0]
        close_price = df.iloc[0, 1]
        high_price  = df.iloc[0, 2]
        return open_price, close_price, high_price

def work_one(_stock_id, _row, _db):
    rs = False
    to_mail = False
    content = ""

    # that day
    stock_date = _row['pub_date']
    that_open, that_close, that_high = get_that_price(_stock_id, stock_date, _db)
    log_info("%s, %s => that --- open[%.2f], close[%.2f], high[%.2f]", _stock_id, stock_date, that_open, that_close, that_high)
    if that_open <= 0 or that_close <= 0:
        log_error("error: can't get the price: %.2f, %.2f", that_open, that_close)
        return rs

    # TEST mode
    is_test_mode = True
    is_test_mode = False

    # this day: open price
    if is_test_mode:
        this_open, this_close, this_high = get_next_price(_stock_id, stock_date, _db)
        log_info("%s, %s => this --- open[%.2f], close[%.2f], high[%.2f]", _stock_id, stock_date, this_open, this_close, this_high)
        if this_open <= 0 or this_close <= 0:
            log_error("error: can't get the price: %.2f, %.2f", this_open, this_close)
            return rs
        open_price = this_open
        curr_price = this_close
    else:
        open_price = get_open_price(_stock_id)
        curr_price = get_curr_price(_stock_id)

    expect_price = _row['expect_price']
    to_buy_price = expect_price + 0.01 # XXX

    log_info(" expect-price: %.2f", expect_price)
    log_info(" to-buy-price: %.2f", to_buy_price)
    log_info("   open-price: %.2f", open_price)

    curr_date = get_today()
    curr_time = get_time()

    if open_price > that_high and curr_price > that_high and curr_price > open_price:
        subject = "gap-高高: %s#%s %s" % (_stock_id, curr_date, curr_time)
        to_mail = True
        rs = True
        log_info("nice: price-reached: open %.2f > %.2f high", open_price, that_high)
    elif open_price > to_buy_price and curr_price > to_buy_price and curr_price > open_price:
        subject = "gap-高开: %s#%s %s" % (_stock_id, curr_date, curr_time)
        to_mail = True
        rs = True
        log_info("nice: price-reached: open %.2f > %.2f expect", open_price, to_buy_price)
    else:
        to_mail = False
        rs = False
        log_debug("sorry: price not match: open %.2f < %.2f expect", open_price, to_buy_price)

    if to_mail:
        # subject = "gap-高开: %s#%s %s" % (_stock_id, curr_date, curr_time)
        content += "建议买入: %.2f元+\n\n" % (open_price)
        content += "昨收: %.2f元\n" % (that_close)
        content += "昨高: %.2f元\n" % (that_high)
        content += "昨开: %.2f元\n" % (that_open)
        content += "今开: %.2f元\n" % (open_price)
        content += "柱体差值: %.2f元\n\n" % (open_price - expect_price)
        content += _row['message']
        log_info("subject: \n%s", subject)
        log_info("mail: \n%s", content)
        saimail_dev(subject, content)
        # saimail2(subject, content)

    return rs


def xxx(_db):
    has_noticed = {}

    if sai_is_product_mode():
        last_date = get_date_by(-1)
        last_date = "2017-09-14"
        last_date = get_newest_trade_date(_db)
        watch_type = "thrap"
    else:
        last_date = "2017-09-05"
        watch_type = "thrap"


    log_info("date: [%s]", last_date)

    list_df = get_open_gap_list(last_date, watch_type, _db)
    if list_df is None:
        log_error("error: get_open_gap_list failure")
        return -1
    elif list_df.empty:
        log_error("[%s] no open_gap data", last_date)
        return 1
    else:
        log_debug("list df: \n%s", list_df)


    # 
    for row_index, row in list_df.iterrows():
        stock_id   = row['stock_id']
        log_debug("--------------------------------------")
        log_debug("------------[%s]------------------", stock_id)

        if has_noticed.has_key(stock_id):
            log_debug("%s already done", stock_id)
            continue
        else:
            has_trigger = work_one(stock_id, row, _db)
            if has_trigger:
                has_noticed[stock_id] = 1
                log_debug("mark: %s as has done", stock_id)
        # for


    return 0


def work():
    db = db_init()

    xxx(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("open_gap.log")

    log_info("let's begin here!")

    if sai_is_product_mode():
        if today_is_weekend():
            log_info("today is weekend, exit")
            # work()
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


# open_gap.py
