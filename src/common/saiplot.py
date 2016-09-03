#!/usr/bin/env python
# -*- encoding: utf8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import tushare as ts
import time

from sailog  import *


def saiplot(_df, _volume):
    _df['buy']  = _df[_volume]
    _df['sell'] = _df[_volume]
    _df.loc[_df.type=='卖盘', 'buy']  = 0
    _df.loc[_df.type=='买盘', 'sell'] = 0

    _df = _df.set_index('time').sort_index()

    kk = _df.loc[:, ['buy', 'sell']].cumsum()

    kk.buy.plot(color='r')
    kk.sell.plot(color='g')

    plt.show()
    return


if __name__=="__main__":
    stock   = '000885'
    day     = '2016-08-10'
    day     = '2016-08-03'
    # df = ts.get_sina_dd(stock, date=day)
    df = ts.get_tick_data(stock, date=day)
    if df is None or df.empty:
        print "no data"
    else:
        df = df[df.volume >= 100]
        print "good: \n%s" % df
        saiplot(df, 'volume')



# saiplot.py
