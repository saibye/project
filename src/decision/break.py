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
# 策略：横盘突破，涨停为界
#  600698 -- 2017-1-3
#
#
#######################################################################

"""
"""
def get_one_list(_stock_id, _trade_date, _db):
    recent = 60
    sql = "select pub_date, open_price, close_price, low_price, high_price, \
last_close_price, deal_total_count vol, \
round((close_price-open_price)/last_close_price*100, 2) rate, \
round((high_price - low_price)/last_close_price*100, 2) amp, \
round((open_price - low_price)/last_close_price*100, 2) dis \
from tbl_day \
where stock_id = '%s' \
and pub_date <= '%s' \
order by pub_date desc limit %d " % (_stock_id, _trade_date, recent)

    log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        df.set_index("pub_date", inplace=True)
        return df


def work_one(_stock_id, _max_date, _db):

    detail_df = get_one_list(_stock_id, _max_date, _db)
    if detail_df is None:
        log_error("error: get_one_list failure")
        return -1
    else:
        # log_debug("list df: \n%s", detail_df)
        pass

    high_list = []
    low_list  = []

    times = 0
    good_to_end = 0
    for row_index, row in detail_df.iterrows():
        trade_date  = row_index
        close_price = row['close_price']
        open_price  = row['open_price']
        low_price   = row['low_price']
        high_price  = row['high_price']
        last_close_price = row['last_close_price']

        rate = (close_price / last_close_price -1) * 100
        log_debug("[%s] ==> %-3.2f%%", trade_date, rate)

        if rate >= 9.8:
            times += 1
            if times == 1:
                log_debug("[%s]本次涨停，开始往前")
            else:
                log_debug("[%s]上次涨停，结束遍历")
                good_to_end = 1
        else:
            high_list.append(high_price)
            low_list.append(low_price)
            # close_list.append(close_price)
            # open_list.append(open_price)
            # high_list.append(high_price)
            # low_list.append(low_price)
            pass

        if good_to_end:
            log_info("nice: good_to_end: let's end")
            break

    log_info("counter: [%d]", len(high_list))

    high_desc = heapq.nlargest(5, high_list)
    low_asc   = heapq.nsmallest(5, low_list)
    log_info("high_list: [%s]", high_desc)
    log_info("low_list:  [%s]", low_asc)
    rate1 = (high_desc[0] / low_asc[0] - 1) * 100  # 最大/最小
    rate2 = (high_desc[3] / low_asc[3] - 1) * 100  # 排除前三
    log_info("rate1: [%.2f]", rate1)
    log_info("rate2: [%.2f]", rate2)

    return 0


def xxx(_db):

    if sai_is_product_mode():
        max_date = get_today()
    else:
        max_date = "2017-01-03"

    max_date = "2017-01-03"

    stock_id = "600698"
    work_one(stock_id, max_date, _db)


    return 0


def work():
    db = db_init()

    xxx(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("break.log")

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


# break.py
