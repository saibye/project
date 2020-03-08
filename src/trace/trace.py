#!/usr/bin/env python
# -*- encoding: utf8 -*-

import os
import _thread

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from common  import *
from pub     import *


g_photo_dir = './'


def trace_plot(_date, _uid, _stock_id, _ma_list, _db):
    log_info('trace_plot: begin')

    global g_photo_dir
    photo_path = '%s/%s.png' % (g_photo_dir, _stock_id)

    till_date = _date

    df = sai_fmt_simple(_stock_id, till_date, _db)
    log_info("simple: \n%s", df)

    df = df.set_index('pub_date').sort_index(ascending=True)
    log_info("new: \n%s", df)


    """
    df['MA20'] 	= df['close_price'].rolling(20).mean()
    df['MA50']	= df['close_price'].rolling(50).mean()
    df['MA200'] = df['close_price'].rolling(200).mean()
    """

    log_info("ma-list1: %s", _ma_list)
    for ma in _ma_list:
        ma_name = 'MA%d' % (ma)
        df[ma_name] = df['close_price'].rolling(ma).mean()


    #---------------------------------------------------------#
    #---------------------------------------------------------#
    #---------------------------------------------------------#
    # plot
    plot_len = int(sai_conf_get2('boot', 'plot_len'))
    log_info("plot-len: %d", plot_len)
    df = df.tail(plot_len)

    # This can clear context
    fig = plt.figure()

    df['close_price'].plot(label='close price', title=_stock_id, ls='-', lw=0.8, color = 'black', figsize=(10,5))

    """
    df['MA20'].plot(label='MA20', color='red', lw=0.2)
    df['MA50'].plot(label='MA50', color='green', lw=0.3)
    df['MA200'].plot(label='MA200', color='blue', lw=0.5)
    """

    for ma in _ma_list:
        ma_name = 'MA%d' % (ma)
        df[ma_name].plot(label=ma_name, lw=0.3)
        log_info('plot: %s', ma_name)

    plt.savefig(photo_path, dpi=300)

    # plt.show()

    # email
    subject = 'T: %s#%s' % (_stock_id, _date)
    body = '%s, %s' % (_date, _stock_id)
    # saimail_photo(subject, body, photo_path)
    _thread.start_new_thread(saimail_photo, (subject, body, photo_path) )

    log_info('trace_plot: end')

    return 0


def trace_one_stock(_date, _uid, _stock_id, _db):
    log_info('trace_one_stock: begin')

    log_info('id: [%s+%s]', _uid, _stock_id)

    sql = "select ma from t_trc_ma where user_id = '%s' order by ma " % (_uid)
    log_info('reg  sql: [%s]', sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info('(P)error: df is None')
        return -1
    else :
        log_info('df-ma length: %d', len(df))

    ma_list = []
    for idx, row in df.iterrows():
        ma = row['ma']
        ma_list.append(ma)
        log_info(">>>>>> ma:\t [%s, %s, %d]", _uid, _stock_id, ma)

    log_info("ma-list: %s", ma_list)
    trace_plot(_date, _uid, _stock_id, ma_list, _db)

    log_info('trace_one_stock: end')

    return 0

'''
  stock_id
0   000725
1   601066
'''
def trace_one_user(_date, _uid, _db):
    log_info('trace_one_user: begin')

    log_info('uid: [%s]', _uid)

    sql = "select stock_id from t_trc_reg where user_id = '%s' order by stock_id" % (_uid)
    log_info('reg  sql: [%s]', sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info('(P)error: df is None')
        return -1
    else :
        log_info('df-reg length: %d', len(df))
    
    for idx, row in df.iterrows():
        stock_id = row['stock_id']
        log_info(">>>> reg:\t [%s, %s]", _uid, stock_id)
        trace_one_stock(_date, _uid, stock_id, _db)

    log_info('trace_one_user: end')

    return 0


def trace_get_date(_trade_date):

    trade_date = ''

    if len(_trade_date) == 10:
        trade_date = _trade_date
        log_info('use [%s] as a date', trade_date)
    elif len(_trade_date) <= 3:
        offset = 0 - int(_trade_date)
        trade_date = get_date_by(offset)
        log_info('fetch date[%s] by offset[%d]', trade_date, offset)
    else:
        trade_date = get_date_by(0)
        log_info('use today', trade_date)

    return trade_date


def production(_db):

    log_info('(P)mode: begin')

    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)

    # till date
    till_date = sai_conf_get2('boot', 'till_date')
    till_date = trace_get_date(till_date)
    log_info("(P)till-date: [%s]", till_date)

    # fetch len
    fetch_len = int(sai_conf_get2('boot', 'fetch_len'))
    sai_fmt_set_fetch_len(fetch_len)
    log_info("(P)fetch-len: [%d]", fetch_len)


    sql = 'select * from t_trc_user'
    log_info('user sql: [%s]', sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info('(P)error: df is None')
        return -1
    else :
        df.set_index('user_id', inplace=True)
        log_info('(P)df-user length: %d', len(df))

    for idx, row in df.iterrows():
        log_info(">> uid: [%s]", idx)
        uid = idx 
        uname = row['user_name']
        umail = row['user_mail']
        enable = row['enable']
        log_info(">> detail: [%s], [%s], [%s]", uname, umail, enable)
        if enable == '1':
            log_info('user [%s, %s] enabled', uid, uname)
        else:
            log_info('user [%s, %s] disabled, ignore', uid, uname)
            continue

        trace_one_user(till_date, uid, _db)

    log_info('(P)mode: end')

    return 0



def work():
    #
    sai_load_conf2('trace.cfg')

    debug_mode = sai_conf_get2('boot', 'debug')
    if debug_mode == 'yes':
        log_debug('DEBUG mode is YES.')

    global g_photo_dir
    g_photo_dir = "%s/project/tmp" % (os.getenv('HOME'))
    log_info("photo-dir: [%s]", g_photo_dir)


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

    log_info("--end")

# trace.py
