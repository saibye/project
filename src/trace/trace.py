#!/usr/bin/env python
# -*- encoding: utf8 -*-

import os
import _thread

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from common  import *

import saiobj


def trace_one_stock(_date, _uid, _stock_id, _db):
    log_info('trace_one_stock: begin')

    log_info('id: [%s+%s]', _uid, _stock_id)

    sql = "select ma from t_trc_ma where user_id = '%s' order by ma " % (_uid)
    log_info('reg  sql: [%s]', sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_error('error: df is None')
        return ''
    else :
        log_debug('df-ma length: %d', len(df))

    ma_list = []
    for idx, row in df.iterrows():
        ma = row['ma']
        ma_list.append(ma)
        log_info(">>>>>> ma:\t [%s, %s, %d]", _uid, _stock_id, ma)

    log_info("ma-list: %s", ma_list)
    path = sai_plot(_date, _uid, _stock_id, ma_list, _db)

    log_info('trace_one_stock: end')

    return path

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
        log_info('error: df is None')
        return -1
    else :
        log_info('df-reg length: %d', len(df))
    
    paths = []
    for idx, row in df.iterrows():
        stock_id = row['stock_id']
        log_info(">>>> reg:\t [%s, %s]", _uid, stock_id)
        path = trace_one_stock(_date, _uid, stock_id, _db)
        if len(path) != 0:
            paths.append(path)
        # break # XXX

    if saiobj.g_debug == 'yes':
        log_info('(D) send several photos once: %s', paths)
        subject = 'T: %s' % (_date)
        body = 'Trace at %s' % (_date)
        saimail_photos(subject, body, paths)

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


def debug(_db):

    log_info('(D)begin')

    # till date
    till_date = sai_conf_get2('debug', 'till_date')
    till_date = trace_get_date(till_date)
    log_info("(D)till-date: [%s]", till_date)

    # fetch len
    fetch_len = int(sai_conf_get2('debug', 'fetch_len'))
    sai_fmt_set_fetch_len(fetch_len)
    log_info("(D)fetch-len: [%d]", fetch_len)

    # plot len
    plot_len = int(sai_conf_get2('debug', 'plot_len'))
    saiobj.g_plot_len = plot_len
    log_info("(D)plot-len: [%d]", saiobj.g_plot_len)

    # stock list
    stocks = sai_conf_get2('debug', 'stock_list')
    stock_list = stocks.split(',')
    log_info("(D)stock_list: %s", stock_list)

    uid = 'DEBUG'
    ma_list = [20, 50, 200]

    paths = []
    for i in range(len(stock_list)):
        stock_id = stock_list[i].strip()
        log_info('(D)stock: [%s] begin', stock_id)

        path = sai_plot(till_date, uid, stock_id, ma_list, _db)
        if len(path) != 0:
            paths.append(path)

    log_info('(D)send several photos once: %s', paths)
    subject = 'T-all: %s' % (till_date)
    body = 'Tracing: %s' % (stock_list)
    saimail_photos(subject, body, paths)

    log_info('(D)end')

    return 0


def production(_db):

    log_info('(P)begin')


    # mail
    saiobj.g_to_send_mail = True

    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)

    # till date
    till_date = sai_conf_get2('production', 'till_date')
    till_date = trace_get_date(till_date)
    log_info("(P)till-date: [%s]", till_date)

    # fetch len
    fetch_len = int(sai_conf_get2('production', 'fetch_len'))
    sai_fmt_set_fetch_len(fetch_len)
    log_info("(P)fetch-len: [%d]", fetch_len)

    # plot len
    plot_len = int(sai_conf_get2('production', 'plot_len'))
    saiobj.g_plot_len = plot_len
    log_info("(P)plot-len: [%d]", saiobj.g_plot_len)


    sql = "select * from t_trc_user where user_id !='debug'"
    log_info('(P)user sql: [%s]', sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info('(P)error: df is None')
        return -1
    else :
        df.set_index('user_id', inplace=True)
        log_info('(P)df-user length: %d', len(df))

    for idx, row in df.iterrows():
        log_info("(P)>> uid: [%s]", idx)
        uid = idx 
        uname = row['user_name']
        umail = row['user_mail']
        enable = row['enable']
        log_info("(P)>> detail: [%s], [%s], [%s]", uname, umail, enable)
        if enable == '1':
            log_info('(P)user [%s, %s] enabled', uid, uname)
        else:
            log_info('(P)user [%s, %s] disabled, ignore', uid, uname)
            continue

        trace_one_user(till_date, uid, _db)

    log_info('(P)end')

    return 0



def work(_db):

    log_info('work begin')

    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)

    if saiobj.g_debug == 'yes':
        debug(_db)
    else:
        production(_db)

    log_info('work end')

    return 0



def main():
    #
    sai_load_conf2('trace.cfg')

    debug_mode = sai_conf_get2('sys', 'debug')
    if debug_mode == 'yes':
        saiobj.g_debug = 'yes'
        log_info('(D) means debug mode.')
    else:
        saiobj.g_debug = 'no'
        log_info('(P) means production mode.')

    saiobj.g_photo_dir = "%s/project/tmp" % (os.getenv('HOME'))
    log_info("photo-dir: [%s]", saiobj.g_photo_dir)


    db = db_init()
    saiobj.g_db = db

    work(db)

    db_end(db)

    return


if __name__=="__main__":
    sailog_set("trace.log")
    sailog_set_info()

    if today_is_weekend():
        log_info('weekend, exit')
        # main()
    else:
        log_info('workday, run')
        main()

    log_info("--end")

# trace.py
