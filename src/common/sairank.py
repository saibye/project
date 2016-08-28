#!/usr/bin/env python
# -*- encoding: utf8 -*-

import numpy as np
import pandas as pd
import tushare as ts

from sailog  import *

# volume 单位是手
def get_buy_sell_rate(_df, _base):
    rate = 0.0

    buy  = 0
    sell = 0

    gp = _df[_df.volume > _base].groupby('type')['volume'].sum()

    for s_idx, s_val in gp.iteritems():
        # log_debug("%s, %s", s_idx, s_val)
        if s_idx == "买盘":
            buy = s_val
        elif s_idx == "卖盘":
            sell = s_val
        else :
            pass

    if buy > 0 and sell > 0:
        rate = 1.0 * buy / sell

    net = buy - sell
    message = "base(%d), buy: %d, sell:%d, rate: %.2f, net: %d" % (_base, buy, sell, rate, net)

    return rate, net, message

# volume 单位是手
def get_buy_sell_sum(_df, _base):
    buy  = 0
    sell = 0

    gp = _df[_df.volume >= _base].groupby('type')['volume'].sum()

    for s_idx, s_val in gp.iteritems():
        if s_idx == "买盘":
            buy = s_val
        elif s_idx == "卖盘":
            sell = s_val
        else :
            pass

    return buy, sell


def get_rate_list(_df, _list):
    rs = []
    ns = []
    ms = []

    for base in _list :
        rate, net, mess = get_buy_sell_rate(_df, base)
        rs.append(rate)
        ns.append(net)
        ms.append(mess)
        # log_debug("base: %d, rate: %.2f", base, rate)

    return rs, ns, ms

def check_df_rates(_df):
    lst = [200, 400, 800, 1000, 2000, 3000]

    rs, ns, ms = get_rate_list(_df, lst)

    rank = 0
    idx  = 0
    for i in rs:
        if i < 1 and i != 0.0:
            rank = -1
            # log_debug("[%d, %.2f]: buy less than sell, means bad", lst[idx], i)
            break

        if i > 10:
            rank += 1000
        elif i >= 5:
            if lst[idx] >= 3000:
                rank += 1000
            elif lst[idx] >= 2000:
                rank += 800
            else:
                rank += 600
        elif i >= 2:
            rank += 400
        elif i >= 1.4:
            rank += 200
        elif i >= 1.2:
            rank += 100

        if i == 0.0:
            if lst[idx] == 1000:
                rank -= 200
            elif lst[idx] == 2000:
                rank -= 400
            elif lst[idx] == 3000:
                rank -= 800

        idx += 1

    return rank, rs, ns, ms

if __name__=="__main__":
    sailog_set("sairank.log")
    base_vol = 100
    stock_id = "000736"
    dd_date  = "2016-08-17"
    stock_id = "002694"
    stock_id = "600187"
    stock_id = "600084"
    stock_id = "000002"
    dd_date  = "2016-08-19"
    dd_date  = "2016-08-17"
    stock_id = "002154"
    stock_id = "002694"
    # df = ts.get_tick_data(stock_id, date=dd_date)
    df = ts.get_sina_dd(stock_id, date=dd_date, vol=base_vol)
    if df is None:
        log_debug("None")
    else:
        df['volume'] = df['volume'] / 100 # sina
        df = df.sort_values(by='time')
        # df = df[df.volume >= 200]
        log_debug("size: %d", len(df))
        # df = df.head(580)
        log_debug("data:\n%s", df)
        rank, rs, ns, mess = check_df_rates(df)
        log_debug("rank: %d", rank)

# end
