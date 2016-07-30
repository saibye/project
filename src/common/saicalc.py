#!/usr/bin/env python
# -*- encoding: utf8 -*-

import pandas as pd
import numpy as np

from sailog  import *



def ema_factor(_n):
    return 2.000 / (_n + 1)

# calculate the simple MA
# input: close price
#   the input Series must be sorted
def calc_sma(_sc, _n):
    #log_debug("sma(%d) is ...", _n)

    # create result set
    se = pd.Series(0.0, _sc.index)

    rownum = 0
    total  = 0.0
    for s_index, s_val in _sc.iteritems():
        rownum = rownum + 1
        total  = total + s_val
        if rownum < _n:
            #log_debug("%04d less than %d", rownum, _n)
            continue

        if rownum == _n:
            se[s_index] = total / _n
            # log_debug("%04d: sma is %.2f", rownum, se[s_index])
            continue

        # old version: cost much time
        #se[s_index] = _sc.head(rownum).tail(_n).mean()

        # rownum > _n
        # pop the first one
        total = total - _sc[rownum - _n-1]
        se[s_index] = total / _n
        # log_debug("%04d: sma is %.2f", rownum, se[s_index])

    return se


# calculate ema12, ema26, diff
# input: close price
#        _m < _n
#   the input Series must be sorted
# return diff, ema(_m), ema(_n)
def calc_diff(_sc, _m, _n):
    # log_debug("diff = ema%d - ema%d...", _m, _n)

    # assert m < n
    if _m >= _n:
        log_error("error: invalid usage: %d >= %d", _m, _n)
        return -1

    # create result set
    se = pd.Series(0.0, _sc.index)
    sm = pd.Series(0.0, _sc.index)
    sn = pd.Series(0.0, _sc.index)

    # get ema_factor
    fac1 = ema_factor(_m)
    fac2 = ema_factor(_n)
    # log_debug("ema_factor is %.3f, %.3f", fac1, fac2)

    ep1 = 0
    ep2 = 0
    rownum = 0

    for s_index, s_val in _sc.iteritems():
        rownum = rownum + 1
        if rownum < _n:
            #log_debug("%04d less than %d", rownum, _n)
            continue

        if rownum == _n:
            ep1  = _sc.head(_m).mean()
            ep2  = _sc.head(_n).mean()
            #log_debug("%04d: initial value is %.2f, %.2f", rownum, ep1, ep2)
            continue;

        if rownum > _n:
            e1 = (s_val - ep1) * fac1 + ep1
            e2 = (s_val - ep2) * fac2 + ep2
            ep1 = e1
            ep2 = e2
            diff = e1 - e2
            se[s_index] = diff
            sm[s_index] = e1 
            sn[s_index] = e2
            #log_debug("%04d: %s: e1: %.2f, e2: %.2f, diff: %.2f", rownum, s_index, e1, e2, diff)
    return se, sm, sn


# calculate DEA and MACD
# input: diff
#   the input Series must be sorted
def calc_macd(_sd, _n):
    # log_debug("dea = ema(diff, %d)...", _n)

    # create result set
    se = pd.Series(0.0, _sd.index) # dea
    sa = pd.Series(0.0, _sd.index) # macd

    # get factor
    fac1 = ema_factor(_n)
    # log_debug("ema_factor is %.3f", fac1)

    ep1 = 0
    rownum = 0

    for s_index, s_val in _sd.iteritems():
        rownum = rownum + 1
        if rownum < _n:
            #log_debug("%04d less than %d", rownum, _n)
            continue

        if rownum == _n:
            ep1  = _sd.head(_n).mean()
            #log_debug("%04d: initial value is %.2f", rownum, ep1)
            continue

        if s_val > -0.00001 and s_val < 0.00001:
            #log_info("zero value: %.3f", s_val)
            continue

        if rownum > _n:
            e1  = (s_val - ep1) * fac1 + ep1
            ep1 = e1;
            se[s_index] = e1
            sa[s_index] = (s_val - e1)*2
            #log_debug("%04d: %s: ema: %.2f, di: %.2f", rownum, s_index, e1, s_val)
    return se, sa

if __name__ == "__main__":
    sailog_set("saicalc.log")

    df = pd.DataFrame()

    sc = pd.Series(range(40))
    log_debug("before: %s", sc)

    ma = calc_sma(sc, 5)

    df['close'] = sc
    df['sma']   = ma
    log_debug("\n%s", df)

    di, ema1, ema2 = calc_diff(sc, 7, 15)
    df['ema1'] = ema1
    df['ema2'] = ema2
    df['diff'] = di
    log_debug("\n%s", df)

    dea, macd = calc_macd(di, 9)
    df['dea']  = dea
    df['macd'] = macd
    log_debug("\n%s", df)


# saicalc.py
