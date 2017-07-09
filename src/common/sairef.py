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

#######################################################################

g_trade_date    = None

g_ref_tech      = 0    # default without MA, MACD

g_ref_list      = None # series
g_ref_detail    = None # dataframe

g_ref_this      = None # dateframe(stock_id)

g_ref_this_close= None # close price series
g_ref_this_open = None #
g_ref_this_high = None #
g_ref_this_low  = None #

g_ref_this_last = None # 
g_ref_this_total= None #

g_ref_this_ma5  = None #
g_ref_this_ma10 = None #
g_ref_this_ma20 = None #
g_ref_this_ma30 = None #
g_ref_this_ma60 = None #
g_ref_this_ma150= None #

g_ref_this_macd = None #
g_ref_this_diff = None #
g_ref_this_dea  = None #

g_ref_this_vma5 = None #
g_ref_this_vma10= None #


def ref_set(_stock_id):
    global g_ref_list
    global g_ref_detail
    global g_ref_this
    global g_ref_tech

    e = g_ref_list.get(_stock_id)
    if e is None:
        log_error("error: %s not exist!", _stock_id)
        return -1

    g_ref_this = g_ref_detail[g_ref_detail['stock_id'] == _stock_id]
    g_ref_this.set_index("pub_date", inplace=True)
    # log_debug("this: \n%s", g_ref_this)

    global g_ref_this_close
    global g_ref_this_open
    global g_ref_this_high
    global g_ref_this_low
    global g_ref_this_last
    global g_ref_this_total
    global g_ref_this_ma5
    global g_ref_this_ma10
    global g_ref_this_ma20
    global g_ref_this_ma30
    global g_ref_this_ma60
    global g_ref_this_ma150
    global g_ref_this_macd
    global g_ref_this_diff
    global g_ref_this_dea
    global g_ref_this_vma5
    global g_ref_this_vma10

    g_ref_this_close= g_ref_this['close_price']
    g_ref_this_open = g_ref_this['open_price']
    g_ref_this_high = g_ref_this['high_price']
    g_ref_this_low  = g_ref_this['low_price']
    g_ref_this_last = g_ref_this['last']
    g_ref_this_total= g_ref_this['total']

    if g_ref_tech == 1:
        log_debug("nice: with MA && MACD")
        g_ref_this_ma5  = g_ref_this['ma5']
        g_ref_this_ma10 = g_ref_this['ma10']
        g_ref_this_ma20 = g_ref_this['ma20']
        g_ref_this_ma30 = g_ref_this['ma30']
        g_ref_this_ma60 = g_ref_this['ma60']
        g_ref_this_ma150= g_ref_this['ma150']
        g_ref_this_macd = g_ref_this['macd']
        g_ref_this_diff = g_ref_this['diff']
        g_ref_this_dea  = g_ref_this['dea']
        g_ref_this_vma5 = g_ref_this['vma5']
        g_ref_this_vma10= g_ref_this['vma10']

    return len(g_ref_this)

def ref_len():
    global g_ref_list
    return len(g_ref_this)

def ref_close(_offset):
    global g_ref_this_close
    return float(g_ref_this_close[_offset])

def ref_open(_offset):
    global g_ref_this_open
    return float(g_ref_this_open[_offset])

def ref_high(_offset):
    global g_ref_this_high
    return float(g_ref_this_high[_offset])

def ref_low(_offset):
    global g_ref_this_low
    return float(g_ref_this_low[_offset])

def ref_pre_close(_offset):
    global g_ref_this_last
    return float(g_ref_this_last[_offset])

def ref_amount(_offset):
    global g_ref_this_total
    return float(g_ref_this_total[_offset])

def ref_vol(_offset):
    global g_ref_this_total
    return float(g_ref_this_total[_offset])

def ref_ma5(_offset):
    global g_ref_this_ma5
    return float(g_ref_this_ma5[_offset])

def ref_ma10(_offset):
    global g_ref_this_ma10
    return float(g_ref_this_ma10[_offset])

def ref_ma20(_offset):
    global g_ref_this_ma20
    return float(g_ref_this_ma20[_offset])

def ref_ma30(_offset):
    global g_ref_this_ma30
    return float(g_ref_this_ma30[_offset])

def ref_ma60(_offset):
    global g_ref_this_ma60
    return float(g_ref_this_ma60[_offset])

def ref_ma150(_offset):
    global g_ref_this_ma150
    return float(g_ref_this_ma150[_offset])

def ref_macd(_offset):
    global g_ref_this_macd
    return float(g_ref_this_macd[_offset])

def ref_diff(_offset):
    global g_ref_this_diff
    return float(g_ref_this_diff[_offset])

def ref_dea(_offset):
    global g_ref_this_dea
    return float(g_ref_this_dea[_offset])

def ref_vma5(_offset):
    global g_ref_this_vma5
    return float(g_ref_this_vma5[_offset])

def ref_vma10(_offset):
    global g_ref_this_vma10
    return float(g_ref_this_vma10[_offset])


"""
-- 2016/11/20
"""
def get_recent_detail_all_1(_db):
    global g_trade_date
    sql = "select a.stock_id stock_id, a.pub_date pub_date, \
a.open_price open_price, a.close_price close_price,  \
a.high_price high_price, a.low_price   low_price,  \
a.last_close_price last, a.deal_total_count total, \
b.ma5 ma5, b.ma10 ma10, b.ma20 ma20, b.ma30 ma30, \
b.ma60 ma60, b.ma150 ma150, macd, diff, dea \
from tbl_day a, tbl_day_tech b \
where a.pub_date in (select * from (select distinct pub_date from tbl_day_tech x where pub_date <='%s' order by pub_date desc limit 10) y) \
and a.stock_id=b.stock_id \
and a.pub_date=b.pub_date \
order by 1, 2 desc" % (g_trade_date)
    log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("no data in db")
        return None
    else:
        log_debug("df: \n%s", df)
        return df



def get_recent_list_1(_db):
    global g_trade_date
    sql = "select distinct a.stock_id stock_id \
from tbl_day a, tbl_day_tech b \
where a.pub_date in (select * from (select distinct pub_date from tbl_day_tech x where pub_date <='%s' order by pub_date desc limit 10) y) \
and a.stock_id=b.stock_id \
and a.pub_date=b.pub_date \
order by 1" % (g_trade_date)

    # log_debug("%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("no data in db: %s", sql)
        return None
    else:
        df.set_index("stock_id", inplace=True)
        df["1"] = "1"
        return df


"""
-- 2016/11/26
-- 无技术指标，如macd等
"""
def get_recent_detail_all(_db):
    global g_trade_date
    sql = "select a.stock_id stock_id, a.pub_date pub_date, \
a.open_price open_price, a.close_price close_price,  \
a.high_price high_price, a.low_price   low_price, \
a.last_close_price last, a.deal_total_count total \
from tbl_day a \
where a.pub_date in (select * from (select distinct pub_date from tbl_day x where pub_date <='%s' order by pub_date desc limit 100) y) \
order by 1, 2 desc" % (g_trade_date)

    log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("no data in db")
        return None
    else:
        # log_debug("df: \n%s", df)
        return df



def get_recent_list(_db):
    global g_trade_date
    sql = "select distinct a.stock_id stock_id \
from tbl_day a \
where a.pub_date in (select * from (select distinct pub_date from tbl_day x where pub_date <='%s' order by pub_date desc limit 30) y) \
order by 1" % (g_trade_date)

    log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("no data in db: %s", sql)
        return None
    else:
        df.set_index("stock_id", inplace=True)
        df["1"] = "1"
        return df

def ref_set_date(_date):
    global g_trade_date
    g_trade_date = _date

def ref_get_list():
    global g_ref_list
    return g_ref_list


def ref_init(_db):
    global g_ref_list
    global g_ref_detail
    global g_trade_date

    if g_trade_date is None:
        g_trade_date = get_date_by(0)
    log_info("date: %s", g_trade_date)

    df = get_recent_list(_db)
    if df is None:
        log_error("error: get_recent_list not found")
        return -1
    else:
        g_ref_list = df['1']
        # log_debug("list:\n%s", g_ref_list)

    g_ref_detail = get_recent_detail_all(_db)
    if g_ref_detail is None:
        log_error("get_recent_detail_all: not found")
        return -1
    else:
        log_debug("detail:\n%d", len(g_ref_detail))

    return 0


# configurable. 2016-11-27
def ref_init2(_list_df, _detail_df):
    global g_ref_list
    global g_ref_detail

    df = _list_df
    if df is None:
        log_error("error:list_df not found")
        return -1
    else:
        g_ref_list = df['1']
        # log_debug("list:\n%s", g_ref_list)

    g_ref_detail = _detail_df
    if g_ref_detail is None:
        log_error("error: _detail_df not found")
        return -1
    else:
        log_debug("detail: %d", len(g_ref_detail))

    return 0


# 30min
def ref_set3(_stock_id):
    global g_ref_list
    global g_ref_detail
    global g_ref_this
    global g_ref_tech

    e = g_ref_list.get(_stock_id)
    if e is None:
        log_error("error: %s not exist!", _stock_id)
        return -1

    g_ref_this = g_ref_detail[g_ref_detail['stock_id'] == _stock_id]
    g_ref_this.set_index("pub_date_time", inplace=True)
    # log_debug("this: \n%s", g_ref_this)

    global g_ref_this_close
    global g_ref_this_open
    global g_ref_this_high
    global g_ref_this_low
    global g_ref_this_last
    global g_ref_this_total

    g_ref_this_close= g_ref_this['close_price']
    g_ref_this_open = g_ref_this['open_price']
    g_ref_this_high = g_ref_this['high_price']
    g_ref_this_low  = g_ref_this['low_price']
    g_ref_this_last = g_ref_this['last']
    g_ref_this_total= g_ref_this['total']


    return len(g_ref_this)


# 30min
def ref_set_tech3(_stock_id):
    global g_ref_list
    global g_ref_detail
    global g_ref_this
    global g_ref_tech

    e = g_ref_list.get(_stock_id)
    if e is None:
        log_error("error: %s not exist!", _stock_id)
        return -1

    g_ref_this = g_ref_detail[g_ref_detail['stock_id'] == _stock_id]
    g_ref_this.set_index("pub_date_time", inplace=True)
    # log_debug("this: \n%s", g_ref_this)

    global g_ref_this_ma5
    global g_ref_this_ma10
    global g_ref_this_ma20
    global g_ref_this_ma30
    global g_ref_this_ma60
    global g_ref_this_ma150
    global g_ref_this_macd
    global g_ref_this_diff
    global g_ref_this_dea
    global g_ref_this_vma5
    global g_ref_this_vma10

    g_ref_this_ma5  = g_ref_this['ma5']
    g_ref_this_ma10 = g_ref_this['ma10']
    g_ref_this_ma20 = g_ref_this['ma20']
    g_ref_this_ma30 = g_ref_this['ma30']
    g_ref_this_ma60 = g_ref_this['ma60']
    g_ref_this_ma150= g_ref_this['ma150']
    g_ref_this_macd = g_ref_this['macd']
    g_ref_this_diff = g_ref_this['diff']
    g_ref_this_dea  = g_ref_this['dea']
    g_ref_this_vma5  = g_ref_this['vma5']
    g_ref_this_vma10 = g_ref_this['vma10']

    return len(g_ref_this)


# day: outer calculate
def ref_set_tech(_stock_id):
    global g_ref_list
    global g_ref_detail
    global g_ref_this
    global g_ref_tech

    e = g_ref_list.get(_stock_id)
    if e is None:
        log_error("error: %s not exist!", _stock_id)
        return -1

    g_ref_this = g_ref_detail[g_ref_detail['stock_id'] == _stock_id]
    g_ref_this.set_index("pub_date", inplace=True)
    # log_debug("this: \n%s", g_ref_this)

    global g_ref_this_ma5
    global g_ref_this_ma10
    global g_ref_this_ma20
    global g_ref_this_ma30
    global g_ref_this_ma60
    global g_ref_this_ma150
    global g_ref_this_macd
    global g_ref_this_diff
    global g_ref_this_dea
    global g_ref_this_vma5
    global g_ref_this_vma10

    g_ref_this_ma5  = g_ref_this['ma5']
    g_ref_this_ma10 = g_ref_this['ma10']
    g_ref_this_ma20 = g_ref_this['ma20']
    g_ref_this_ma30 = g_ref_this['ma30']
    g_ref_this_ma60 = g_ref_this['ma60']
    g_ref_this_ma150= g_ref_this['ma150']
    g_ref_this_macd = g_ref_this['macd']
    g_ref_this_diff = g_ref_this['diff']
    g_ref_this_dea  = g_ref_this['dea']
    g_ref_this_vma5  = g_ref_this['vma5']
    g_ref_this_vma10 = g_ref_this['vma10']

    return len(g_ref_this)

# day: self calculate
def ref_set_with_tech(_stock_id):
    global g_ref_list
    global g_ref_detail
    global g_ref_this
    global g_ref_tech

    e = g_ref_list.get(_stock_id)
    if e is None:
        log_error("error: %s not exist!", _stock_id)
        return -1

    g_ref_this = g_ref_detail[g_ref_detail['stock_id'] == _stock_id]
    g_ref_this.set_index("pub_date", inplace=True)

    global g_ref_this_close
    global g_ref_this_open
    global g_ref_this_high
    global g_ref_this_low
    global g_ref_this_last
    global g_ref_this_total
    global g_ref_this_ma5
    global g_ref_this_ma10
    global g_ref_this_ma20
    global g_ref_this_ma30
    global g_ref_this_ma60
    global g_ref_this_ma150
    global g_ref_this_macd
    global g_ref_this_diff
    global g_ref_this_dea
    global g_ref_this_vma5
    global g_ref_this_vma10

    g_ref_this_close= g_ref_this['close_price']
    g_ref_this_open = g_ref_this['open_price']
    g_ref_this_high = g_ref_this['high_price']
    g_ref_this_low  = g_ref_this['low_price']
    g_ref_this_last = g_ref_this['last']
    g_ref_this_total= g_ref_this['total']

    # _detail_df.sort_index(ascending=False, inplace=True)

    sc = g_ref_this_close.sort_index(ascending=True)

    # sma5
    g_ref_this_ma5 = calc_sma(sc, 5).sort_index(ascending=False)

    # sma10
    g_ref_this_ma10 = calc_sma(sc, 10).sort_index(ascending=False)

    # sma20
    g_ref_this_ma20 = calc_sma(sc, 20).sort_index(ascending=False)

    # sma30
    g_ref_this_ma30 = calc_sma(sc, 30).sort_index(ascending=False)

    # sma60
    g_ref_this_ma60 = calc_sma(sc, 60).sort_index(ascending=False)

    # sma120
    g_ref_this_ma120 = calc_sma(sc, 120).sort_index(ascending=False)

    # sma150
    g_ref_this_ma150 = calc_sma(sc, 150).sort_index(ascending=False)

    # macd: ema(12), ema(26), diff, dea(9), macd
    sm, sn, g_ref_this_diff, g_ref_this_dea, g_ref_this_macd = calc_macd_list0(sc, 12, 26, 9)
    g_ref_this_diff.sort_index(ascending=False, inplace=True)
    g_ref_this_dea.sort_index(ascending=False, inplace=True)
    g_ref_this_macd.sort_index(ascending=False, inplace=True)


    # volume - sma5
    sv = g_ref_this_total.sort_index(ascending=True)
    g_ref_this_vma5 = calc_sma(sv, 5).sort_index(ascending=False)

    g_ref_this_vma10 = calc_sma(sv, 10).sort_index(ascending=False)

    return len(g_ref_this)



# 2017-7-9
def ref_init4(_detail_df):
    global g_ref_detail

    g_ref_detail = _detail_df
    if g_ref_detail is None:
        log_error("error: _detail_df not found")
        return -1
    else:
        # log_debug("detail: %d", len(g_ref_detail))
        pass

    global g_ref_this_close
    global g_ref_this_open
    global g_ref_this_high
    global g_ref_this_low
    global g_ref_this_last
    global g_ref_this_total

    g_ref_this_close= g_ref_detail['close_price']
    g_ref_this_open = g_ref_detail['open_price']
    g_ref_this_high = g_ref_detail['high_price']
    g_ref_this_low  = g_ref_detail['low_price']
    g_ref_this_last = g_ref_detail['last']
    g_ref_this_total= g_ref_detail['total']

    return len(g_ref_detail)


# 2017-7-9
def ref_set_tech4():
    global g_ref_detail

    global g_ref_this_ma5
    global g_ref_this_ma10
    global g_ref_this_ma20
    global g_ref_this_ma30
    global g_ref_this_ma60
    global g_ref_this_ma150
    global g_ref_this_macd
    global g_ref_this_diff
    global g_ref_this_dea
    global g_ref_this_vma5
    global g_ref_this_vma10

    g_ref_this_ma5   = g_ref_detail['ma5']
    g_ref_this_ma10  = g_ref_detail['ma10']
    g_ref_this_ma20  = g_ref_detail['ma20']
    g_ref_this_ma30  = g_ref_detail['ma30']
    g_ref_this_ma60  = g_ref_detail['ma60']
    g_ref_this_ma150 = g_ref_detail['ma150']
    g_ref_this_macd  = g_ref_detail['macd']
    g_ref_this_diff  = g_ref_detail['diff']
    g_ref_this_dea   = g_ref_detail['dea']
    g_ref_this_vma5  = g_ref_detail['vma5']
    g_ref_this_vma10 = g_ref_detail['vma10']

    return len(g_ref_detail)


#######################################################################
if __name__=="__main__":
    sailog_set("sairef.log")

    log_info("main begin here!")

    log_info("main ends  bye!")

#######################################################################

# sairef.py
