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

from case1   import *
from case2   import *
from case3   import *
from case4   import *
from case5   import *
from case6   import *
from case7   import *
from case8   import *

#######################################################################
#
#######################################################################

g_detail_fetched = 150
g_detail_used    = 100


def CupWithHandle_work_one_day_stock(_stock_id, _till,  _db):

    global g_detail_fetched 
    global g_detail_used

    log_debug("=====[%s, %s]=====", _stock_id, _till)

    # 获取明细数据
    # 之前n1单位的交易数据
    n1 = g_detail_fetched
    detail_df = get_CupWithHandle_detail(_stock_id, _till, n1, _db);
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
    rv = CupWithHandle_format_ref(_stock_id, detail_df)
    if rv < 0:
        log_error("error: CupWithHandle_format_ref: %s", _stock_id)
        return -1

    used_len = g_detail_used
    my_df = detail_df.head(used_len)

    # case1
    """
    """
    rv = CupWithHandle_analyzer1(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice1: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case2
    rv = CupWithHandle_analyzer2(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice2: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case3
    rv = CupWithHandle_analyzer3(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice3: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case4
    rv = CupWithHandle_analyzer4(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice4: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case5
    rv = CupWithHandle_analyzer5(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice5: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case6
    rv = CupWithHandle_analyzer6(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice6: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case7
    rv = CupWithHandle_analyzer7(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice7: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    # case8
    rv = CupWithHandle_analyzer8(_stock_id, _till, my_df, used_len, _db)
    if rv == 0:
        log_info("nice8: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    return 1


def get_CupWithHandle_detail(_stock_id, _pub_date, _n, _db):
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


def get_CupWithHandle_stock_list(_till, _db):
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




def CupWithHandle_work_one_day(_till_date, _db):

    log_info("date: %s", _till_date)

    list_df = get_CupWithHandle_stock_list(_till_date, _db)
    if list_df is None:
        log_error("error: get_CupWithHandle_stock_list failure")
        return -1
    else:
        # log_debug("list df:\n%s", list_df)
        pass

    begin = get_micro_second()

    for row_index, row in list_df.iterrows():

        stock_id = row_index

        # log_debug("==============================")

        CupWithHandle_work_one_day_stock(stock_id, _till_date, _db)

    log_info("DAY [%s] costs %d us", _till_date, get_micro_second() - begin)

    return 0


def regression(_db):

    # all
    max_date = "2017-06-26"
    days = 200


    # 600191 @ 2017-07-05
    max_date = "2017-07-05"
    days = 1

    # 000488  @ 2017-06-26
    max_date = "2017-06-26"
    days = 1

    #
    max_date = "2017-07-21"
    days = 30

    #
    max_date = "2017-08-10"
    days = 26

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
        CupWithHandle_work_one_day(till_date, _db)

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
        log_info("till_date: %s", till_date)
        CupWithHandle_work_one_day(till_date, db)

        """
        # 沧州大化 1 done
        till_date = "2017-07-10"
        stock_id  = "600230"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 华资实业 2 done
        till_date = "2017-07-05"
        stock_id  = "600191"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 敦煌种业 3 done
        till_date = "2017-07-18"
        stock_id  = "600354"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 方大碳素 4 case2 done
        till_date = "2017-05-11"
        stock_id  = "600516"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 洛阳钼业 5 case2 done
        till_date = "2017-07-05"
        stock_id  = "603993"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 东湖高新 6 done
        till_date = "2017-07-17"
        stock_id  = "600133"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 天茂集团 7 done
        till_date = "2017-07-05"
        stock_id  = "000627"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 晨鸣纸业 8 done
        till_date = "2017-06-26"
        stock_id  = "000488"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 中天金融 9
        till_date = "2017-07-17"
        stock_id  = "000540"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 南钢股份
        till_date = "2017-07-18"
        stock_id  = "600282"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 云铝股份
        till_date = "2017-07-17"
        stock_id  = "000807"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 凌钢股份
        till_date = "2017-07-19"
        stock_id  = "600231"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 本板钢材
        till_date = "2017-07-31"
        stock_id  = "000761"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 中孚实业
        till_date = "2017-07-31"
        stock_id  = "600595"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 紫金矿业
        till_date = "2017-07-26"
        stock_id  = "601899"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 怡球资源
        till_date = "2017-07-31"
        stock_id  = "601388"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 中国铝业
        till_date = "2017-07-17"
        stock_id  = "601600"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 华新水泥
        till_date = "2017-07-07"
        stock_id  = "600801"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 西山煤电
        till_date = "2017-07-17"
        stock_id  = "000983"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 杭氧股份
        till_date = "2017-08-10"
        stock_id  = "002430"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)
        """

    else:
        regression(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("CupWithHandle0.log")

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

# CupWithHandle.py
