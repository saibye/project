#!/usr/bin/env python
# -*- encoding: utf8 -*-

import tushare as ts
import time
import pandas as pd
import numpy as np

from saiutil import *
from sailog  import *


g_stock_basic     = None
g_stock_quotation = None

# 名称、流通、PE等
def get_stock_list_df_tu():
    global g_stock_basic

    count = 0
    while count < 20:
        count = count + 1
        try:
            g_stock_basic = ts.get_stock_basics()
            break
        except Exception:
            log_error("warn: get_stock_basics exception: %d!", count)
            time.sleep(5)

    if g_stock_basic is not None:
        g_stock_basic.sort_index(inplace=True)

    return g_stock_basic


# 当日行情：涨幅、收盘等
def get_stock_quotation():
    global g_stock_quotation

    #  today all 
    count = 0
    while count < 5:
        count = count + 1
        try :
            g_stock_quotation = ts.get_today_all()
            break
        except Exception:
            log_error("error: get_today_all")

    if g_stock_quotation is not None:
        g_stock_quotation.set_index('code', inplace=True)

    return g_stock_quotation


# 当前价，大多是收盘价
# 只能是最新一个交易日
def get_curr_price(_stock_id):
    df = None
    try :
        df = ts.get_realtime_quotes(_stock_id)
    except Exception:
        log_error("error: get_realtime_quotes")
        return None

    if df is not None:
        c = float(df['price'][0])
    else:
        c = None

    return c

# 开盘价
# 只能是最新一个交易日
def get_open_price(_stock_id):
    df = None
    try :
        df = ts.get_realtime_quotes(_stock_id)
    except Exception:
        log_error("error: get_realtime_quotes")
        return None

    if df is not None:
        o = float(df['open'][0])
    else:
        o = None

    return o


# 涨幅
# 只能是最新一个交易日
def get_chg_rate(_stock_id):
    df = None

    try :
        df = ts.get_realtime_quotes(_stock_id)
    except Exception:
        log_error("error: get_realtime_quotes")
        return None

    if df is not None:
        close = float(df['price'][0])
        pre   = float(df['pre_close'][0])
        chg   = 0.0
        if pre > 0:
            chg   = (close / pre - 1) * 100
    else:
        chg   = None

    return chg


# 柱体
# 只能是最新一个交易日
def get_cyl_rate(_stock_id):
    df = None

    try :
        df = ts.get_realtime_quotes(_stock_id)
    except Exception:
        log_error("error: get_realtime_quotes")
        return None

    if df is not None:
        o   = float(df['open'][0])
        c   = float(df['price'][0])
        pre = float(df['pre_close'][0])
        cyl = ((c-o) / pre) * 100
    else:
        cyl = None

    return cyl


# name
def get_name(_stock_id):
    df = None
    try :
        df = ts.get_realtime_quotes(_stock_id)
    except Exception:
        log_error("error: get_realtime_quotes")
        return None

    if df is not None:
        n = df['name'][0]
    else:
        n = None

    return n


# 振幅
# 只能是最新一个交易日
def get_amp_rate(_stock_id):
    df = None

    try :
        df = ts.get_realtime_quotes(_stock_id)
    except Exception:
        log_error("error: get_realtime_quotes")
        return None

    if df is not None:
        h   = float(df['high'][0])
        l   = float(df['low'][0])
        pre = float(df['pre_close'][0])
        amp = ((h-l) / pre) * 100
    else:
        amp = None

    return amp


def get_basic_info(_stock_id):
    global g_stock_basic

    info = ""

    if g_stock_basic is None:
        return info

    # TODO: check whether frame contains this stock
    row = g_stock_basic.loc[_stock_id, :]

    # 名称, 行业, 地区
    # 市盈率, 流通股本, 总股本, 上市日期
    info  = "%s-%s-%s\n" % (row['name'], row['industry'], row['area'])
    info += "市盈率 : %s\n" % row['pe']

    v1 = float(row['outstanding']) # / 10000.00
    info += "流通股 : %.2f亿股\n" % v1

    v2 = float(row['totals']) # / 10000.00
    info += "总股本 : %.2f亿股\n" % v2
    info += "上市   : %s\n" % row['timeToMarket']

    # 当前价
    c = get_curr_price(_stock_id)
    if c is not None:
        v3 = c * v1
        info += "流通市 : %.2f亿\n" % v3

    log_debug("info:\n%s", info)

    # return info
    return info

# 2017-2-25 龙虎榜
def get_top_list_tu(_trade_date):
    stock_list = None

    count = 0
    while count < 2:
        count = count + 1
        try:
            stock_list = ts.top_list(_trade_date)
            break
        except Exception:
            log_error("warn: ts.top_list exception: %d!", count)
            time.sleep(5)

    return stock_list



# 2018-7-29
def get_last_workday():

    df = ts.get_realtime_quotes('000001')

    # log_debug(df)

    pub_date = None

    for row_index, row in df.iterrows():
        # log_debug(row_index)
        this_date = str(row['date'])

        if pub_date is None or this_date > pub_date:
            pub_date = this_date

        # log_debug("date -- %s -- %s", pub_date, type(pub_date))

    return pub_date


if __name__=="__main__":
    sailog_set("saitu.log")
    subject   = u"goodbye subject"
    body      = u"hello world, buy buy buy"
    stock_id = "000002"
    stock_id = "000712"
    rate  = get_chg_rate(stock_id)
    log_debug("-- %s --", stock_id)
    log_debug("name -- %s",   get_name(stock_id))
    log_debug("curr -- %.2f", get_curr_price(stock_id))
    log_debug("rate -- %.2f", get_chg_rate(stock_id))
    log_debug("cyln -- %.2f", get_cyl_rate(stock_id))
    log_debug("ampl -- %.2f", get_amp_rate(stock_id))

    work_date = get_last_workday()
    log_debug("work-date -- %s -- %s", work_date, type(work_date))

# saitu.py
