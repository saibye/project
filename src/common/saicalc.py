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

    """
    # create result set
    se = pd.Series(0.0, _sc.index)
    """

    l1 = []      # result list
    l2 = []      # n container
    l2_len = 0   # size of l2
    l2_fst = 0.0 # first element

    rownum = 0
    total  = 0.0
    for s_index, s_val in _sc.iteritems():
        rownum = rownum + 1
        total  = total + s_val

        # keep container updated and just N size
        l2.append(s_val)
        if l2_len == _n :
            l2_fst = l2.pop(0)
        else :
            l2_len = l2_len + 1

        if rownum < _n :
            l1.append(0.0)
            #log_debug("%04d less than %d", rownum, _n)
            continue

        elif rownum == _n :
            l1.append(total/_n)
            # se[s_index] = total / _n
            # log_debug("%04d: sma is %.2f", rownum, se[s_index])
            continue

        else :
            # old version: cost much time
            #se[s_index] = _sc.head(rownum).tail(_n).mean()

            # rownum > _n
            # pop the first one
            total = total -  l2_fst #_sc[rownum - _n-1]
            # se[s_index] = total / _n
            l1.append(total/_n)
            # log_debug("%04d: sma is %.2f", rownum, se[s_index])
            # log_debug("%04d: sma is %.2f", rownum, l1[-1])

    # create result set from list. 2016/8/3
    se = pd.Series(l1, _sc.index)

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
        elif rownum == _n:
            ep1  = _sc.head(_m).mean()
            ep2  = _sc.head(_n).mean()
            #log_debug("%04d: initial value is %.2f, %.2f", rownum, ep1, ep2)
            continue;
        elif rownum > _n:
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



# dynamic mode: calculate ema12, ema26, diff
# input: close price, ema_m, ema_, diff, m, n 
#   the input Series must be sorted and ordered
# return nothing
def calc_diff_dynamic(_close, _ema_m, _ema_n, _diff,  _m, _n):
    pd.options.mode.chained_assignment = None
    # log_debug("diff = ema%d - ema%d...", _m, _n)

    # get ema_factor
    fac1 = ema_factor(_m)
    fac2 = ema_factor(_n)
    # log_debug("ema_factor is %.3f, %.3f", fac1, fac2)

    # assign init value
    ep1 = _close.head(_m).mean()
    ep2 = _close.head(_n).mean()

    e1 = 1
    e2 = 1
    rownum = 0
    for s_index, s_val in _close.iteritems():
        rownum = rownum + 1

        # ema(12)
        if _ema_m[s_index] > 0 :
            ep1 = _ema_m[s_index]
        else :
            e1  = (s_val - ep1) * fac1 + ep1
            ep1 = e1
            _ema_m.loc[s_index] = e1


        # ema(26)
        if _ema_n[s_index] > 0 :
            ep2 = _ema_n[s_index]
        else :
            e2  = (s_val - ep2) * fac2 + ep2
            ep2 = e2
            _ema_n.loc[s_index] = e2

        # diff = ema(12) - ema(26)
        if e1 > 0 and e2 > 0 :
            di = e1 - e2
            _diff.loc[s_index] = di
            #log_debug("%04d: %s: e1: %.2f, e2: %.2f, diff: %.2f", rownum, s_index, e1, e2, diff)
    return


# dynamic mode: calculate EMA*2, DIFF, DEA and MACD
# input: (m, n, k) => (12, 26, 9)
#   the input Series must be sorted
# It's so frustrated, this new function is much slower than (calc_diff+calc_macd). 2016/7/31
def calc_macd_dynamic(_close, _ema_m, _ema_n, _diff,  _dea, _macd, _m, _n, _k):
    pd.options.mode.chained_assignment = None
    # log_debug("calc macd(%d, %d, %d)", _m, _n, _k)

    # get ema_factor
    fac1 = ema_factor(_m)
    fac2 = ema_factor(_n)
    fac3 = ema_factor(_k)

    # assign init value
    ep1 = _close.head(_m).mean()
    ep2 = _close.head(_n).mean()
    ep3 = -1.0

    e1  = -1.0
    e2  = -1.0
    e3  = -1.0

    di_count = 0
    di_sum   = 0.0
    for s_index, s_val in _close.iteritems():
        # ema(12)
        if _ema_m[s_index] > 0 :
            ep1 = _ema_m[s_index]
        else :
            e1  = (s_val - ep1) * fac1 + ep1
            ep1 = e1
            _ema_m[s_index] = e1


        # ema(26)
        if _ema_n[s_index] > 0 :
            ep2 = _ema_n[s_index]
        else :
            e2  = (s_val - ep2) * fac2 + ep2
            ep2 = e2
            _ema_n[s_index] = e2

        # diff = ema(12) - ema(26)
        if e1 > 0 and e2 > 0 :
            di = e1 - e2
            di_count = di_count + 1
            di_sum  += di
            _diff[s_index] = di
            #log_debug("%04d: %s: e1: %.2f, e2: %.2f, diff: %.2f", rownum, s_index, e1, e2, diff)

        # dea(k), macd
        if di_count <  _k :
            pass
        elif di_count == _k :
            ep3 = di_sum / _k
        else :
            e3  = (di - ep3) * fac3 + ep3
            ep3 = e3;
            _dea[s_index]  = e3
            _macd[s_index] = (di - e3) *2
            # log_debug("%s: macd: %.3f, di: %.3f, dea: %.3f", s_index, (di-e3)*2, di, e3)

    return


# calculate the simple MA * 2: ma(30), ma(60)
# input: close price
#   the input Series must be sorted
# It's frustrated too, this function is slower than (calc_sma+calc_sma). 2016/7/31
def calc_sma2(_sc, _sm, _sn, _m, _n):
    pd.options.mode.chained_assignment = None
    #log_debug("sma2(%d, %d) is ...", _m, _n)

    total_m = 0.0
    total_n = 0.0
    
    rownum  = 0
    for s_index, s_val in _sc.iteritems():
        total_m  = total_m + s_val
        total_n  = total_n + s_val

        if rownum < _m:
            pass
        elif rownum == _m:
            _sm[s_index] = total_m / _m
        else :
            # rownum > _m
            # pop the first one
            total_m = total_m -  0 #_sc[rownum - _m-1]
            _sm[s_index] = total_m / _m
            # log_debug("%04d: sma is %.2f", rownum, [s_index])

        if rownum < _n:
            pass
        elif rownum == _n:
            _sn[s_index] = total_n / _n
        else :
            # rownum > _n
            # pop the first one
            total_n = total_n -  0 #_sc[rownum - _n-1]
            _sn[s_index] = total_n / _n
            # log_debug("%04d: sma is %.2f", rownum, [s_index])

        rownum = rownum + 1

    return


#  2016/8/6 list mode: calculate EMA*2, DIFF, DEA and MACD 
# input: (m, n, k) => (12, 26, 9)
#   the input Series must be sorted
def calc_macd_list(_close, _ema_m, _ema_n, _m, _n, _k):
    pd.options.mode.chained_assignment = None
    # log_debug("calc macd(%d, %d, %d)", _m, _n, _k)

    # get ema_factor
    fac1 = ema_factor(_m)
    fac2 = ema_factor(_n)
    fac3 = ema_factor(_k)

    # assign init value
    ep1 = _close.head(_m).mean()
    ep2 = _close.head(_n).mean()
    ep3 = -1.0

    e1  = -1.0
    e2  = -1.0
    e3  = -1.0

    ema_m = list(_ema_m)
    ema_n = list(_ema_n)

    diff = []
    dea  = []
    macd = []

    idx      = 0
    di_count = 0
    di_sum   = 0.0
    for s_index, s_val in _close.iteritems():
        # ema(12)
        if ema_m[idx] > 0 :
            ep1 = ema_m[idx]
        else :
            e1  = (s_val - ep1) * fac1 + ep1
            ep1 = e1
            ema_m[idx] = e1


        # ema(26)
        if ema_n[idx] > 0 :
            ep2 = ema_n[idx]
        else :
            e2  = (s_val - ep2) * fac2 + ep2
            ep2 = e2
            ema_n[idx] = e2

        # diff = ema(12) - ema(26)
        if e1 > 0 and e2 > 0 :
            di = e1 - e2
            di_count = di_count + 1
            di_sum  += di
        else :
            di = 0.0
        diff.append(di)
        # log_debug("%04d: e1: %.2f, e2: %.2f, diff: %.2f", idx, e1, e2, di)

        # dea(k), macd
        if di_count <  _k :
            e3 = 0.0
            d2 = 0.0
        elif di_count == _k :
            ep3 = di_sum / _k
            e3 = 0.0
            d2 = 0.0
        else :
            e3  = (di - ep3) * fac3 + ep3
            ep3 = e3;
            d2  = (di - e3) * 2
        dea.append(e3)
        macd.append(d2)
        # log_debug("%04d: macd: %.3f, di: %.3f, dea: %.3f", idx, d2, di, e3)

        idx = idx + 1

    return pd.Series(ema_m, _close.index), \
        pd.Series(ema_n, _close.index), \
        pd.Series(diff,  _close.index), \
        pd.Series(dea,   _close.index), \
        pd.Series(macd,  _close.index)



#  2016/8/16
# calculate ema12, ema26, diff
# input: close price
#        _m < _n
#   the input Series must be sorted
# return  ema(_m), ema(_n), diff
def calc_diff_list0(_sc, _m, _n):
    # log_debug("diff = ema%d - ema%d...", _m, _n)

    # assert m < n
    if _m >= _n:
        log_error("error: invalid usage: %d >= %d", _m, _n)
        return -1

    ema_m = []
    ema_n = []
    diffl = []

    # get ema_factor
    fac1 = ema_factor(_m)
    fac2 = ema_factor(_n)
    # log_debug("ema_factor is %.3f, %.3f", fac1, fac2)

    # init value
    ep1  = _sc.head(_m).mean()
    ep2  = _sc.head(_n).mean()

    ep1 = 0
    ep2 = 0
    rownum = 0

    for s_index, s_val in _sc.iteritems():
        rownum = rownum + 1
        if rownum < _n:
            #log_debug("%04d less than %d", rownum, _n)
            ema_m.append(0.0)
            ema_n.append(0.0)
            diffl.append(0.0)
            continue
        elif rownum == _n:
            ep1  = _sc.head(_n).tail(_m).mean()
            ep2  = _sc.head(_n).mean()
            ema_m.append(ep1)
            ema_n.append(ep2)
            diffl.append(ep1-ep2)
            #log_debug("%04d: initial value is %.2f, %.2f", rownum, ep1, ep2)
            continue;
        elif rownum > _n:
            e1 = (s_val - ep1) * fac1 + ep1
            e2 = (s_val - ep2) * fac2 + ep2
            ep1 = e1
            ep2 = e2
            ema_m.append(e1)
            ema_n.append(e2)
            diffl.append(e1-e2)
            #log_debug("%04d: %s: e1: %.2f, e2: %.2f, diff: %.2f", rownum, s_index, e1, e2, diff)

    # create result set
    return pd.Series(ema_m, _close.index), \
        pd.Series(ema_n, _close.index), \
        pd.Series(diffl,  _close.index)



#  2016/8/6 list mode: calculate EMA*2, DIFF, DEA and MACD 
# input: (m, n, k) => (12, 26, 9)
#   the input Series must be sorted
def calc_macd_list0(_close, _m, _n, _k):
    pd.options.mode.chained_assignment = None
    # log_debug("calc macd(%d, %d, %d)", _m, _n, _k)

    # get ema_factor
    fac1 = ema_factor(_m)
    fac2 = ema_factor(_n)
    fac3 = ema_factor(_k)

    # assign init value
    ep1 = _close.head(_m).mean()
    ep2 = _close.head(_n).mean()
    ep3 = -1.0

    e1  = -1.0
    e2  = -1.0
    e3  = -1.0

    ema_m = []
    ema_n = []
    diff  = []
    dea   = []
    macd  = []

    idx      = 0
    di_count = 0
    di_sum   = 0.0
    for s_index, s_val in _close.iteritems():
        idx = idx + 1

        # ema(12)
        if idx < _m:
            ema_m.append(0.0)
        elif idx == _m:
            ep1  = _close.head(_m).mean()
            ema_m.append(ep1)
        else:
            e1  = (s_val - ep1) * fac1 + ep1
            ep1 = e1
            ema_m.append(e1)


        # ema(26)
        if idx < _n:
            ema_n.append(0.0)
        elif idx == _n:
            ep2  = _close.head(_n).mean()
            ema_n.append(ep2)
        else:
            e2  = (s_val - ep2) * fac2 + ep2
            ep2 = e2
            ema_n.append(e2)


        # diff = ema(12) - ema(26)
        if e1 > 0 and e2 > 0 :
            di = e1 - e2
            di_count = di_count + 1
            di_sum  += di
        else :
            di = 0.0
        diff.append(di)
        # log_debug("%04d: e1: %.2f, e2: %.2f, diff: %.2f", idx, e1, e2, di)

        # dea(k), macd
        if di_count <  _k :
            e3 = 0.0
            d2 = 0.0
        elif di_count == _k :
            ep3 = di_sum / _k
            e3  = ep3
            d2  = 0.0
        else :
            e3  = (di - ep3) * fac3 + ep3
            ep3 = e3;
            d2  = (di - e3) * 2
        dea.append(e3)
        macd.append(d2)
        log_debug("%04d: macd: %.3f, di: %.3f, dea: %.3f", idx, d2, di, e3)


    return pd.Series(ema_m, _close.index), \
        pd.Series(ema_n, _close.index), \
        pd.Series(diff,  _close.index), \
        pd.Series(dea,   _close.index), \
        pd.Series(macd,  _close.index)

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
