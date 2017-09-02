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
并保存数据库
"""

#######################################################################


"""
1. get data from table
2. computate ma30, ma60, ema, diff, dea
3. save data to table
"""

def get_kday_tech_sql_row(_row):
    dt = get_today()
    tm = get_time()

    pub_date    = _row['pub_date']
    stock_loc   = _row['stock_loc']
    stock_id    = _row['stock_id']
    close_price = _row['close_price']

    ma5   = _row['ma5']
    ma10  = _row['ma10']
    ma20  = _row['ma20']
    ma30  = _row['ma30']
    ma60  = _row['ma60']
    ma120 = _row['ma120']
    ma150 = _row['ma150']

    ema12 = _row['ema12']
    ema26 = _row['ema26']
    diff  = _row['diff']
    dea   = _row['dea']
    macd  = _row['macd']

    sql = "insert into tbl_day_tech \
(pub_date, stock_id, stock_loc, close_price, \
ma5, ma10, ma20, ma30, ma60, ma120, ma150, \
ema12, ema26, diff, dea, macd, \
inst_date, inst_time) \
values ('%s', '%s', '%s',  '%s', \
'%.2f', '%.2f', '%.2f', '%.2f', \
'%.2f', '%.2f', '%.2f', \
'%.2f', '%.2f', '%.2f', '%.2f', '%.2f', \
'%s', '%s')" % \
   (pub_date, stock_id, stock_loc, close_price,
    round(ma5, 2), round(ma10, 2), round(ma20, 2), round(ma30, 2),
    round(ma60, 2), round(ma120, 2), round(ma150, 2),
    round(ema12, 2), round(ema26, 2), round(diff, 2), round(dea, 2), round(macd, 2),
    dt, tm)

    # log_debug("%s", sql)

    return sql


def kday_tech_to_db(_df, _db):
    rownum = 0
    for row_index, row in _df.iterrows():
        # rownum = rownum + 1

        sql = get_kday_tech_sql_row(row)

        sql_to_db(sql, _db)

    return



def get_kday_from_db(_stock_id, _db):
    sql = "select * from tbl_day where stock_id='%s' order by pub_date desc limit 300" % _stock_id

    df = pd.read_sql_query(sql, _db)

    return df


def clear_kday_tech(_stock_id, _db):
    sql = "delete from tbl_day_tech where stock_id='%s'" % _stock_id

    return sql_to_db(sql, _db)


def calc_kday_tech_one(_stock_id, _db):

    df = get_kday_from_db(_stock_id, _db)

    if df is None:
        log_error("stock %s no data, exit", _stock_id)
        return

    if df.empty:
        log_error("stock %s no data2, exit", _stock_id)
        return


    # delete old data
    clear_kday_tech(_stock_id, _db)


    df = df.sort_index(ascending=False)

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

    # sma120
    se = calc_sma(sc, 120)
    df['ma120'] = se;

    # sma150
    se = calc_sma(sc, 150)
    df['ma150'] = se;

    # sma200
    se = calc_sma(sc, 200)
    df['ma200'] = se;

    # macd: ema(12), ema(26), diff, dea(9), macd
    sm, sn, sd, se, sa = calc_macd_list0(sc, 12, 26, 9)
    df['ema12'] = sm;
    df['ema26'] = sn;
    df['diff']  = sd;
    df['dea']   = se;
    df['macd']  = sa;


    kday_tech_to_db(df, _db)  # good

    # log_debug("hi\n%s", df.loc[:, ['pub_date', 'close_price', 'ma20', 'macd', 'diff', 'dea']])

    return

def kday_tech(_stocks, _db):

    for row_index, row in _stocks.iterrows():
        stock_id = row_index
        log_debug("---stock is %s",  stock_id)
        calc_kday_tech_one(stock_id, _db)

    return


def work():
    db = db_init()

    tbl = "tbl_day"

    #  get stock list
    stocks = get_stock_list_table(tbl, db)
    if stocks is None:
        log_error("list is none")
        return -1

    kday_tech(stocks, db)

    db_end(db)

    return 0

def init():
    sailog_set("kday_tech.log")

#######################################################################

def main():
    init()

    log_debug("let's begin here!")

    if sai_is_product_mode():
        if today_is_weekend():
            log_info("today is weekend, exit")
        else:
            log_info("today is workday, come on")
            work()
    else:
        work()

    log_debug("main ends, bye!")

    return

main()
exit()

#######################################################################

# kday_tech.py
