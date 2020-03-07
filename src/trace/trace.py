#!/usr/bin/env python
# -*- encoding: utf8 -*-

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from common  import *
from pub     import *




def trace_plot(_uid, _stock_id, _ma_list, _db):
    log_info('trace_plot: begin')

    length = 500
    sai_fmt_set_fetch_len(length)

    till_date = '2020-03-06'

    # df = sai_fmt_set(_stock_id, till_date, mode, length, _db)
    df = sai_fmt_simple(_stock_id, till_date, _db)
    log_info("simple: \n%s", df)

    df = df.set_index('pub_date').sort_index(ascending=True)
    log_info("new: \n%s", df)

    df['MA5']  	= df['close_price'].rolling(5).mean()
    df['MA10'] 	= df['close_price'].rolling(10).mean()
    df['MA20'] 	= df['close_price'].rolling(20).mean()
    df['MA50']	= df['close_price'].rolling(50).mean()
    df['MA200'] = df['close_price'].rolling(200).mean()

    df = df.tail(300)

    df['close_price'].plot(label='close price', title=_stock_id, ls='-', lw=0.8, color = 'black', figsize=(10,5))
    #df['MA5'].plot(label='MA5', color='red')
    #df['MA10'].plot(label='MA10', color='grey')
    df['MA20'].plot(label='MA20', color='red', lw=0.2)
    df['MA50'].plot(label='MA50', color='blue', lw=0.3)
    df['MA200'].plot(label='MA200', color='m', lw=0.5)
    
    plt.xlabel('date')
    plt.ylabel('close')
    # plt.savefig(_stock_id+'.png', dpi=300)
    plt.savefig(_stock_id+'.png')
    plt.show()

    log_info('trace_plot: end')

    return 0


def trace_one_stock(_uid, _stock_id, _db):
    log_info('trace_one_stock: begin')

    log_info('id: [%s+%s]', _uid, _stock_id)

    sql = "select ma from t_trc_ma where user_id = '%s' order by ma " % (_uid)
    log_info('reg  sql: [%s]', sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info('(P)error: df is None')
        return -1
    else :
        log_info('ma length: %d', len(df))

    ma_list = []
    for idx, row in df.iterrows():
        ma = row['ma']
        ma_list.append(ma)
        log_info(">>>>>> ma:\t [%s, %s, %d]", _uid, _stock_id, ma)

    log_info("ma-list: %s", ma_list)
    trace_plot(_uid, _stock_id, ma_list, _db)

    log_info('trace_one_stock: end')

    return 0

'''
  stock_id
0   000725
1   601066
'''
def trace_one_user(_uid, _db):
    log_info('trace_one_user: begin')

    log_info('uid: [%s]', _uid)

    sql = "select stock_id from t_trc_reg where user_id = '%s' order by stock_id" % (_uid)
    log_info('reg  sql: [%s]', sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info('(P)error: df is None')
        return -1
    else :
        log_info('reg length: %d', len(df))
    
    for idx, row in df.iterrows():
        stock_id = row['stock_id']
        log_info(">>>> reg:\t [%s, %s]", _uid, stock_id)
        trace_one_stock(_uid, stock_id, _db)

    log_info('trace_one_user: end')

    return 0


def production(_db):

    log_info('(P)mode: begin')

    sql = 'select * from t_trc_user'
    log_info('user sql: [%s]', sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info('(P)error: df is None')
        return -1
    else :
        df.set_index('user_id', inplace=True)
        log_info('(P)user length: %d', len(df))

    for idx, row in df.iterrows():
        log_info("-- %s --", idx)
        uid = idx 
        uname = row['user_name']
        umail = row['user_mail']
        enable = row['enable']
        log_info(">> user: [%s], [%s], [%s]", uname, umail, enable)
        if enable == '1':
            log_info('user [%s, %s] enable', uid, uname)
        else:
            log_info('user [%s, %s] disabled, ignore', uid, uname)
            continue

        trace_one_user(uid, _db)

    log_info('(P)mode: end')

    return 0



def debug():
    log_info('this is debug mode.')

    return



def work():
    #
    sai_load_conf2('trace.cfg')

    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)

    debug_mode = sai_conf_get2('debug', 'enable')
    if debug_mode == 'yes':
        log_debug('debug mode is YES.')

    db = db_init()
    saiobj.g_db = db

    production(db)

    db_end(db)


if __name__=="__main__":
    sailog_set("trace.log")
    sailog_set_info()

    if today_is_weekend():
        log_info('weekend, exit')
        work()
    else:
        log_info('workday, run')
        work()

    log_debug("--end")

# trace.py
