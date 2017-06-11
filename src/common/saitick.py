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


g_sina_mode = 0

def get_tick(_stock_id, _trade_date):
    global g_sina_mode

    if g_sina_mode == 1:
        # log_debug("sina")
        return get_tick_sina(_stock_id, _trade_date)
    else:
        # log_debug("feng")
        return get_tick_feng(_stock_id, _trade_date)

def tick_set_sina_mode():
    global g_sina_mode
    g_sina_mode = 1

def tick_set_feng_mode():
    global g_sina_mode
    g_sina_mode = 0


def get_tick_sina(_stock_id, _trade_date):

    # sina base
    base_vol = 200 # should >= 400

    df = None

    try:
        df = ts.get_sina_dd(_stock_id, date=_trade_date, vol=base_vol)
    except Exception:
        log_error("warn: %s get sina exception!", _stock_id)
        time.sleep(5)
        return None

    if df is None :
        log_error("warn: stock %s, %s is None, next", _stock_id, _trade_date)
        return None

    if df.empty:
        log_error("warn: stock %s, %s is empty, next", _stock_id, _trade_date)
        return None

    if len(df) <= 5:
        log_error("warn: stock %s, %s is short %d, next", _stock_id, _trade_date, len(df))
        return None

    #  sina data: convert to 手
    df['volume'] = df['volume'] / 100

    df = df.set_index('time').sort_index()

    return df


def get_tick_feng(_stock_id, _trade_date):

    df = None

    try:
        df = ts.get_tick_data(_stock_id, date=_trade_date, retry_count=5, pause=1)
    except Exception:
        log_error("warn: %s get ticks exception!", _stock_id)
        time.sleep(5)
        return None

    if df is None :
        log_error("warn: stock %s, %s is None, next", _stock_id, _trade_date)
        return None

    if df.empty:
        log_error("warn: stock %s, %s is empty, next", _stock_id, _trade_date)
        return None

    if len(df) <= 5:
        log_error("warn: stock %s, %s is short %d, next", _stock_id, _trade_date, len(df))
        return None

    df = df.set_index('time').sort_index()

    return df


def sai_tick_bottom(_stock_id, _trade_date):

    log_info("%s %s @ %s", _stock_id, get_name(_stock_id), _trade_date)

    tick_set_sina_mode()

    df = get_tick(_stock_id, _trade_date)
    if df is None :
        log_error("warn: stock %s, %s is None, next", _stock_id, _trade_date)
        return -1, -1, -1

    # log_debug("\n%s", df)

    bottom = min(df['price'])
    # log_info("min: %.2f", bottom)

    len1 = len(df)
    sum1 = df['volume'].sum()
    vol1 = df['volume'].sum()
    # log_debug("df1: len1: %d, vol1: %d, sum1: %.2f\n%s", len1, vol1, sum1, df)

    df2  = df[df.price <= bottom]

    len2 = len(df2)
    sum2 = df2['volume'].sum()
    vol2 = df2['volume'].sum()
    # log_debug("df2: len2: %d, vol2: %d, sum2: %.2f\n%s", len2, vol2, sum2, df2)

    time_rate = 1.0 * len2 / len1
    sum_rate  = 1.0 * sum2 / sum1
    sao_rate =  1.0 * (sum2 * len1) / (sum1 * len2)

    """
    log_info("time时间片占比: %.2f / 8", time_rate * 8)
    log_info("sum 成交额占比: %.2f%%", 100 * sum_rate)
    log_info("扫货力度:   %.2f", sao_rate)
    """

    return time_rate, sum_rate, sao_rate


#######################################################################
if __name__=="__main__":
    sailog_set("sairef.log")

    log_info("main begin here!")

    log_info("main ends  bye!")

#######################################################################

# sairef.py
