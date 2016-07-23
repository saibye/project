#!/usr/bin/env python
# -*- encoding: utf8 -*-

import pandas as pd
import numpy as np


def sma(_df, _n):
    m = _df['close'].head(_n).mean()
    print "sma%d is %.2f" % (_n, m);

def factor(_n):
    return 2.000 / (_n + 1)

def ema(_df, _n):
    #print "ema%d is ..." % (_n)
    df = _df.sort_index(ascending=True)

    fac = factor(_n)
    #print "factor is %.3f" % fac

    # create result set
    se = pd.Series(0.0, _df.index)

    ep = 0
    rownum = 0
    for row_index, row in df.iterrows():
        rownum = rownum + 1
        if rownum < _n:
            print "%04d less than %d" % (rownum, _n)
            continue

        if rownum == _n:
            ep  = df['close'].head(_n).mean()
            se[row_index] = ep
            print "%04d: initial value is %.2f" % (rownum, ep)
            continue;

        if rownum > _n:
            e1 = (row['close'] - ep) * fac + ep
            ep = e1;
            se[row_index] = e1
            print "%04d: %s: e1: %.2f, c: %.2f" % (rownum, row_index, e1, row['close'])
    return se


def diff(_df, _m, _n):
    print "diff = ema%d - ema%d..." % (_m, _n)

    # assert m < n
    if _m >= _n:
        print "error: invalid usage: %d >= %d" % (_m, _n)
        return -1

    # ensure ascending
    df = _df.sort_index(ascending=True)

    # create result set
    se = pd.Series(0.0, _df.index)

    # get factor
    fac1 = factor(_m)
    fac2 = factor(_n)
    print "factor is %.3f, %.3f" % (fac1, fac2)

    ep1 = 0
    ep2 = 0
    rownum = 0

    for row_index, row in df.iterrows():
        rownum = rownum + 1
        if rownum < _n:
            print "%04d less than %d" % (rownum, _n)
            continue

        if rownum == _n:
            ep1  = df['close'].head(_m).mean()
            ep2  = df['close'].head(_n).mean()
            print "%04d: initial value is %.2f, %.2f" % (rownum, ep1, ep2)
            continue;

        if rownum > _n:
            e1 = (row['close'] - ep1) * fac1 + ep1
            e2 = (row['close'] - ep2) * fac2 + ep2
            ep1 = e1;
            ep2 = e2;
            diff = e1 - e2
            se[row_index] = diff
            print "%04d: %s: e1: %.2f, e2: %.2f, diff: %.2f, c: %.2f" \
                % (rownum, row_index, e1, e2, diff, row['close'])
    return se


def dea(_df, _n):
    print "dea = ema(diff, %d)..." % (_n)

    # ensure ascending
    df = _df.sort_index(ascending=True)

    # create result set
    se = pd.Series(0.0, _df.index)

    # get factor
    fac1 = factor(_n)
    print "factor is %.3f" % (fac1)

    ep1 = 0
    rownum = 0

    for row_index, row in df.iterrows():
        rownum = rownum + 1
        if rownum < _n:
            print "%04d less than %d" % (rownum, _n)
            continue

        if rownum == _n:
            ep1  = df['close'].head(_n).mean()
            print "%04d: initial value is %.2f" % (rownum, ep1)
            continue

        if row['diff'] > -0.00001 and row['diff'] < 0.00001:
            print "zero value: %.3f" % row['diff']
            continue

        if rownum > _n:
            e1 = (row['diff'] - ep1) * fac1 + ep1
            ep1 = e1;
            se[row_index] = e1
            print "%04d: %s: ema: %.2f, diff: %.2f" \
                % (rownum, row_index, e1, row['diff'])
    return se


def calc_sma(_df, _n):
    print "sma(%d) is ..." % (_n)
    df = _df.sort_index(ascending=True)

    # create result set
    se = pd.Series(0.0, _df.index)

    rownum = 0
    for row_index, row in df.iterrows():
        rownum = rownum + 1
        if rownum < _n:
            #print "%04d less than %d" % (rownum, _n)
            continue

        se[row_index] = df['close_price'].head(rownum).tail(_n).mean()
        #print "%04d: sma is %.2f" % (rownum, se[row_index])

    return se


# calculate ema12, ema26, diff
def calc_diff(_df, _m, _n):
    print "diff = ema%d - ema%d..." % (_m, _n)

    # assert m < n
    if _m >= _n:
        print "error: invalid usage: %d >= %d" % (_m, _n)
        return -1

    # ensure ascending
    df = _df.sort_index(ascending=True)

    # create result set
    se = pd.Series(0.0, _df.index)
    sm = pd.Series(0.0, _df.index)
    sn = pd.Series(0.0, _df.index)

    # get factor
    fac1 = factor(_m)
    fac2 = factor(_n)
    print "factor is %.3f, %.3f" % (fac1, fac2)

    ep1 = 0
    ep2 = 0
    rownum = 0

    for row_index, row in df.iterrows():
        rownum = rownum + 1
        if rownum < _n:
            #print "%04d less than %d" % (rownum, _n)
            continue

        if rownum == _n:
            ep1  = df['close_price'].head(_m).mean()
            ep2  = df['close_price'].head(_n).mean()
            #print "%04d: initial value is %.2f, %.2f" % (rownum, ep1, ep2)
            continue;

        if rownum > _n:
            e1 = (row['close_price'] - ep1) * fac1 + ep1
            e2 = (row['close_price'] - ep2) * fac2 + ep2
            ep1 = e1;
            ep2 = e2;
            diff = e1 - e2
            se[row_index] = diff
            sm[row_index] = e1 
            sn[row_index] = e2
            #print "%04d: %s: e1: %.2f, e2: %.2f, diff: %.2f, c: %.2f" \
            #    % (rownum, row_index, e1, e2, diff, row['close_price'])
    return se, sm, sn

# calculate DEA and MACD
def calc_macd(_df, _n):
    print "dea = ema(diff, %d)..." % (_n)

    # ensure ascending
    df = _df.sort_index(ascending=True)

    # create result set
    se = pd.Series(0.0, _df.index) # diff
    sa = pd.Series(0.0, _df.index) # macd

    # get factor
    fac1 = factor(_n)
    print "factor is %.3f" % (fac1)

    ep1 = 0
    rownum = 0

    for row_index, row in df.iterrows():
        rownum = rownum + 1
        if rownum < _n:
            #print "%04d less than %d" % (rownum, _n)
            continue

        if rownum == _n:
            ep1  = df['diff'].head(_n).mean()
            #print "%04d: initial value is %.2f" % (rownum, ep1)
            continue

        if row['diff'] > -0.00001 and row['diff'] < 0.00001:
            #print "zero value: %.3f" % row['diff']
            continue

        if rownum > _n:
            e1 = (row['diff'] - ep1) * fac1 + ep1
            ep1 = e1;
            se[row_index] = e1
            sa[row_index] = (row['diff'] - e1)*2
            # print "%04d: %s: ema: %.2f, diff: %.2f"  % (rownum, row_index, e1, row['diff'])
    return se, sa

# saicalc.py
