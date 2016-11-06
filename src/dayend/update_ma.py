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



def get_df_from_table(_stock_id, _table, _db):
    sql = "select * from %s where stock_id='%s' order by pub_date limit 300" % (_table, _stock_id)

    df = pd.read_sql_query(sql, _db);

    return df


def update_one(_stock_id, _table, _db):

    df = get_df_from_table(_stock_id, _table, _db)

    if df is None:
        log_error("stock %s no data, exit", _stock_id)
        return

    df = df.sort_index(ascending=True)

    sc = df['close_price']

    # sma5
    se = calc_sma(sc, 5)
    df['ma5'] = se;

    # sma10
    se = calc_sma(sc, 10)
    df['ma10'] = se;

    # sma20
    se = calc_sma(sc, 20)
    df['ma20'] = se;

    # sma30
    se = calc_sma(sc, 30)
    df['ma30'] = se;

    # sma60
    se = calc_sma(sc, 60)
    df['ma60'] = se;

    # macd: ema(12), ema(26), diff, dea(9), macd
    sm, sn, sd, se, sa = calc_macd_list0(sc, 12, 26, 9)
    df['ema12'] = sm;
    df['ema26'] = sn;
    df['diff']  = sd;
    df['dea']   = se;
    df['macd']  = sa;

    """
    update_df_to_db(df, _db)  # good
    """

    #log_debug("hi\n%s", df.loc[:, ['pub_date', 'pub_time', 'close_price', 'macd', 'diff', 'dea']])

    return

def update_ma(_stocks, _table, _db):

    for row_index, row in _stocks.iterrows():
        stock_id = row_index
        stock_id = "000002"
        log_debug("---stock is %s",  stock_id)
        update_one(stock_id, _table, _db)
        break

    return


def work():
    db = db_init()

    # TODO: get table name from ARGV
    table = "tbl_day"

    #  get stock list
    stocks = get_stock_list_table(table, db)
    if stocks is None:
        log_error("list is none")
        return -1

    update_ma(stocks, table, db)

    db_end(db)

    return 0

def init():
    sailog_set("updatema.log")

#######################################################################

def main():
    init()

    log_debug("let's begin here!")

    work()

    log_debug("main ends, bye!")

    return

main()
exit()

#######################################################################

# update_ma.py
