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

from pub_pre_thrive import *
from case1   import *
from case2   import *
from case3   import *
from case4   import *
from case5   import *
from case6   import *

#######################################################################
#
#######################################################################

g_detail_fetched = 150
g_detail_used    = 100


def pre_thrive_work_one_day_stock(_stock_id, _till,  _db):

    global g_detail_fetched 
    global g_detail_used

    log_debug("=====[%s, %s]=====", _stock_id, _till)

    # 获取明细数据
    # 之前n1单位的交易数据
    n1 = g_detail_fetched
    detail_df = get_pre_thrive_detail(_stock_id, _till, n1, _db);
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
    rv = pre_thrive_format_ref(_stock_id, detail_df)
    if rv < 0:
        log_error("error: pre_thrive_format_ref: %s", _stock_id)
        return -1
    """

    used_len = g_detail_used
    my_df = detail_df.head(used_len)

    # case1
    rv = pre_thrive_analyzer1(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice1: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case2
    rv = pre_thrive_analyzer2(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice2: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case3
    rv = pre_thrive_analyzer3(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice3: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case4
    rv = pre_thrive_analyzer4(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice4: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case5
    rv = pre_thrive_analyzer5(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice5: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case6
    rv = pre_thrive_analyzer6(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice6: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    log_debug("-------------------------------------------------")

    return 1


def get_pre_thrive_detail(_stock_id, _pub_date, _n, _db):
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


def get_pre_thrive_stock_list(_till, _db):
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




def pre_thrive_work_one_day(_till_date, _db):

    log_info("date: %s", _till_date)

    list_df = get_pre_thrive_stock_list(_till_date, _db)
    if list_df is None:
        log_error("error: get_pre_thrive_stock_list failure")
        return -1
    else:
        # log_debug("list df:\n%s", list_df)
        pass

    begin = get_micro_second()

    for row_index, row in list_df.iterrows():

        stock_id = row_index

        # log_debug("==============================")

        pre_thrive_work_one_day_stock(stock_id, _till_date, _db)

    log_info("DAY [%s] costs %d us", _till_date, get_micro_second() - begin)

    return 0


def regression(_db):

    #
    max_date = "2017-08-30"
    days = 2

    max_date = "2017-09-07"
    days = 20

    max_date = "2017-09-16"
    days = 20

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
        pre_thrive_work_one_day(till_date, _db)

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
        till_date = "2018-09-18"
        log_info("till_date: %s", till_date)
        pre_thrive_work_one_day(till_date, db)

        """
        # case1
        # 中孚信息 300659
        stock_id  = "300659"
        till_date = "2017-08-30"
        pre_thrive_work_one_day_stock(stock_id, till_date, db)

        # 韩建河山 603616
        till_date = "2017-04-24"
        stock_id  = "603616"
        pre_thrive_work_one_day_stock(stock_id, till_date, db)

        # 万科A 000002
        till_date = "2016-08-11"
        stock_id  = "000002"
        pre_thrive_work_one_day_stock(stock_id, till_date, db)

        # 西部建设 002302
        till_date = "2017-01-16"
        stock_id  = "002302"
        pre_thrive_work_one_day_stock(stock_id, till_date, db)

        # 东方铁塔 002545
        till_date = "2017-08-04"
        stock_id  = "002545"
        pre_thrive_work_one_day_stock(stock_id, till_date, db)

        # 青山纸业 600103
        till_date = "2017-07-11"
        stock_id  = "600103"
        pre_thrive_work_one_day_stock(stock_id, till_date, db)

        # 九鼎新材 002201 # case2
        till_date = "2017-09-05"
        stock_id  = "002201"
        pre_thrive_work_one_day_stock(stock_id, till_date, db)

        # 达安股份 case3
        till_date = "2017-09-06"
        stock_id  = "300635"
        pre_thrive_work_one_day_stock(stock_id, till_date, db)

        # 科大国创 case4 done
        till_date = "2017-09-11"
        stock_id  = "300520"
        pre_thrive_work_one_day_stock(stock_id, till_date, db)

        # 盈方微
        till_date = "2017-09-11"
        stock_id  = "000670"
        pre_thrive_work_one_day_stock(stock_id, till_date, db)

        # 溢多利
        till_date = "2017-09-13"
        stock_id  = "300381"
        pre_thrive_work_one_day_stock(stock_id, till_date, db)
        """

    else:
        regression(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("pre_thrive5.log")

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

# pre_thrive.py
