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
from saitech import *

#######################################################################


"""
+++ 601003, 2016-11-21
测试效果非常不理想，故不启用。 2017-2-4
"""


"""
均线压制，ma5-ma60
一阳三线
macd全为正
放量涨停，量比4+
"""
def get_cross3_list(_trade_date, _db):
    sql = "select a.stock_id, a.pub_date, a.open_price, a.close_price, \
a.last_close_price last, a.deal_total_count total, \
b.ma5, b.ma10, b.ma20, b.ma30, b.ma60, b.ma150, \
macd, diff, dea \
from tbl_day a, tbl_day_tech b \
where a.stock_id=b.stock_id \
and a.pub_date=b.pub_date \
and a.close_price > a.open_price \
and (a.close_price - a.last_close_price) / a.last_close_price * 100 > 9.8 \
and b.ma5   >= a.open_price \
and b.ma10  >= a.open_price \
and b.ma20  >= a.open_price \
and b.ma5   <= a.close_price \
and b.ma10  <= a.close_price \
and b.ma20  <= a.close_price \
and b.ma5   >  b.ma10 \
and b.ma10  >  b.ma20 \
and b.ma20  >  b.ma30 \
and b.ma30  >  b.ma60 \
and b.macd >= 0.00 \
and b.diff >= 0.01 \
and b.dea  >= 0.01 \
order by 2, 1"

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


def work():
    db = db_init()

    if sai_is_product_mode():
        trade_date = get_date_by(0)
        days     = 1
    else:
        trade_date = "2016-12-03"
        days     = 3

    subject = "cross3 %s" % trade_date

    # step2: list
    stock_list = get_cross3_list(trade_date, db)
    if stock_list is None:
        log_error("error: get_cross5_list(%s) is None", trade_date)
        return -1

    # step5
    content = ""
    for row_index, row in stock_list.iterrows():
        stock_id   = row_index
        trade_date = row['pub_date']
        log_debug("------------%s, %s-------------", stock_id, trade_date)
        rate = tech_get_vol_rate(stock_id, trade_date, db)
        if rate >= 4:
            log_info( "nice:  %s, %s, vol-rate: %.2f", stock_id, trade_date, rate)
            info = get_basic_info_all(stock_id, db)
            content += info
            content += "---------------------------------\n"
        else:
            log_debug("sorry: %s, %s, vol-rate: %.2f", stock_id, trade_date, rate)


    if len(content) > 0:
        log_debug("head: %s", subject)
        log_debug("mail: \n%s", content)

        if sai_is_product_mode():
            saimail(subject, content)
    else:
        log_debug("%s not match", trade_date)

    db_end(db)

    return 0



#######################################################################

def main():
    sailog_set("ma_cross3.log")

    log_info("let's begin here!")

    if sai_is_product_mode():
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

# ma_cross3.py
