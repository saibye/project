#!/usr/bin/env python
# -*- encoding: utf8 -*-

from sailog  import *

def get_buy_sell_rate(_df, _base):
    rate = 0.0

    buy  = 0
    sell = 0

    # for sina_dd
    # _base = _base * 100

    gp = _df[_df.volume > _base].groupby('type')['volume'].sum()

    for s_idx, s_val in gp.iteritems():
        log_debug("%s, %s", s_idx, s_val)
        if s_idx == "买盘":
            buy = s_val
        elif s_idx == "卖盘":
            sell = s_val
        else :
            pass

    if buy > 0 and sell > 0:
        rate = 1.0 * buy / sell
        
    return rate


def get_rate_list(_df, _list):
    rs = []

    for base in _list :
        rate = get_buy_sell_rate(_df, base)
        rs.append(rate)
        log_debug("base: %d, rate: %.2f", base, rate)

    return rs

def check_df_rates(_df):
    lst = [100, 200, 400, 800, 1000, 2000, 3000]
    exp = [1,   1,   1,   1,   1,    2,    6]
    exp = [2,   2,   2,   2.7, 3.5,  1.5,  1]
    exp = [2,   1.8, 1,   1,   1,    1,    1]
    exp = [2,   2,   2,   2,   1,    1,    1]
    exp = [4,   4,   9,   15,  1,    1,    1]

    rs = get_rate_list(_df, lst)

    rank = 0
    idx = 0
    for i in rs:
        if i < 1 and i != 0.0:
            rank = -1
            log_debug("[%d, %.2f]: buy less than sell, means bad", lst[idx], i)
            break

        if i > 10:
            rank += 10000
        elif i >= 6:
            rank += 1000
        elif i >= 4:
            rank += 100
        elif i >= 3:
            rank += 10
        elif i >= 2:
            rank += 1

        idx += 1

    return rank

# end
