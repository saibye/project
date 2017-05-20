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
# dadan3 back ma20
#######################################################################


# 2017-3-30 ma20 only
def get_good_list(_trade_date, _good_type, _db):
    sql = "select a.pub_date event_date, a.stock_id, b.pub_date back_date, \
a.v1 volume, a.v2 price, a.v4 time \
from tbl_good a, tbl_day b, tbl_day_tech c \
where a.stock_id = b.stock_id \
and   b.stock_id = c.stock_id \
and   b.pub_date = c.pub_date \
and   b.pub_date>= a.pub_date \
and   (c.ma20<= b.high_price and c.ma20 >= b.low_price) \
and   b.close_price >= b.open_price \
and   a.good_type = '%s' \
and   b.pub_date  = '%s' \
and   a.pub_date in \
(select * from (select distinct pub_date from tbl_good order by pub_date desc limit 20) x)" % (_good_type, _trade_date)

    log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        # df.set_index("stock_id", inplace=True)
        return df

def work_one(_stock_id, _row, _db):

    log_info("work_one begin")

    begin = get_micro_second()

    if sai_is_product_mode():
        saimail(subject, item)

    log_info("it costs %d us", get_micro_second() - begin)

    return 0


def xxx(_db):
    has_noticed = {}

    if sai_is_product_mode():
        last_date = get_date_by(-1)
        good_type = "dadan3"
    else:
        last_date = "2016-11-29"
        good_type = "dadan2"
        last_date = "2016-12-22"
        good_type = "dadan3"
        last_date = "2017-05-17"

    list_df = get_good_list(last_date, good_type, _db)
    if list_df is None:
        log_error("error: get_good_list failure")
        return -1
    elif list_df.empty:
        log_error("[%s] no good data", last_date)
        return 1
    else:
        log_debug("list df: \n%s", list_df)

    content = "需要:\n"
    content+= "1. 均线向上发散: MA20\n"
    content+= "2. MA5, 10, 20相近\n"
    content+= "3. 新股更佳\n\n"
    for row_index, row in list_df.iterrows():
        stock_id   = row['stock_id']
        log_debug("[%s]------------------", stock_id)
        if has_noticed.has_key(stock_id):
            log_debug("%s already done", stock_id)
            continue
        else:
            has_noticed[stock_id] = "1"

        volume     = row['volume']
        price      = row['price']
        event_time = row['time']
        event_date = row['event_date']
        back_date  = row['back_date']
        one = "%s\n" % (event_date)
        one+= "[%s] 最新[%.2f]元 涨幅[%.2f%%]\n" % (stock_id, get_curr_price(stock_id), get_chg_rate(stock_id))
        one+= "[%s] 当时[%.2f]元 成交[%.2f]万手\n发生时间[%s %s]\n回归时间[%s]\n\n" % (stock_id, price, volume/10000.00, event_date, event_time, back_date)
        one+= get_basic_info_all(stock_id, _db)
        one+= "++++++++++++++++++++++++++++++++++++++\n"
        content += "%s\n" % (one)

    subject = "dd3-back20: %s" % (last_date)
    log_info("subject: \n%s", subject)
    log_info("content: \n%s", content)
    saimail(subject, content)

    return 0




def work():
    db = db_init()

    xxx(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("good.log")

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


# good.py
