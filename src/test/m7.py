#!/usr/bin/env python
# -*- encoding: utf8 -*-

import numpy as np
import matplotlib.pyplot as plt

import baostock as bs
import pandas as pd

def f():
    lg = bs.login()
    print("bs: login code: ", lg.error_code)
    if lg.error_code != "0":
        print("error: login failure: %s, %s" % (lg.error_code, lg.error_msg))
        return 1

    stock_id = 'sz.000725'
    st_date  = '2018-03-01'
    ed_date  = '2020-03-05'

    stock_id = 'sh.601066'
    st_date  = '2017-01-01'
    ed_date  = '2019-08-15'
    rs = bs.query_history_k_data_plus(stock_id,
            "date,code,open,high,low,close,preclose,volume,amount",
            start_date=st_date, end_date=ed_date,
            frequency="d", adjustflag="2")
    print('query_history_k_data_plus: %s, %s' % (rs.error_code, rs.error_msg))
    bs.logout()

    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    df = pd.DataFrame(data_list, columns=rs.fields)

    df["open"]      = pd.to_numeric(df["open"])
    df["close"]     = pd.to_numeric(df["close"])
    df["high"]      = pd.to_numeric(df["high"])
    df["low"]       = pd.to_numeric(df["low"])
    df["preclose"]  = pd.to_numeric(df["preclose"])
    df["volume"]    = pd.to_numeric(df["volume"])
    df["amount"]    = pd.to_numeric(df["amount"])
    df.set_index('date', inplace=True)


    print(df)

    df['MA5']  = df['close'].rolling(5).mean()
    df['MA10'] = df['close'].rolling(10).mean()
    df['MA20'] = df['close'].rolling(20).mean()
    df['MA50'] = df['close'].rolling(50).mean()
    df['MA200'] = df['close'].rolling(200).mean()

    
    fig = plt.figure()

    left, bottom, width, height = 0.1, 0.1, 0.8, 0.8
    ax1 = fig.add_axes([left, bottom, width, height])
    #ax1.plot(df['close'], 'r')
    
    
    df['close'].plot(label='close price', title=stock_id, ls='-', lw=0.8, color = 'black', figsize=(10,5))
    #df['MA5'].plot(label='MA5', color='red')
    #df['MA10'].plot(label='MA10', color='grey')
    df['MA20'].plot(label='MA20', color='red', lw=0.2)
    df['MA50'].plot(label='MA50', color='blue', lw=0.3)
    df['MA200'].plot(label='MA200', color='m', lw=0.5)

    df2 = df.tail(20)
    left, bottom, width, height = 0.2, 0.6, 0.25, 0.25
    ax2 = fig.add_axes([left, bottom, width, height])
    #ax2.plot(df2['close'], 'b')
    df2['close'].plot(lw=0.6, color = 'black')
    df2['MA5'].plot(label='MA50', color='y', lw=0.2)
    df2['MA10'].plot(label='MA10', color='g', lw=0.2)
    
    #plt.xlabel('date')
    #plt.ylabel('close')
    # plt.savefig(stock_id+'.png', dpi=300)
    plt.savefig(stock_id+'.png')
    plt.show()


f()

