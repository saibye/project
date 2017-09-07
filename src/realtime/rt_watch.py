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
# pre-thrive trigger
#######################################################################


def get_watch_list(_trade_date, _good_type, _db):
    sql = "select * from tbl_watch a \
where  a.pub_date  = '%s' \
and    a.good_type = '%s' " % (_trade_date, _good_type)

    log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        # df.set_index("stock_id", inplace=True)
        return df

def work_one(_stock_id, _row, _db):
    rs = False
    to_mail = False
    content = ""

    expect_price = _row['expect_price']
    to_buy_price = expect_price + 0.1 # XXX
    curr_price = get_curr_price(_stock_id)
    log_info(" expect-price: %.2f", expect_price)
    log_info(" to-buy-price: %.2f", to_buy_price)
    log_info("current-price: %.2f", curr_price)

    if curr_price > to_buy_price:
        to_mail = True
        rs = True
        log_info("nice: price-reached: curr %.2f > %.2f expect", curr_price, to_buy_price)
    else:
        to_mail = False
        rs = False
        log_debug("sorry: price not match: curr %.2f < %.2f expect", curr_price, to_buy_price)

    if to_mail:
        curr_date = get_today()
        curr_time = get_time()
        subject = "pre-thrive: %s#%s %s" % (_stock_id, curr_date, curr_time)
        content += "建议买入: %.2f元+\n\n" % (to_buy_price)
        content += _row['message']
        log_info("subject: \n%s", subject)
        log_info("mail: \n%s", content)
        saimail_dev(subject, content)
        saimail2(subject, content)

    return rs


def xxx(_db):
    has_noticed = {}

    if sai_is_product_mode():
        last_date = get_date_by(-1)
        last_date = "2017-08-30"
        last_date = get_newest_trade_date(_db)
        watch_type = "pre-thrive"
    else:
        last_date = "2017-09-05"
        watch_type = "pre-thrive"


    log_info("date: [%s]", last_date)

    list_df = get_watch_list(last_date, watch_type, _db)
    if list_df is None:
        log_error("error: get_watch_list failure")
        return -1
    elif list_df.empty:
        log_error("[%s] no watch data", last_date)
        return 1
    else:
        log_debug("list df: \n%s", list_df)

    end_time  = '15:05:00'
    # end_time  = '23:05:00'
    lun_time1 = '11:40:00'
    lun_time2 = '13:00:00'

    counter  = 0
    while 1:
        counter = counter + 1

        curr = get_time()

        # 中午休息
        if curr >= lun_time1 and curr <= lun_time2:
            log_info("'%s' means noon time", curr)
            time.sleep(300)
            continue

        log_info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

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

        # 当日结束
        curr = get_time()
        if curr >= end_time:
            log_info("'%s' means end today", curr)
            break

        time.sleep(300)
        # time.sleep(20)

        # while


    return 0




def work():
    db = db_init()

    xxx(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("watch.log")

    log_info("let's begin here!")

    if sai_is_product_mode():
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

#######################################################################


# watch.py
