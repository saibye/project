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
# 不需要macd等,  所以只使用tbl_day表 2016/11/26
#######################################################################


def get_v1_list(_db):
    sql = "select distinct stock_id from tbl_day where pub_date = (select max(pub_date) from tbl_day)"

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        df.set_index("stock_id", inplace=True)
        return df


def get_v1_min(_stock_id, _n1, _n2, _db):
    sql = "select pub_date, deal_total_count \
from tbl_day a where a.stock_id = '%s'\
and a.pub_date >= (select min(pub_date) from \
        ( select pub_date from tbl_day \
          where stock_id = '%s' \
          order by pub_date desc limit %d) t1)\
and deal_total_count = \
    (select min(deal_total_count) \
     from tbl_day b where b.stock_id = '%s' \
     and b.pub_date >= (select min(pub_date) from \
         ( select pub_date from tbl_day \
           where stock_id = '%s' \
           order by pub_date desc limit %d) t1))\
and (select min(deal_total_count) from tbl_day b\
    where b.stock_id = '%s'\
    and b.pub_date >= (select min(pub_date) from \
        ( select pub_date from tbl_day \
          where stock_id = '%s' \
          order by pub_date desc limit %d) t1)) = \
    (select min(deal_total_count) from tbl_day b \
     where b.stock_id = '%s' \
     and b.pub_date >= (select min(pub_date) from \
         ( select pub_date from tbl_day \
           where stock_id = '%s' \
           order by pub_date desc limit %d) t1)) \
order by pub_date desc limit 1" % (_stock_id, _stock_id, _n1, \
    _stock_id, _stock_id, _n1, \
    _stock_id, _stock_id, _n1, \
    _stock_id, _stock_id, _n2)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        # df.set_index("pub_date", inplace=True)
        # log_debug("min df: \n%s", df)
        return df


def get_v1_detail(_stock_id, _pub_date, _n1, _db):
    sql = "select pub_date, open_price, close_price, deal_total_count, last_close_price \
from tbl_day a where a.stock_id  = '%s' and   a.pub_date >= '%s' \
order by pub_date limit %d" % (_stock_id, _pub_date, _n1)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        # df.set_index("pub_date", inplace=True)
        # log_debug("detail df: \n%s", df)
        return df


def work_one(_stock_id, _db):

    log_info("work_one begin")

    good = 0
    vr1   = 0.0
    rate1 = 0.0
    vr2   = 0.0
    rate2 = 0.0
    one   = ""
    two   = ""

    begin = get_micro_second()

    n1 = 3
    n2 = 30
    n3 = 3

    # min(volume), pub_date
    date_df = get_v1_min(_stock_id, n1, n2, _db)
    if date_df is None:
        log_info("n1(%d), n2(%d) not match!", n1, n2)
        return -1
    elif date_df.empty:
        log_debug("date_df is empty: [%d]", len(date_df))
        return 1
    else:
        # log_debug("min: len[%d]\n%s", len(date_df), date_df)
        min_date = date_df.iloc[0, 0]
        min_vol  = date_df.iloc[0, 1]
        log_debug("min_date: [%s]", min_date)
        log_debug("min_vol:  [%s]", min_vol)

    if min_vol < 0.0001:
        log_info("volume too small: [%.4f]", min_vol)
        return 1

    # 之后n天的交易数据
    detail_df = get_v1_detail(_stock_id, min_date, n3, _db);
    if detail_df is None:
        log_info("[%s, %s, %s] detail is none", _stock_id, min_date, min_vol)
        return -1
    elif detail_df.empty:
        log_debug("detail_df is empty: [%d]", len(detail_df))
        return 1
    else:
        log_debug("min: len[%d]\n%s", len(detail_df), detail_df)

    length = len(detail_df)

    vol0   = detail_df['deal_total_count'][0]
    date0  = detail_df['pub_date'][0]
    open0  = detail_df['open_price'][0]
    close0 = detail_df['close_price'][0]
    last0  = detail_df['last_close_price'][0]
    log_debug("volume0: [%.3f]", vol0)

    rate0  = (close0 - last0) / last0 * 100
    if rate0 > 9.9:
        log_info("xxoo 无量涨停")
        return 1

    if length >= 2:
        vol1   = detail_df['deal_total_count'][1]
        date1  = detail_df['pub_date'][1]
        open1  = detail_df['open_price'][1]
        close1 = detail_df['close_price'][1]
        rate1  = (close1 - close0) / close0 * 100
        vr1    = vol1 / vol0
        one    = "[%s]涨幅1: [%.2f], 量比1: [%.2f]" % (date1, rate1, vr1)
        log_debug("one: %s", one)

    if length >= 3:
        vol2   = detail_df['deal_total_count'][2]
        date2  = detail_df['pub_date'][2]
        open2  = detail_df['open_price'][2]
        close2 = detail_df['close_price'][2]
        rate2  = (close2 - close1) / close1 * 100
        vr2    = vol2 / vol0
        two    = "[%s]涨幅2: [%.2f], 量比2: [%.2f]" % (date2, rate2, vr2)
        log_debug("two: %s", two)

    # 检查量比
    if (rate1 > 0 and vr1 >= 10) or (rate2 > 0 and vr2 >= 10):
        log_info("nice, a chance: [%s], since: [%s]", _stock_id, min_date)
        item  = "%s 地量: [%.3f]@[%s]" % (_stock_id, vol0, min_date)
        xsg   = get_xsg_info(_stock_id, _db)
        item += "\n%s\n%s\n%s" % (one, two, xsg)
        subject  = "diliang: %s" % (min_date)
        # content += item
        log_info("subject: \n%s", subject)
        log_info("content: \n%s", item)
        if sai_is_product_mode():
            saimail(subject, item)
        sai_save_good(_stock_id, date0, "diliang", min_vol, vr1, vr2, min_date, _db)
    else :
        log_info("sorry... [%s]", _stock_id)

    log_info("it costs %d us", get_micro_second() - begin)

    return 0


def xxx(_db):

    list_df = get_v1_list(_db)
    if list_df is None:
        log_error("error: get_v1_list failure")
        return -1
    else:
        log_debug("list df: \n%s", list_df)

    for row_index, row in list_df.iterrows():
        stock_id = row_index
        log_debug("[%s]------------------", stock_id)
        rv = work_one(stock_id, _db)

    return 0




def work():
    db = db_init()

    xxx(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("v1.log")

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


# v1.py
