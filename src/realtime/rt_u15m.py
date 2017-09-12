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
# 15min-unit ma-law
#######################################################################



def work_one(_stock_id, _row, _db):
    rs = False
    to_mail = False
    content = ""

    begin = get_micro_second()

    try:
        df = ts.get_k_data(_stock_id, ktype='15', autype='qfq')
    except Exception:
        log_error("warn:error: %s get_k_data exception!", _stock_id)
        return -4

    # calc cost time
    log_info("get_k_data [%s] costs %d us", _stock_id, get_micro_second()-begin)

    if df is None :
        log_error("warn: stock %s is None, next", _stock_id)
        return -1

    if df.empty:
        log_error("warn: stock %s is empty, next", _stock_id)
        return -2

    df.sort_index(ascending=False, inplace=True)

    log_debug("\n%s", df)

    if to_mail:
        curr_date = get_today()
        curr_time = get_time()
        subject = "15-MA-law: %s#%s %s" % (_stock_id, curr_date, curr_time)
        content += "+++"
        log_info("subject: \n%s", subject)
        log_info("mail: \n%s", content)
        # saimail_dev(subject, content)
        # saimail2(subject, content)

    return rs


def get_u15m_list(_trade_date, _good_type, _db):
    sql = "select * from tbl_u15m a \
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


def xxx(_db):
    has_noticed = {}

    if sai_is_product_mode():
        last_date = get_date_by(-1)
        last_date = "2017-08-30"
        last_date = get_newest_trade_date(_db)
    else:
        last_date = "2017-09-05"


    log_info("date: [%s]", last_date)

    list_df = get_stock_list_df_tu() 
    if list_df is None:
        log_error("error: get list failure")
        return -1
    elif list_df.empty:
        log_error("[%s] no u15m data", last_date)
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
    sailog_set("u15m.log")

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


# u15m.py
