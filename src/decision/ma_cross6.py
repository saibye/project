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
from saitech import *

#######################################################################

"""
一阳六线5,10,20,30,60,150
配合macd合理区间
2016-12-11：新增成交量、高位徘徊
"""


def check_cross6_chance_one(_stock_id, _cross_date, _open_price, _close_price, _this_date, _db):
    result = False

    ztmd = (_open_price + _close_price) / 2
    """
    log_debug("ztmd  (%s, %s) => %.2f",  _stock_id, _cross_date, ztmd)
    log_debug("close (%s, %s) => %.2f",  _stock_id, _cross_date, _close_price)
    """

    vol_rate = tech_get_vol_rate(_stock_id, _cross_date, _db)
    log_info("volrt (%s, %s) => %.2f",  _stock_id, _cross_date, vol_rate)


    # 最近9(m1)天的收盘价，高于穿越日收盘价的天数为n1
    m1 = 9
    n1 = tech_get_exist_days(_stock_id, _cross_date, _close_price, m1, _db)
    log_info("exist1(%s, %s) => %d",  _stock_id, _cross_date, n1)

    # 最近8(m2)天的收盘价，高于穿越日中线价的天数为n2
    m2 = 8
    n2 = tech_get_exist_n2(_stock_id, _cross_date, ztmd, m2, _db)
    log_info("exist2(%s, %s) => %d",  _stock_id, _cross_date, n2)

    # 今天碰到ma10
    touch_ma10 = tech_check_touch_ma10(_stock_id, _this_date, _db)
    log_debug("ma10  (%s, %s) => %s",  _stock_id, _this_date, touch_ma10)

    """
    1. 量比8倍时， n1 >= 6, n2 >= 8
    2. 量比2倍时， n1 >= 9, n2 >= 8 # disabled
    """

    if vol_rate >= 8:
        log_info("good3: %.2f", vol_rate)
        # if n1 >= 6 and n2 >= m2 and touch_ma10:
        if n1 >= 6 and n2 >= m2:
            result = True
            log_info("nice3: %s: exist(close): %d, exist(low): %d", _stock_id, n1, n2)
    elif vol_rate >= 2:
        log_info("good2: %.2f", vol_rate)
        if n1 >= m1 and n2 >= m2 and touch_ma10:
            # 暂不启用 2016-12-11
            # result = True
            log_info("nice2: %s: exist(close): %d, exist(low): %d", _stock_id, n1, n2)
    else:
        log_info("small_rate: %.2f", vol_rate)

    return result , vol_rate, n1, n2




def check_chance(_stocks, _db):

    """
    basic_info = ts.get_stock_basics()
    if basic_info is None:
        log_error("error: ts.get_stock_basics")
        return 
    """

    #
    trade_date = get_date_by(0)
    log_debug("trade_date: %s", trade_date)

    content = ""
    for row_index, row in _stocks.iterrows():
        if sai_is_product_mode():
            stock_id    = row_index
            cross_date  = row['pub_date']
            close_price = row['close_price']
            open_price  = row['open_price']
            trade_date = get_last_trade_date(stock_id, _db)
        else:
            stock_id    = row_index
            cross_date  = row['pub_date']
            close_price = row['close_price']
            open_price  = row['open_price']
            trade_date = get_last_trade_date(stock_id, _db)
            """
            stock_id    = "600868"
            cross_date  = "2016-09-28"
            close_price = 5.31
            open_price  = 4.89
            trade_date  = "2016-10-18"
            trade_date  = "2016-10-17"
            trade_date  = "2016-10-21"

            stock_id    = "600857"
            cross_date  = "2016-09-29"
            close_price = 14.57
            open_price  = 14.11
            trade_date  = "2016-10-18"
            """
        log_debug("-------------[%s, %s]-------------", stock_id, cross_date)
        """
        info_row = basic_info.loc[stock_id, :]
        one = "%s [%s] [%s]\n" % (stock_id, row['pub_date'], info_row['name'])
        """
        good, vol_rate, n1, n2 = check_cross6_chance_one(stock_id, cross_date, open_price, close_price, trade_date, _db)
        if good:
            one = "%s cross[%s], chance[%s]\n" % (stock_id, cross_date, trade_date)
            one += "--vol_rate: %.2f, days1(%d), days2(%d)\n" % (vol_rate, n1, n2)
            one += "------------------------------------------------------\n"
            log_debug("nice: %s has chance at[%s]\n", stock_id, trade_date)
            content += one
        else:
            log_debug("sorry: %s no chance at[%s]\n", stock_id, trade_date)


    subject = "cross6 %s" % (trade_date)
    log_debug("%s", subject)
    log_debug("\n%s", content)
    if len(content):
        content = "no chance for cross6"

    if sai_is_product_mode():
        saimail(subject, content)
    else:
        log_info("mail: \n%s", content)

    return


"""
-- 2016/11/15
and b.macd > 0 \
and b.diff > 0 \
and b.dea  >= 0 \
"""
def get_cross6(_n, _db):
    sql = "select a.stock_id, a.pub_date, a.open_price, a.close_price,  \
b.ma5, b.ma10, b.ma20, b.ma30, b.ma60, b.ma150, macd, diff, dea \
from tbl_day a, tbl_day_tech b \
where a.pub_date in (select * from (select distinct pub_date from tbl_day_tech x order by pub_date desc limit %d) y) \
and a.stock_id=b.stock_id \
and a.pub_date=b.pub_date \
and a.open_price < a.close_price \
and b.ma5   >= a.open_price \
and b.ma10  >= a.open_price \
and b.ma20  >= a.open_price \
and b.ma30  >= a.open_price \
and b.ma60  >= a.open_price \
and b.ma150 >= a.open_price \
and b.ma5   <= a.close_price \
and b.ma10  <= a.close_price \
and b.ma20  <= a.close_price \
and b.ma30  <= a.close_price \
and b.ma60  <= a.close_price \
and b.ma150 <= a.close_price \
and b.macd >= -0.05 \
and b.diff >= -0.02 \
and b.dea  >= -0.02 \
order by 2 desc,1" % (_n)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        log_debug("df: \n%s", df)
        return df


def work():
    db = db_init()

    # 最近n天
    n  = 14

    # step1: get from web
    stocks = get_cross6(n, db)

    log_debug("df:\n%s", stocks)

    if stocks is None:
        log_info("not found!")
    else:
        stocks.set_index('stock_id', inplace=True)
        check_chance(stocks, db)


    db_end(db)


#######################################################################

def main():
    sailog_set("ma_cross6.log")

    log_info("let's begin here!")

    # check holiday
    if sai_is_product_mode():
        if today_is_weekend():
            log_info("today is weekend, exit")
            work()
        else:
            log_info("today is workday, come on")
            work()
    else:
        log_info("test mode, come on")
        work()

    log_info("main ends, bye!")
    return

main()
exit()

#######################################################################


# ma_corss6.py
