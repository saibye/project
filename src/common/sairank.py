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


def get_df_rank(_sina_df):

    if _sina_df is None :
        # log_error("warn: df is None, next")
        return -1, "" 

    if _sina_df.empty:
        # log_error("warn: df is empty, next")
        return -2, ""

    if len(_sina_df) <= 5:
        # log_error("warn: df is short: %d, next", len(_sina_df))
        return -3, ""


    length = len(_sina_df)
    open_price  = _sina_df['price'][0]
    close_price = _sina_df['price'][length-1]
    # log_debug("open: %s, close: %s", open_price, close_price)

    if close_price <= 8.0:
        # log_error("warn: price is too cheap, next")
        return -4, ""

    if close_price <= open_price*1.01:
        kk = 9
        content = "price: [%s, %s]-\n" % (open_price, close_price)
    else:
        kk = 0
        content = "price: [%s, %s]\n" % (open_price, close_price)

    factor = close_price / 10.0

    base_list = [200, 400, 800, 1000, 2000, 3000]

    rank = 0.0

    counter5 = 0
    counter10 = 0
    counter20 = 0
    counter30 = 0
    counter40 = 0
    counter50 = 0
    counter_bad = 0
    for base in base_list :
        rank = 0
        net  = 0.0
        buy, sell = get_buy_sell_sum(_sina_df, base)

        diff = buy - sell
        diff2 = diff * factor
        content += "%04d B: %.2f, S: %.2f, N: %.2f, %.2f\n" % \
                    (base, buy/10000.00, sell/10000.00, diff/10000.00, diff2/10000.00)

        diff = diff2
        if diff >= 500000:
            counter50 += 1

        if diff >= 400000:
            counter40 += 1

        if diff >= 300000:
            counter30 += 1

        if diff >= 200000:
            counter20 += 1

        if diff >= 100000:
            counter10 += 1

        if diff >= 30000:
            counter5 += 1

        if diff < 0:
            counter_bad += 1

    if counter50 >= 5:
        rank = 500
    elif counter40 >= 5:
        rank = 400
    elif counter30 >= 5:
        rank = 300
    elif counter20 >= 5:
        rank = 200
    elif counter10 >= 5:
        rank = 100
    elif counter5 >= 5:
        rank = 50

    if counter_bad > 0:
        rank -= 10

    if rank > 0:
        rank += kk

    return  rank, content


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
