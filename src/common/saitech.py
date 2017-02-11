#!/usr/bin/env python
# -*- encoding: utf8 -*-

import tushare as ts
import time
import pandas as pd
import numpy as np

from saiutil import *
from sailog  import *
from saitu   import *
from saidb   import *





"""
2016/12/10
与昨日量比
"""
def tech_get_vol_rate(_stock_id, _trade_date, _db):
    trade_date = str(_trade_date)
    sql = "select pub_date, close_price, open_price, low_price, high_price, last_close_price, deal_total_count \
from tbl_day \
where stock_id='%s' \
and pub_date <= '%s' \
order by pub_date desc \
limit 2" % (_stock_id, trade_date)

    # log_debug("sql: [%s]", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_error("'%s' not found1", _stock_id)
        return -1 
    elif df.empty:
        log_error("'%s' not found2", _stock_id)
        return -1 
    else:
        pass

    if len(df) != 2:
        log_error("'%s' is too short", _stock_id)
        log_error("df: \n%s", df)
        return -1 

    vol_this = df['deal_total_count'][0]
    vol_last = df['deal_total_count'][1]

    date_this = str(df['pub_date'][0])
    date_last = str(df['pub_date'][1])

    if date_this != trade_date:
        log_error("'%s' has no data at '%s'", _stock_id, trade_date)
        log_error("df: \n%s", df)
        return -1

    rate = vol_this / vol_last
    # log_info("%s: vol(%s)/vol(%s) = %.2f", _stock_id, date_this, date_last, rate)

    return rate


"""
2016/12/10
check(low <= ma10 <= high)
"""
def tech_check_touch_ma10(_stock_id, _trade_date, _db):
    sql = "select a.close_price, a.open_price, a.low_price, a.high_price, a.last_close_price, b.ma5, b.ma10 \
from tbl_day a, tbl_day_tech b \
where a.stock_id='%s' \
and a.pub_date  = '%s' \
and a.stock_id  = b.stock_id \
and a.pub_date  = b.pub_date" % (_stock_id, _trade_date)

    # log_debug("check touch-ma10-sql: [%s]", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_error("%s not found1", _stock_id)
        return False
    elif df.empty:
        log_error("%s not found2", _stock_id)
        return False
    else:
        pass

    ma5         = df['ma5'][0]
    ma10        = df['ma10'][0]
    close_price = df['close_price'][0]
    open_price  = df['open_price'][0]
    high_price  = df['high_price'][0]
    low_price   = df['low_price'][0]

    """
    log_info("ma5(%s),   ma10(%s)", ma5, ma10)
    log_info("close(%s), open(%s)", close_price, open_price)
    log_info("low(%s),   high(%s)", low_price,   high_price)
    """

    if ma10 <= high_price and ma10 >= low_price:
        return True
    else:
        return False



"""
2016/12/10
check(low <= ma5 <= high)
"""
def tech_check_touch_ma5(_stock_id, _trade_date, _db):
    sql = "select a.close_price, a.open_price, a.low_price, a.high_price, a.last_close_price, b.ma5, b.ma10 \
from tbl_day a, tbl_day_tech b \
where a.stock_id='%s' \
and a.pub_date  = '%s' \
and a.stock_id  = b.stock_id \
and a.pub_date  = b.pub_date" % (_stock_id, _trade_date)

    # log_debug("check touch-ma5-sql: [%s]", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_error("%s not found1", _stock_id)
        return False
    elif df.empty:
        log_error("%s not found2", _stock_id)
        return False
    else:
        pass

    ma5         = df['ma5'][0]
    ma10        = df['ma10'][0]
    close_price = df['close_price'][0]
    open_price  = df['open_price'][0]
    high_price  = df['high_price'][0]
    low_price   = df['low_price'][0]

    """
    log_info("ma5(%s),   ma10(%s)", ma5, ma10)
    log_info("close(%s), open(%s)", close_price, open_price)
    log_info("low(%s),   high(%s)", low_price,   high_price)
    """

    if ma5 <= high_price and ma5 >= low_price:
        return True
    else:
        return False


"""
功能：_trade_date之后_m天的{收盘}价，有x天高于指定值(_price)
场景：一阳N线后，持续x天在高于{收盘}价的地方徘徊
"""
def tech_get_exist_days(_stock_id, _trade_date, _price, _m, _db):
    sql = "select count(1) cnt from \
(select * from tbl_day \
where stock_id = '%s' \
and pub_date > '%s' \
order by pub_date \
limit %d) t1 \
where close_price > %.2f" % (_stock_id, _trade_date, _m, _price)

    # log_debug("check exist n: [%s]", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_error("'%s' not found1", _stock_id)
        return False
    elif df.empty:
        log_error("'%s' not found2", _stock_id)
        return False
    else:
        pass

    cnt     = df['cnt'][0]
    # log_info("cnt: %d, type(%s)", cnt, type(cnt))

    return cnt


"""
功能：_trade_date之后_m天的{最低}价，有x天高于指定值(_price)
场景：一阳N线后，持续x天在高于{中线}价的地方徘徊
"""
def tech_get_exist_n2(_stock_id, _trade_date, _price, _m, _db):
    sql = "select count(1) cnt from \
(select * from tbl_day \
where stock_id = '%s' \
and   pub_date > '%s' \
order by pub_date \
limit %d) t1 \
where low_price > %.2f" % (_stock_id, _trade_date, _m, _price)

    # log_debug("check exist n2: [%s]", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_error("'%s' not found1", _stock_id)
        return False
    elif df.empty:
        log_error("'%s' not found2", _stock_id)
        return False
    else:
        pass

    cnt     = df['cnt'][0]

    # log_info("cnt: %d, type(%s)", cnt, type(cnt))

    return cnt


#######################################################################
if __name__=="__main__":
    sailog_set("saitech.log")
    log_info("main begin here!")

    db = db_init()

    #------------------------------------------------------------------
    stock_id   = "600466"
    trade_date = "2016-10-28"
    rate = tech_get_vol_rate(stock_id, trade_date, db)
    log_debug("rate: [%s][%s] is [%.2f]", stock_id, trade_date, rate)

    #------------------------------------------------------------------
    stock_id   = "600868"
    trade_date = "2016-10-21"
    if tech_check_touch_ma10(stock_id, trade_date, db):
        log_info("%s, %s touch ma10", stock_id, trade_date)
    else:
        log_info("%s, %s not touch ma10", stock_id, trade_date)

    #------------------------------------------------------------------
    stock_id   = "600173"
    trade_date = "2016-12-05"
    trade_date = "2016-12-04"
    if tech_check_touch_ma5(stock_id, trade_date, db):
        log_info("%s, %s touch ma5", stock_id, trade_date)
    else:
        log_info("%s, %s not touch ma5", stock_id, trade_date)

    #------------------------------------------------------------------
    stock_id   = "600868"
    trade_date = "2016-09-28"
    m = 10
    price = 5.31
    n = tech_get_exist_days(stock_id, trade_date, price, m, db)
    log_info("exist1 has: %d day", n)


    #------------------------------------------------------------------
    stock_id   = "600868"
    trade_date = "2016-09-28"
    m = 10
    price = 5.10
    n = tech_get_exist_n2(stock_id, trade_date, price, m, db)
    log_info("exist2 has: %d day", n)

    #------------------------------------------------------------------
    stock_id   = "002346"
    trade_date = "2016-12-23"
    rate = tech_get_vol_rate(stock_id, trade_date, db)
    log_debug("rate: [%s][%s] is [%.2f]", stock_id, trade_date, rate)

    #------------------------------------------------------------------
    stock_id   = "002346"
    trade_date = "2016-12-26"
    rate = tech_get_vol_rate(stock_id, trade_date, db)
    log_debug("rate: [%s][%s] is [%.2f]", stock_id, trade_date, rate)

    #------------------------------------------------------------------
    stock_id   = "601003"
    trade_date = "2016-11-21"
    rate = tech_get_vol_rate(stock_id, trade_date, db)
    log_debug("rate: [%s][%s] is [%.2f]", stock_id, trade_date, rate)

    #------------------------------------------------------------------
    db_end(db)
    log_info("main ends  bye!")

#######################################################################

# saitech.py
