#!/usr/bin/env python
# -*- encoding: utf8 -*-

import heapq

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
# 策略： 向上跳空
#  600698 -- 2016-1-3   rate1: 19.87, rate2: 14.65, cnt: 57
#######################################################################

"""
"""
def get_one_list(_stock_id, _trade_date, _db):
    recent = 100
    sql = "select pub_date, open_price, close_price, low_price, high_price, \
last_close_price, deal_total_count vol, \
round((close_price-open_price)/last_close_price*100, 2) rate, \
round((high_price - low_price)/last_close_price*100, 2) amp, \
round((open_price - low_price)/last_close_price*100, 2) dis \
from tbl_day \
where stock_id = '%s' \
and pub_date <= '%s' \
order by pub_date desc limit %d " % (_stock_id, _trade_date, recent)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        df.set_index("pub_date", inplace=True)
        return df


def work_one_stock(_stock_id, _max_date, _db):
    rv = 0

    detail_df = get_one_list(_stock_id, _max_date, _db)
    if detail_df is None:
        log_error("error: get_one_list failure")
        return -1
    else:
        # log_debug("list df: \n%s", detail_df)
        pass

    log_info("%s -- %s", _stock_id, _max_date)
    high_list = []
    low_list  = []

    content = ""

    max_high = -9999
    max_date = ""
    min_low  = 9999
    min_date = ""
    next_low = -1
    next_high = -1
    counter  = 0
    high_price = 100
    for row_index, row in detail_df.iterrows():
        trade_date  = row_index
        close_price = row['close_price']
        open_price  = row['open_price']
        low_price   = row['low_price']
        high_price  = row['high_price']
        last_close_price = row['last_close_price']

        counter = counter + 1

        rate = (close_price / last_close_price -1) * 100
        # log_debug("[%s] ==> %-3.2f%%", trade_date, rate)

        if next_low > high_price:
            rt_all = (max_high - min_low) / min_low * 100
            rt_min = (min_low - high_price) / high_price * 100
            rt_gap = (next_low- high_price) / high_price * 100
            log_info(" [%s] upgap [%.2f%%], upmin [%.2f%%]", trade_date, rt_gap, rt_min)
            log_info(" ---- min_low  [%.2f][%s], this_high[%.2f]", min_low, min_date, high_price)
            log_info(" ---- max_high [%.2f][%s], rt[%.2f%%]", max_high, max_date, rt_all)
            days_on_market = get_day_to_market(_stock_id, trade_date, _db)
            if min_low > high_price and days_on_market > 100 and counter > 90 and rt_gap >= 2 and rt_all <= 30:
                content =  "## %s ##\n" % (_stock_id)
                content += "## nice: 向上跳空于[%s] ##\n" % (trade_date)
                content += "## nice: [%d]天未回补 幅度[%.2f%%] ##\n" % (counter, rt_min)
                log_info("\n%s", content)
                break
        elif next_high < low_price:
            log_info("[%s] downgap", trade_date)
        else:
            # log_debug("[%s]没有跳空", trade_date)
            pass

        if low_price  < min_low:
            min_low = low_price
            min_date=trade_date

        if high_price > max_high:
            max_high=high_price
            max_date=trade_date

        next_low  = low_price
        next_high = high_price
        # end of for


    log_info("-------------------------------------------------------------")

    return 0


"""
获取指定日期股票列表 2017-4-9
"""
def get_stock_list_by_date(_date, _db):
    sql = "select distinct stock_id from tbl_day \
where pub_date='%s' \
order by 1" % (_date)

    df = pd.read_sql_query(sql, _db);

    if df is None:
        return None

    return df.set_index('stock_id')


def xxx(_db):

    if sai_is_product_mode():
        trade_date = get_today()
        trade_date = "2017-01-03"
        trade_date = "2016-12-30"
        trade_date = "2017-04-20"
    else:
        trade_date = "2017-01-03"
        trade_date = "2016-12-30"
        trade_date = "2017-04-20"

    log_debug("trade_date: %s", trade_date)
    list_df = get_stock_list_by_date(trade_date, _db)
    if list_df is None:
        log_error("error: get_one_list failure")
        return -1
    else:
        log_debug("list df: \n%s", list_df)
        pass

    for row_index, row in list_df.iterrows():
        stock_id = row_index
        # stock_id = "600698"
        work_one_stock(stock_id, trade_date, _db)
        # break

    return 0


def work():
    db = db_init()

    xxx(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("gap.log")

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

# gap.py
