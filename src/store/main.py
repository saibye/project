#!/usr/bin/env python
# -*- encoding: utf8 -*-


from sqlalchemy import create_engine
import tushare as ts
import MySQLdb
import time
import pandas as pd
import numpy as np


def get_today():
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    dt = time.strftime("%Y-%m-%d", time.localtime()) 
    return dt

def get_time():
    tm = time.strftime("%H:%M:%S", time.localtime()) 
    return tm 

def row_to_sql(_stock_id, _row_index, _row):
    date1, time1 = _row_index.split()

    sql = "insert into tbl_30min \
(pub_date, pub_time, stock_id, stock_loc, \
open_price, high_price, close_price, low_price, \
price_change, change_rate, deal_total_count, \
ma5, ma10, ma20, \
vma5, vma10, vma20, \
turnover, \
inst_date, inst_time) \
values ('%s', '%s', '%s', '%s',  \
'%.02f', '%.2f', '%.2f', \
'%.2f', '%.2f', '%.2f', \
'%.2f', '%.2f', '%.2f', \
'%.2f', \
'%.2f', '%.2f', '%.2f', '%.2f', \
'%s', '%s')" % \
    (date1, time1, _stock_id, 'cn', 
     _row.loc['open'], _row.loc['high'], _row.loc['close'], _row.loc['low'],
     _row.loc['price_change'], _row.loc['p_change'], _row.loc['volume'],
     _row.loc['ma5'], _row.loc['ma10'], _row.loc['ma20'],
     _row.loc['v_ma5'], _row.loc['v_ma10'], _row.loc['v_ma20'],
     _row.loc['turnover'],
     g_date, g_time)

    return sql


def sql_to_db(_sql, _db):

    # 使用cursor()方法获取操作游标 
    cursor = _db.cursor()

    try:
       # 执行sql语句
       cursor.execute(_sql)
       # 提交到数据库执行
       _db.commit()
    except:
       # 发生错误时回滚
       print "execute sql failed"
       _db.rollback()
    return

def df_to_db(_stock_id, _df, _db):
    print "i'm importing %s" % _stock_id

    for row_index, row in _df.iterrows():
        #print "-----------index is ",  row_index
        date2, time2 = row_index.split()
        #print ("date: %s, time: %s" % (date2, time2))
        #print "close is ", row.loc['close'], ", ma5 is ", row.loc['ma5'], ", change: ", row['p_change']
        sql = row_to_sql(_stock_id, row_index, row)
        #print sql
        sql_to_db(sql, _db)

    return

def clear_stock_from_db(_stock_id, _db):
    sql = "delete from tbl_30min where stock_id = '%s'" % _stock_id
    print sql
    sql_to_db(sql, _db)

def sma(_df, _n):
    m = _df['close'].head(_n).mean()
    print "sma%d is %.2f" % (_n, m);

def factor(_n):
    return 2.000 / (_n + 1)

def ema(_df, _n):
    print "ema%d is ..." % (_n)
    df = _df.sort_index(ascending=True)

    fac = factor(_n)
    print "factor is %.3f" % fac

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
#######################################################################
g_date = get_today()

g_time = get_time()


stock_id    = '002709'
stock_id    = '300028'
start_date  = '2016-05-25'
end_date    = '2016-07-01'
minute      = '30'

def db_init():
    # 打开数据库连接
    db = MySQLdb.connect("182.92.239.6", "tudev", "wangfei", "tu" )
    return db

def db_end(_db):
    # 关闭数据库连接
    _db.close()

def get_stock_list_df():
    df = ts.get_stock_basics()
    return df.sort_index()


def work_one_once(_stock_id, _db):
    print "work_one_once begin %s" % _stock_id

    #df = ts.get_hist_data(_stock_id, start=start_date, end=end_date, ktype=minute)

    # full data
    df = ts.get_hist_data(_stock_id, ktype=minute)
    if df is None :
        print "stock %s no data, next" % _stock_id
        return

    #print df

    # clear previous data
    clear_stock_from_db(_stock_id, _db)

    # import dataframe to db
    df_to_db(_stock_id, df, _db)

    print "work_one_once end"

    return 

def import_once(_stocks):
    db = db_init()

    clear_stock_from_db(stock_id, db)

    for row_index, row in _stocks.iterrows():
        print "---index is ",  row_index
        work_one_once(row_index, db)

    db_end(db)
    print "function ends"


def prototype(_stock_id):
    print "work_prototype begin"

    df = ts.get_hist_data(_stock_id, start=start_date, end=end_date, ktype=minute)

    if df is None :
        print "is none"
    else :
        print "not none"

    #print df
    #print df.head(1)
    #print df

    length = len(df)
    print "total row is ", length

     #clear_stock_from_db(_stock_id, db)
     #df_to_db(df, db)
    sma(df, 5)
    sma(df, 10)
    sma(df, 20)
    sma(df, 30)
    sma(df, 60)
    sma(df, 150)

    s1 = ema(df, 12)
    df['ema12'] = s1

    s2 = ema(df, 26)
    df['ema26'] = s2

    s3 = diff(df, 12, 26)
    df['diff'] = s3

    s4 = dea(df, 9)
    df['dea'] = s4

    print df.sort_index(ascending=True)


    print "work_prototype end"

    return 


def update_ma():
    db = db_init()

    sql = "select concat(pub_date, ' ', pub_time) key_index, t.* from tbl_30min t limit 10"
    df = pd.read_sql_query(sql, db);

    df = df.set_index(['key_index'])

    print df.head()

    db_end(db)
    print "function ends"


def main():
    print "let's begin here!"

    #stocks = get_stock_list_df()
    #import_once(stocks)

    update_ma()

    print "main ends, bye!"
    return

main()
exit()
print "can't arrive here"
#######################################################################

#print ts.get_hist_data('600848',start='2015-01-05',end='2015-01-09')
#print df['close'].head(5)


# main.py
