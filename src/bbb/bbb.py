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
from saitech import *

from pub_bbb import *
from case1   import *
from case2   import *
from case3   import *


#######################################################################
#
#######################################################################

g_detail_fetched = 400
g_detail_used    = 100


def bbb_work_one_day_stock(_stock_id, _till,  _db):

    global g_detail_fetched 
    global g_detail_used

    log_debug("=====[%s, %s]=====", _stock_id, _till)

    # 获取明细数据
    # 之前n1单位的交易数据
    n1 = g_detail_fetched
    detail_df = get_bbb_detail(_stock_id, _till, n1, _db);
    if detail_df is None:
        log_info("[%s, %s] detail is none", _stock_id, _till)
        return -1
    elif detail_df.empty:
        log_debug("detail_df is empty: [%d]", len(detail_df))
        return 1
    else:
        # log_debug("n1: len[%d]", len(detail_df))
        pass

    length = len(detail_df)
    if length < g_detail_used:
        log_info("data-not-enough: %s: %d", _stock_id, length)
        return 1

    # 格式化数据
    rv = bbb_format_ref(_stock_id, detail_df)
    if rv < 0:
        log_error("error: bbb_format_ref: %s", _stock_id)
        return -1

    used_len = g_detail_used
    used_len = g_detail_fetched
    my_df = detail_df.head(used_len)

    # case1
    rv = bbb_analyzer1(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice1: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case2
    rv = bbb_analyzer2(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice2: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case3
    rv = bbb_analyzer3(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice3: %s", _stock_id)
        return 0

    log_debug("-------------------------------------------------")

    return 1


def get_bbb_detail(_stock_id, _pub_date, _n, _db):
    sql = "select stock_id, pub_date, open_price, close_price, \
deal_total_count total, last_close_price last, \
high_price, low_price \
from tbl_day a \
where a.stock_id  = '%s' and a.pub_date <= '%s' \
order by pub_date desc limit %d" % (_stock_id, _pub_date, _n)

    # log_debug("detail-sql:\n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        return df


def get_bbb_stock_list(_till, _db):
    sql = "select distinct stock_id from tbl_day \
where pub_date = \
(select max(pub_date) from tbl_day \
where pub_date <= '%s')" % (_till)

    # log_debug("stock list sql:\n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _till)
        return None
    else:
        df.set_index("stock_id", inplace=True)
        return df




def bbb_work_one_day(_till_date, _db):

    log_info("date: %s", _till_date)

    list_df = get_bbb_stock_list(_till_date, _db)
    if list_df is None:
        log_error("error: get_bbb_stock_list failure")
        return -1
    else:
        # log_debug("list df:\n%s", list_df)
        pass

    begin = get_micro_second()

    for row_index, row in list_df.iterrows():

        stock_id = row_index

        # log_debug("==============================")

        bbb_work_one_day_stock(stock_id, _till_date, _db)

    log_info("DAY [%s] costs %d us", _till_date, get_micro_second() - begin)

    return 0


def regression(_db):

    #
    max_date = "2017-10-13"
    days = 1

    max_date = "2017-09-28"
    days = 1

    max_date = "2017-09-19"
    days = 1

    max_date = "2017-09-18"
    days = 1

    max_date = "2017-11-03"
    days = 10

    log_info("regress")

    date_df = get_recent_pub_date(max_date, days, _db)
    if date_df is None:
        log_error("error: get_recent_pub_date failure")
        return -1
    else:
        date_df.set_index("pub_date", inplace=True)

    for row_index, row in date_df.iterrows():
        till_date = row_index
        log_debug("[%s]------------------", till_date)
        bbb_work_one_day(till_date, _db)

    return 0


def work():
    db = db_init()

    """
    regression(db)
    return 0
    """

    if sai_is_product_mode():
        till_date = get_date_by(0)
        till_date = get_newest_trade_date(db)
        # till_date = "2017-08-25"
        log_info("till_date: %s", till_date)
        bbb_work_one_day(till_date, db)


        """

        # 国星光电 (weak) TODO
        till_date = "2017-10-23"
        stock_id  = "002449"
        bbb_work_one_day_stock(stock_id, till_date, db)

        # 健康元 done case3
        till_date = "2017-09-01"
        stock_id  = "600380"
        bbb_work_one_day_stock(stock_id, till_date, db)

        # 恒立液压  done case2
        till_date = "2017-11-01"
        stock_id  = "601100"
        bbb_work_one_day_stock(stock_id, till_date, db)

        # 士兰微 done case1
        till_date = "2017-09-19"
        stock_id  = "600460"
        bbb_work_one_day_stock(stock_id, till_date, db)

        # 永辉超市 done case1
        till_date = "2017-09-19"
        stock_id  = "601933"
        bbb_work_one_day_stock(stock_id, till_date, db)


        # 阳光电源 done case1
        till_date = "2017-09-13"
        stock_id  = "300274"
        bbb_work_one_day_stock(stock_id, till_date, db)


        # 京东方 done case1 -- all in all
        till_date = "2017-09-28"
        stock_id  = "000725"
        bbb_work_one_day_stock(stock_id, till_date, db)

        # 鸿特精密 done case1
        till_date = "2017-10-13"
        stock_id  = "300176"
        bbb_work_one_day_stock(stock_id, till_date, db)

        # 长春高新 done case1
        till_date = "2017-08-18"
        stock_id  = "000661"
        bbb_work_one_day_stock(stock_id, till_date, db)

        # 招商银行 done case1
        till_date = "2017-05-12"
        stock_id  = "600036"
        bbb_work_one_day_stock(stock_id, till_date, db)

        # 普利制药 done case1
        till_date = "2017-09-01"
        stock_id  = "300630"
        bbb_work_one_day_stock(stock_id, till_date, db)
        """

    else:
        regression(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("bbb1.log")

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

#######################################################################

main()

#######################################################################

# bbb.py
