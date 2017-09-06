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

from pub_u15m import *
from case1   import *

#######################################################################
#
#######################################################################

g_detail_fetched = 450
g_detail_used    = 400


def u15m_work_one_day_stock(_stock_id, _till,  _db):

    global g_detail_fetched 
    global g_detail_used

    log_debug("=====[%s, %s]=====", _stock_id, _till)

    # 获取明细数据
    # 之前n1单位的交易数据
    n1 = g_detail_fetched
    detail_df = get_u15m_detail(_stock_id, _till, n1, _db);
    if detail_df is None:
        log_info("[%s, %s] detail is none", _stock_id, _till)
        return -1
    elif detail_df.empty:
        log_debug("detail_df is empty: [%d]", len(detail_df))
        return 1
    else:
        log_debug("n1: len[%d]\n%s", len(detail_df), detail_df)
        pass

    length = len(detail_df)
    if length < g_detail_used:
        log_info("data-not-enough: %s: %d", _stock_id, length)
        return 1

    # 格式化数据
    rv = u15m_format_ref(_stock_id, detail_df)
    if rv < 0:
        log_error("error: u15m_format_ref: %s", _stock_id)
        return -1

    used_len = g_detail_used
    my_df = detail_df.head(used_len)

    log_debug("ref0: p[%.3f] -- v[%.3f]", ref_close(0), ref_vol(0))
    log_debug("ref1: p[%.3f] -- v[%.3f]", ref_close(1), ref_vol(1))
    log_debug("ref2: p[%.3f] -- v[%.3f]", ref_close(2), ref_vol(2))

    log_debug("ma0:  5[%.3f] - 10[%.3f] - 20[%.3f] - 200[%.3f]", ref_ma5(0), ref_ma10(0), ref_ma20(0), ref_ma200(0))
    log_debug("ma1:  5[%.3f] - 10[%.3f] - 20[%.3f] - 200[%.3f]", ref_ma5(1), ref_ma10(1), ref_ma20(1), ref_ma200(1))
    log_debug("ma2:  5[%.3f] - 10[%.3f] - 20[%.3f] - 200[%.3f]", ref_ma5(2), ref_ma10(2), ref_ma20(2), ref_ma200(2))

    log_debug("vma0: 5[%.3f] - 10[%.3f] - 50[%.3f]", ref_vma5(0), ref_vma10(0), ref_vma50(0))
    log_debug("vma1: 5[%.3f] - 10[%.3f] - 50[%.3f]", ref_vma5(1), ref_vma10(1), ref_vma50(1))
    log_debug("vma2: 5[%.3f] - 10[%.3f] - 50[%.3f]", ref_vma5(2), ref_vma10(2), ref_vma50(2))


    # case1
    rv = u15m_analyzer1(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice1: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    log_debug("-------------------------------------------------")

    return 1


def get_u15m_detail(_stock_id, _pub_date, _n, _db):
    sql = "select stock_id, pub_date_time, open_price, close_price, \
deal_total_count total, last_close_price last, \
high_price, low_price \
from tbl_15min a \
where a.stock_id  = '%s' and a.pub_date_time <= '%s' \
order by pub_date_time desc limit %d" % (_stock_id, _pub_date, _n)

    log_debug("detail-sql:\n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        return df


def get_u15m_stock_list(_till, _db):
    sql = "select distinct stock_id from tbl_15min \
where pub_date_time = \
(select max(pub_date_time) from tbl_day \
where pub_date_time <= '%s')" % (_till)

    # log_debug("stock list sql:\n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _till)
        return None
    else:
        df.set_index("stock_id", inplace=True)
        return df




def u15m_work_one_day(_till_date, _db):

    log_info("date: %s", _till_date)

    list_df = get_u15m_stock_list(_till_date, _db)
    if list_df is None:
        log_error("error: get_u15m_stock_list failure")
        return -1
    else:
        # log_debug("list df:\n%s", list_df)
        pass

    begin = get_micro_second()

    for row_index, row in list_df.iterrows():

        stock_id = row_index

        # log_debug("==============================")

        u15m_work_one_day_stock(stock_id, _till_date, _db)

    log_info("DAY [%s] costs %d us", _till_date, get_micro_second() - begin)

    return 0


def regression(_db):

    #
    max_date = "2017-09-01"
    days = 10

    log_info("regress")

    date_df = get_recent_pub_date(max_date, days, _db)
    if date_df is None:
        log_error("error: get_recent_pub_date failure")
        return -1
    else:
        date_df.set_index("pub_date_time", inplace=True)

    for row_index, row in date_df.iterrows():
        till_date = row_index
        log_debug("[%s]------------------", till_date)
        u15m_work_one_day(till_date, _db)

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
        # u15m_work_one_day(till_date, db)

        # 韵达股份 
        till_date = "2017-09-01 15:00:00"
        stock_id  = "002120"
        u15m_work_one_day_stock(stock_id, till_date, db)

        """
        # 隆基股份
        till_date = "2017-09-04"
        stock_id  = "601012"
        u15m_work_one_day_stock(stock_id, till_date, db)

        """

    else:
        regression(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("u15m0.log")

    log_info("let's begin here!")

    if sai_is_product_mode():
        if today_is_weekend():
            log_info("today is weekend, exit")
            work()
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

# u15m.py
