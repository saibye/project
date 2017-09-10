#!/usr/bin/env python
# -*- encoding: utf8 -*-

from datetime import *

import tushare as ts
import pandas as pd
import numpy as np

from saiutil import *
from saidb   import *
from saisql  import *
from saicalc import *
from sailog  import *
from saitu   import *

#######################################################################


def is_open_time(_date_time):
    dt = str(_date_time)
    if dt.find("09:30") != -1:
        return 1
    return 0

def is_subsequent_open_time(_date_time):
    dt = str(_date_time)
    if dt.find("10:00") != -1:
        return 1
    return 0

def k_unit_one_to_db(_stock_id, _df, _start_date, _db):

    dt = get_today()
    tm = get_time()

    table_name = "tbl_30min"

    # init last close price
    # last_close_price = _df['close'][0]
    # last_close_price = _df.iloc[0,2]

    length = len(_df)


    # XXX: check time is '09:30', 2017-6-18

    # import dataframe to db
    counter = 0
    volume  = 0
    open_volume = 0
    open_price = -1
    for row_index, row in _df.iterrows():
        counter = counter + 1
        trade_date_time = row.loc['date']
        if is_open_time(trade_date_time):
            open_volume = row.loc['volume']
            open_price = row.loc['open']
            log_debug("open: %s -- %.2f", trade_date_time, open_volume)
            continue
        elif is_subsequent_open_time(trade_date_time):
            volume = row.loc['volume'] + open_volume
            if open_volume > 0:
                # use last open-price
                pass
            else:
                open_price = row.loc['open']
            open_volume = 0
            # log_debug("open subsequent: %.2f -- %.2f -- %.3f", row.loc['volume'], volume, open_price)
        else:
            volume = row.loc['volume']
            open_volume = 0
            open_price = row.loc['open']
            # log_debug("others: %s -- %.2f", trade_date_time, volume)


        if counter >= length:
            last_close_price = _df.iloc[counter-1,2]
            log_debug("end-time: %.2f", last_close_price)
        else:
            last_close_price = _df.iloc[counter,2]
            # log_debug("last-clo: %.2f", last_close_price)

        # 前复权
        sql = "insert into tbl_30min \
(pub_date_time, stock_id, stock_loc, \
open_price, high_price, close_price, low_price, \
last_close_price, \
deal_total_count, \
inst_date, inst_time) \
values ('%s', '%s', '%s',  \
'%.2f', '%.2f', '%.2f', '%.2f', \
'%.2f', \
'%.3f', \
'%s', '%s')" % \
       (row.loc['date'], _stock_id, 'cn', 
        open_price, row.loc['high'], row.loc['close'], row.loc['low'],
        last_close_price,
        volume / 1000.00, 
        dt, tm)

        # last_close_price = row.loc['close']

        # log_debug("%s", sql)
        rv = sql_to_db_nolog(sql, _db)
        if rv != 0:
            log_error("error: sql_to_db30: %s", sql)
            return 0

    log_debug("%s: processed: %d", _stock_id, counter);

    return 0


def k_unit_get_max_date(_stock_id, _db):
    table_name = "tbl_30min"
    df = get_max_pub_date_time_kunit(_stock_id, table_name, _db)

    if df is None :
        log_error("warn: stock %s max-pub-date is None, next", _stock_id)
        return None

    if df.empty:
        log_error("warn: stock %s max-pub-date is empty, next", _stock_id)
        return None

    for row_index, row in df.iterrows():
        max_date = row['pub_date_time']

    if max_date is not None:
        log_info("max pub_date_time is %s", max_date)

    return max_date


def k_unit_one_stock(_stock_id, _db):
    log_info("k_unit_one_stock begin")

    # get max-date from table, as start date
    max_date = k_unit_get_max_date(_stock_id, _db)
    end_date = get_date_by(0)

    log_debug("[%s, %s]", max_date, end_date)

    # qfq
    if max_date is None:
        start_date = '2017-03-01'
        log_debug("it's first time: [%s]", _stock_id)
    else:
        start_date = str(max_date)
        log_debug("a old friend: [%s]", _stock_id)

    log_debug("[%s, %s]", start_date, end_date)

    # get from web(by tushare)
    begin = get_micro_second()

    try:
        df = ts.get_k_data(_stock_id, ktype='30', autype='qfq', start=start_date, end=end_date)
        # df = ts.get_h_data(_stock_id, autype='qfq', start=start_date, end=end_date, retry_count=5, pause=6)
        # df = ts.get_h_data(_stock_id, start='2016-08-20', end='2016-10-30')
        # df = ts.get_h_data(_stock_id, autype='qfq')
    except Exception:
        log_error("warn:error: %s get_k_data exception!", _stock_id)
        return -4

    # calc cost time
    log_info("get_k_data [%s] costs %d us", _stock_id, get_micro_second()-begin)

    if df is None :
        log_error("warn: stock %s is None, next", _stock_id)
        return -1

    if df.empty:
        log_error("warn: stock %s is empty, next", _stock_id)
        return -2

    df.sort_index(ascending=False, inplace=True)
    # df = df.sort_index(ascending=True)
    # df = df.reindex(index=range(0, len(df)))
    # log_debug("df: \n%s", df)

    begin = get_micro_second()

    k_unit_one_to_db(_stock_id, df, max_date, _db)

    log_info("one_to_db costs %d us", get_micro_second() - begin)

    log_info("function k_unit_one_stock end")

    return 


def work():
    db = db_init()

    # step1: get from web
    # stocks = get_stock_list_df_tu() # not real time 2017-5-31

    # stocks = get_stock_quotation() # bug only 100 rows 2017-6-7

    # 2017-9-6
    table = "tbl_day"
    stocks = get_stock_list_table_quick(table, db)


    # step2: to db
    begin = get_micro_second()

    # to db
    for row_index, row in stocks.iterrows():
        stock_id = row_index
        log_debug("stock: %s", stock_id)

        # import to DB
        k_unit_one_stock(stock_id, db)

    log_info("save-all costs %d us", get_micro_second()-begin)

    db_end(db)


#######################################################################

def main():
    sailog_set("k_unit.log")

    log_info("let's begin here!")

    if sai_is_product_mode():
        if today_is_weekend():
            log_info("today is weekend, exit")
        else:
            log_info("today is workday, come on")
            work()
    else:
        work()

    log_info("main ends, bye!")
    return

main()
exit()

#######################################################################


# k_unit.py
