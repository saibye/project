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

from pub_thrive import *
from case1   import *
from case2   import *
from case3   import *
from case4   import *
from case5   import *
from case6   import *
from case7   import *
from case8   import *
from case9   import *
from case10  import *

#######################################################################
#
#######################################################################

g_detail_fetched = 150
g_detail_used    = 100


def thrive_work_one_day_stock(_stock_id, _till,  _db):

    global g_detail_fetched 
    global g_detail_used

    log_debug("=====[%s, %s]=====", _stock_id, _till)

    # 获取明细数据
    # 之前n1单位的交易数据
    n1 = g_detail_fetched
    detail_df = get_thrive_detail(_stock_id, _till, n1, _db);
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
    if length < 8:
        log_info("data-not-enough: %s: %d", _stock_id, length)
        return 1

    """
    # 格式化数据
    rv = thrive_format_ref(_stock_id, detail_df)
    if rv < 0:
        log_error("error: thrive_format_ref: %s", _stock_id)
        return -1
    """

    used_len = g_detail_used
    my_df = detail_df.head(used_len)

    # case1
    rv = thrive_analyzer1(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice1: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case2
    rv = thrive_analyzer2(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice2: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case3
    rv = thrive_analyzer3(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice3: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case4
    rv = thrive_analyzer4(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice4: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case5 TODO FIXME 2017-9-5
    # rv = thrive_analyzer5(_stock_id, _till, my_df, used_len, _db)
    # if rv == 0:
    #    log_info("nice5: %s", _stock_id)
    #     return 0
    # log_debug("-------------------------------------------------")

    # case6
    rv = thrive_analyzer6(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice6: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case7
    rv = thrive_analyzer7(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice7: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case8
    rv = thrive_analyzer8(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice8: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case9
    rv = thrive_analyzer9(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice9: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case10
    rv = thrive_analyzer10(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice10: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    log_debug("-------------------------------------------------")

    return 1


def get_thrive_detail(_stock_id, _pub_date, _n, _db):
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


def get_thrive_stock_list(_till, _db):
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




def thrive_work_one_day(_till_date, _db):

    log_info("date: %s", _till_date)

    list_df = get_thrive_stock_list(_till_date, _db)
    if list_df is None:
        log_error("error: get_thrive_stock_list failure")
        return -1
    else:
        # log_debug("list df:\n%s", list_df)
        pass

    begin = get_micro_second()

    for row_index, row in list_df.iterrows():

        stock_id = row_index

        # log_debug("==============================")

        thrive_work_one_day_stock(stock_id, _till_date, _db)

    log_info("DAY [%s] costs %d us", _till_date, get_micro_second() - begin)

    return 0


def regression(_db):

    #
    max_date = "2017-09-06"
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
        thrive_work_one_day(till_date, _db)

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
        thrive_work_one_day(till_date, db)

        """

        # case1
        # 华泰股份 600308 done
        till_date = "2017-07-18"
        stock_id  = "600308"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 九鼎新材 002201
        till_date = "2017-08-25"
        stock_id  = "002201"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 东方铁塔 002545
        till_date = "2017-08-07"
        stock_id  = "002545"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 设计总院 603357
        till_date = "2017-08-10"
        stock_id  = "603357"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # CASE2
        # 韩建河山 603616
        till_date = "2017-04-25"
        stock_id  = "603616"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # CASE3
        # 西部建设
        till_date = "2017-01-17"
        stock_id  = "002302"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 迅游科技
        till_date = "2017-08-25"
        stock_id  = "300467"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 泸天化
        till_date = "2017-06-13"
        stock_id  = "000912"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 泸天化
        till_date = "2016-09-26"
        stock_id  = "000912"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 中孚信息
        till_date = "2017-08-31"
        stock_id  = "300659"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # CASE5
        # 水晶光电
        till_date = "2017-08-25"
        stock_id  = "002273"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 西部建设
        till_date = "2017-02-06"
        stock_id  = "002302"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 浙大网新
        till_date = "2017-08-31"
        stock_id  = "600797"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 中信国安
        till_date = "2017-08-29"
        stock_id  = "000839"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 露天煤业
        till_date = "2017-08-24"
        stock_id  = "002128"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 中国神华 discarded
        till_date = "2017-05-22"
        stock_id  = "601088"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 龙净环保 discared
        till_date = "2017-08-31"
        stock_id  = "600388"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 中科曙光
        till_date = "2017-08-28"
        stock_id  = "603019"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 先河环保
        till_date = "2017-04-24"
        stock_id  = "300137"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 神州泰岳
        till_date = "2017-08-28"
        stock_id  = "300002"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 先进数通
        till_date = "2017-09-01"
        stock_id  = "300541"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 建科院
        till_date = "2017-08-11"
        stock_id  = "300675"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 精工钢构
        till_date = "2017-08-28"
        stock_id  = "600496"
        thrive_work_one_day_stock(stock_id, till_date, db)

        # 万东医疗
        till_date = "2017-08-28"
        stock_id  = "600055"
        thrive_work_one_day_stock(stock_id, till_date, db)

        """

    else:
        regression(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("thrive.log")

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

# thrive.py
