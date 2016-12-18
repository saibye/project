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
from saitu   import *

#######################################################################
# 1: 生产模式；0: 测试模式
g_product_mode = 0
g_product_mode = 1



def get_cross5_date(_max_date, _days, _db):
    sql = "select distinct pub_date from tbl_day_tech z \
where pub_date < (select max(pub_date) from tbl_day_tech where pub_date<='%s') order by pub_date desc limit %d" % (_max_date, _days)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        df.set_index("pub_date", inplace=True)
        # log_debug("date df: \n%s", df)
        return df


"""
-- 2016/11/27
_trade_date 必须是前一个交易日！
例如今天是2016-11-25，trade_date则是2016-11-24
"""
def get_cross5_list(_trade_date, _db):
    sql = "select a.stock_id stock_id from tbl_day a, tbl_day_tech b \
where a.stock_id=b.stock_id \
and a.pub_date=b.pub_date \
and a.pub_date='%s' \
and a.close_price > a.open_price \
and b.ma5   >= a.open_price \
and b.ma10  >= a.open_price \
and b.ma20  >= a.open_price \
and b.ma30  >= a.open_price \
and b.ma60  >= a.open_price \
and b.ma5   <= a.close_price \
and b.ma10  <= a.close_price \
and b.ma20  <= a.close_price \
and b.ma30  <= a.close_price \
and b.ma60  <= a.close_price \
and b.macd >= -0.01 \
and b.diff >= -0.04 \
and b.dea  >= -0.04 order by 1" % (_trade_date)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        df.set_index("stock_id", inplace=True)
        df["1"] = "1"
        # log_debug("df: \n%s", df)
        return df


def get_cross5_detail(_trade_date, _db):
    sql = "select a.stock_id, a.pub_date, a.open_price, a.close_price, a.high_price, a.low_price, \
a.last_close_price last, a.deal_total_count total, \
b.ma5, b.ma10, b.ma20, b.ma30, b.ma60, b.ma150, \
macd, diff, dea \
from tbl_day a, tbl_day_tech b \
where a.stock_id=b.stock_id \
and a.pub_date=b.pub_date \
and a.pub_date in (select * from (select distinct pub_date from tbl_day_tech x \
where pub_date <= (select distinct pub_date from tbl_day_tech z where pub_date > '%s' order by pub_date limit 1) \
order by pub_date desc limit 5) y) \
and a.stock_id in (select * from ( select a.stock_id from tbl_day a, tbl_day_tech b \
where a.stock_id=b.stock_id \
and a.pub_date=b.pub_date \
and a.pub_date='%s' \
and a.close_price > a.open_price \
and b.ma5   >= a.open_price \
and b.ma10  >= a.open_price \
and b.ma20  >= a.open_price \
and b.ma30  >= a.open_price \
and b.ma60  >= a.open_price \
and b.ma5   <= a.close_price \
and b.ma10  <= a.close_price \
and b.ma20  <= a.close_price \
and b.ma30  <= a.close_price \
and b.ma60  <= a.close_price \
and b.macd >= -0.01 \
and b.diff >= -0.04 \
and b.dea  >= -0.04) c) \
order by 1, 2 desc" % (_trade_date, _trade_date)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        # log_debug("df: \n%s", df)
        return df


def work_one(_trade_date, _db):

    # step2: list
    stock_list = get_cross5_list(_trade_date, _db)
    if stock_list is None:
        log_error("error: get_cross5_list(%s) is None", _trade_date)
        return -1

    # step3: detail
    stock_detail = get_cross5_detail(_trade_date, _db)
    if stock_detail is None:
        log_error("error: get_cross5_detail(%s) is None", _trade_date)
        return -1

    # step4
    rv = ref_init2(stock_list, stock_detail)
    if rv < 0:
        log_error("error: ref_init2")
        return -1


    # step5
    content = ""
    for row_index, row in stock_list.iterrows():
        stock_id = row_index
        rv = ref_set(stock_id)
        if rv < 0:
            log_error("error: ref_set %s", stock_id)
            return -1
        elif rv < 3:
            log_error("warn: small %s", stock_id)
            continue

        log_debug("------------%s-------------", stock_id)
        amount_rate = ref_amount(1) / ref_amount(2)
        ##### 2016-11
        # 1. 穿越当日，成交量翻倍
        # 2. 次日，成交量增加
        # 3. 次日，高开
        # 4. 次日，收阳线
        ##### 2016-12-3 减弱条件
        # 1. 穿越当日，成交量放大
        # 2. 次日，比前天成交量增加
        # 3. 次日，高开 -0.01
        # 4. 次日，收阳线
        # if amount_rate>=2 and ref_amount(0)>ref_amount(1) and ref_open(0)>=ref_close(1) and ref_close(0)>=ref_open(0):
        if amount_rate>=2 and ref_amount(0)>ref_amount(2) and ref_open(0)>=ref_close(1)*0.99 and ref_close(0)>=ref_open(0):
            log_debug("rate: %.2f", amount_rate)
            log_debug("amount1  < amout2    -- %.2f <  %.2f", ref_amount(2), ref_amount(1))
            log_debug("amount2  < amout3    -- %.2f <  %.2f", ref_amount(1), ref_amount(0))
            log_debug("open(0)  > close(1)  -- %.2f >  %.2f", ref_open(0),   ref_close(1))
            log_debug("close(0) >= open(0)  -- %.2f >= %.2f", ref_close(0),  ref_open(0))
            log_debug("nice: cross5 buy %s", stock_id)
            info = get_basic_info(stock_id)
            xsg  = get_xsg_info(stock_id, _db)
            one = "%s [%s] [%s]\n%s%s\n" % (stock_id, _trade_date, get_name(stock_id), info, xsg)
            content += one
        else:
            log_debug("sorry, not match")

    if len(content) > 0:
        subject = "cross5 %s" % _trade_date
        log_debug("head: %s", subject)
        log_debug("mail: \n%s", content)

        if g_product_mode == 1:
            saimail(subject, content)
    else:
        log_debug("%s not match", _trade_date)

    return 0


def work():
    db = db_init()

    # trade_date = "2016-11-14"
    basic = get_stock_list_df_tu()
    if basic is None:
        log_debug("error: get_stock_list_df_tu failure")
        return -1

    if g_product_mode == 1:
        max_date = get_date_by(0)
        days     = 2
        days     = 1
    else:
        max_date = "2016-12-03"
        days     = 3

    # 获得前一个交易日期
    date_df = get_cross5_date(max_date, days, db)
    if date_df is None:
        log_error("erorr: get_cross5_date")
        return -1

    for row_index, row in date_df.iterrows():
        trade_date = row_index
        log_debug("trade_date: %s", trade_date)

        rv = work_one(trade_date, db)
        if rv != 0:
            log_error("error: work_one %s failure", trade_date)

    db_end(db)


#######################################################################

def main():
    global g_product_mode
    sailog_set("ma_cross5.log")

    log_info("let's begin here!")

    if g_product_mode == 1:
        # check holiday
        if today_is_weekend():
            log_info("today is weekend, exit")
        else:
            log_info("today is workday, come on")
            work()
    else:
        log_info("test mode")
        work()

    log_info("main ends, bye!")
    return

main()
exit()

#######################################################################

# ma_cross5.py
