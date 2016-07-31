#!/usr/bin/env python
# -*- encoding: utf8 -*-


from sqlalchemy import create_engine
import tushare as ts
import MySQLdb
import time
import pandas as pd
import numpy as np

from saiutil import *
from saidb   import *
from saisql  import *
from saicalc import *
from sailog  import *

#######################################################################


"""
"""

g_map   = {}

def get_df_from_db1(_stock_id, _db):
    #sql = "select * from tbl_30min t where stock_id='%s' order by pub_date desc, pub_time desc limit 300" % _stock_id
    #sql = "select * from tbl_30min t where stock_id='%s' order by pub_date desc, pub_time desc limit 10" % _stock_id
    sql = "select * from tbl_30min t where stock_id='%s' \
           order by pub_date desc, pub_time desc limit 120" % _stock_id

    df = pd.read_sql_query(sql, _db);

    return df

def get_df_from_db2(_stock_id, _db):
    sql = "select * from tbl_30min t where stock_id='%s' \
           order by pub_date desc, pub_time desc limit 10" % _stock_id

    df = pd.read_sql_query(sql, _db);

    return df


def choose_init_one(_stock_id, _db):

    begin = get_micro_second()

    df = get_df_from_db1(_stock_id, _db)

    diff = get_micro_second() - begin
    log_debug("get_df_from_db costs %d", diff)

    if df is None:
        print "stock %s no data, exit" % _stock_id
        return

    df = df.set_index(['pub_date', 'pub_time'])
    df = df.sort_index(ascending=True)

    global g_map
    g_map[_stock_id] = df

    # log_debug("df: \n%s", df.tail())

    return

def choose_init(_stocks, _db):

    for row_index, row in _stocks.iterrows():
        log_debug("---stock is %s",  row_index)
        stock_id = row_index
        choose_init_one(stock_id, _db)
        # break

    return


def choose_merge_one(_stock_id, _db):

    begin = get_micro_second()

    df = get_df_from_db2(_stock_id, _db)

    diff = get_micro_second() - begin
    log_debug("get_df_from_db2 costs %d", diff)

    if df is None:
        print "stock %s no data, exit" % _stock_id
        return

    df = df.set_index(['pub_date', 'pub_time'])
    df = df.sort_index(ascending=True)

    # log_debug("df-merge1: \n%s", df)

    global g_map
    df_prev = g_map[_stock_id]

    # log_debug("df-merge2: \n%s", df_prev)

    #df = pd.merge(df, df_prev) # bad
    #df = pd.concat([df, df_prev]) #bad
    #df = pd.merge(df, df_prev, how='inner', on=['pub_date', 'pub_time']) # bad
    df = pd.concat([df, df_prev]).drop_duplicates().sort_index(ascending=True) # nice, 2016/7/26

    # log_debug("df-merge: \n%s", df)
    g_map[_stock_id] = df

    return


def choose_calc_one(_stock_id):
    global g_map
    df = g_map[_stock_id]

    begin = get_micro_second()

    sc = df['close_price']
    # sma30
    se = calc_sma(sc, 30)
    df['ma30'] = se;

    # sma60
    se = calc_sma(sc, 60)
    df['ma60'] = se;

    """
    # this is slower... 2016/7/31
    calc_sma2(df['close_price'], df['ma30'], df['ma60'], 30, 60)
    """

    log_debug("ma30/60 costs %d", get_micro_second() - begin)

    begin = get_micro_second()
    # macd: ema(12), ema(26), diff, dea(9), macd
    sd, sm, sn = calc_diff(sc, 12, 26)
    df['ema12'] = sm;
    df['ema26'] = sn;
    df['diff']  = sd;
    log_debug("clac_diff costs %d", get_micro_second() - begin)

    """
    """
    # calc_diff_dynamic(df['close_price'], df['ema12'], df['ema26'], df['diff'], 12, 26)
    # calc_diff_dynamic(sc, s_ema12, s_ema26, s_diff, 12, 26)

    begin = get_micro_second()

    sd, sa = calc_macd(sd, 9)
    df['dea']   = sd;
    df['macd']  = sa;

    """
    # this is slower... 2016/7/31
    calc_macd_dynamic(df['close_price'], df['ema12'], df['ema26'], df['diff'], df['dea'], df['macd'], 12, 26, 9)
    """

    log_debug("clac_macd_dynamic costs %d", get_micro_second() - begin)

    return

# execute the algorithm
def choose_rule_one(_stock_id):
    global g_map
    df = g_map[_stock_id]

    begin = get_micro_second()

    """
    # sma30
    se = calc_sma(sc, 30)
    df['ma30'] = se;
    """
    last  = df.tail(1)
    idx   = last.index[0]

    op    = last['open_price'][0]
    close = last['close_price'][0]
    high  = last['high_price'][0]
    low   = last['low_price'][0]

    ma5   = last['ma5'][0]
    ma10  = last['ma10'][0]
    ma20  = last['ma20'][0]
    ma30  = last['ma30'][0]
    ma60  = last['ma60'][0]

    di    = last['diff'][0]
    dea   = last['dea'][0]
    macd  = last['macd'][0]

    vol   = last['deal_total_count'][0]
    v5    = last['vma5'][0]
    v10   = last['vma10'][0]

    log_debug("ma5: %s", ma5)
    minp = min(ma5, ma10, ma20, ma30, ma60)
    maxp = max(ma5, ma10, ma20, ma30, ma60)
    minp = min(ma5, ma10, ma20, ma30)
    maxp = max(ma5, ma10, ma20, ma30)

    rate = minp / maxp * 100
    log_debug("stock: %s, close: %.2f, open: %.2f", _stock_id, close, op)
    log_debug(">>>min: %.2f, max: %.2f, rate: %.2f", minp, maxp, rate)
    log_debug(">>>macd:  %.2f, %.2f, %.2f", macd, di ,dea)
    log_debug(">>>volume:  %.2f, %.2f, %.2f", vol, v5, v10)

    if close > op \
        and close >= maxp \
        and op    <= minp \
        and rate  >= 98 \
        and di    >  -0.1 \
        and vol   > v10 \
        and 1     == 1:
        log_info("buy: %s at %s", _stock_id, idx)

    """
    TODO: add this needs more observation: price uprise, and volume become bigger!
    """
    log_debug("rule_one costs %d", get_micro_second() - begin)

    return


def choose_loop(_stocks, _db):

    for row_index, row in _stocks.iterrows():
        log_debug("---stock2 is %s",  row_index)
        stock_id = row_index
        # remove merge for performance 2016/7/30
        # choose_merge_one(stock_id, _db)

        # calculate ma(30), ma(60), macd
        begin = get_micro_second()
        choose_calc_one(stock_id)
        log_debug("clac_one costs %d", get_micro_second() - begin)

        # check rule
        begin = get_micro_second()
        choose_rule_one(stock_id)
        log_debug("rule_one costs %d", get_micro_second() - begin)
        # break

    return


def work():
    db = db_init()

    #  compute and update
    stocks = get_stock_list_df_db(db)
    log_debug("get stock list: %s",  stocks)

    choose_init(stocks, db)

    log_debug("init succeeds")

    choose_loop(stocks, db)
    log_debug("loop accomplished")

    db_end(db)


#######################################################################

def main():
    print "let's begin here!"

    sailog_set("choose.log")

    begin = get_micro_second()

    work()

    diff = get_micro_second() - begin

    log_debug("work costs %d", diff)

    log_debug("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    """
    for item in sorted(g_map.keys()):
        log_debug("key: %s", item)
        df = g_map[item]
        log_debug("df2: \n%s", df.loc[:, ['close_price', 'macd', 'diff', 'dea', 'ma60']])
        break
    """

    print "main ends, bye!"

    #raw_input()

    return

main()
exit()
print "can't arrive here"

#######################################################################

# choose.py
