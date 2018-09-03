#!/usr/bin/env python
# -*- encoding: utf8 -*-


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



"""
应用场景:
一天结束，把新采集的数据计算，
得到diff, dea, macd，
并更新到数据库
"""

#######################################################################


"""
1. get data from table
2. computate ma30, ma60, ema, diff, dea
3. save data to table
"""

def get_df_from_db(_stock_id, _db):
    sql = "select * from tbl_30min t where stock_id='%s' order by pub_date, pub_time limit 1000" % _stock_id

    df = pd.read_sql_query(sql, _db);

    return df

def get_update_sql_row(_row):
    pub_date  = _row['pub_date']
    pub_time  = _row['pub_time']
    pub_time  = str(pub_time).split()[2] # timedelta "0 days 14:00:00" -> str "14:00:00" 2016/7/10
    stock_loc = _row['stock_loc']
    stock_id  = _row['stock_id']
    ma30  = _row['ma30']
    ma60  = _row['ma60']
    ema12 = _row['ema12']
    ema26 = _row['ema26']
    diff  = _row['diff']
    dea   = _row['dea']
    macd  = _row['macd']

    sql = "update tbl_30min set ma30 = '%.2f', ma60 = '%.2f', \
ema12='%.2f', ema26 = '%.2f', diff='%.2f', dea='%.2f', macd='%.2f' \
where pub_date='%s' and pub_time='%s' and stock_loc='%s' and stock_id='%s'" % \
           (ma30, ma60, ema12, ema26, diff, dea, macd,
            pub_date, pub_time, stock_loc, stock_id)

    return sql


def update_df_to_db(_df, _db):
    rownum = 0
    for row_index, row in _df.iterrows():
        rownum = rownum + 1
        # TODO if ema12 is not zero, next
        sql = get_update_sql_row(row)
        sql_to_db(sql, _db)

    return




def update_one(_stock_id, _db):

    df = get_df_from_db(_stock_id, _db)

    df = df.sort_index(ascending=True)

    if df is None:
        log_error("stock %s no data, exit", _stock_id)
        return

    #df = df.set_index(['pub_date', 'pub_time', 'stock_id', 'stock_loc'])

    # sma30
    se = calc_sma(df['close_price'], 30)
    df['ma30'] = se;

    # sma60
    se = calc_sma(df['close_price'], 60)
    df['ma60'] = se;

    # macd: ema(12), ema(26), diff, dea(9), macd
    sd, sm, sn = calc_diff(df['close_price'], 12, 26)
    df['ema12'] = sm;
    df['ema26'] = sn;
    df['diff']  = sd;

    sd, sa = calc_macd(df['diff'], 9)
    df['dea']  = sd;
    df['macd'] = sa;

    # comment just for test 2016/7/30
    update_df_to_db(df, _db)  # good

    #log_debug("hi\n%s", df.loc[:, ['pub_date', 'pub_time', 'close_price', 'macd', 'diff', 'dea']])

    return

def update_ma_30min(_stocks, _db):

    rownum = 0
    for row_index, row in _stocks.iterrows():
        rownum = rownum + 1
        log_debug("---stock is %s",  row_index)
        stock_id = row_index
        update_one(stock_id, _db)

    return


def work():
    db = db_init()

    #  compute and update
    stocks = get_stock_list_df_db(db)

    update_ma_30min(stocks, db)

    db_end(db)


#######################################################################

def main():
    sailog_set("updatema.log")
    log_debug("let's begin here!")

    work()

    log_debug("main ends, bye!")
    return

main()
exit()

#######################################################################

# update_ma_30min.py
