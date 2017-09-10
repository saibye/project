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


def k_15min_one_to_db(_stock_id, _df, _db):

    dt = get_today()
    tm = get_time()

    table_name = "tbl_15min"

    # init last close price
    # last_close_price = _df['close'][0]

    length = len(_df)

    # import dataframe to db
    counter = 0
    volume  = 0
    open_volume = 0
    open_price = -1
    for row_index, row in _df.iterrows():
        counter = counter + 1
        trade_date_time = row.loc['date']
        open_price = row.loc['open']
        volume = row.loc['volume']

        if counter >= length:
            last_close_price = _df.iloc[counter-1,2]
            log_debug("end-time: %.2f", last_close_price)
        else:
            last_close_price = _df.iloc[counter,2]
            # log_debug("last-clo: %.2f", last_close_price)


        # 前复权
        sql = "insert into tbl_15min \
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
        volume, 
        dt, tm)

        # last_close_price = row.loc['close']

        # log_debug("%s", sql)
        rv = sql_to_db_nolog(sql, _db)
        if rv != 0:
            log_error("error: sql_to_db15: %s", sql)
            return 0

    log_debug("%s: processed: %d rows", _stock_id, counter);

    return 0



def k_15min_one_stock(_stock_id, _db):
    # log_info("k_15min_one_stock begin")


    # get from web(by tushare)
    begin = get_micro_second()

    try:
        df = ts.get_k_data(_stock_id, ktype='15', autype='qfq')
    except Exception:
        log_error("warn:error: %s get_k_data exception!", _stock_id)
        return -4

    # calc cost time
    log_info("get_k_data [%s] costs %d ms", _stock_id, (get_micro_second()-begin)/1000)

    if df is None :
        log_error("warn: stock %s is None, next", _stock_id)
        return -1

    if df.empty:
        log_error("warn: stock %s is empty, next", _stock_id)
        return -2

    df.sort_index(ascending=False, inplace=True)

    begin = get_micro_second()

    k_15min_one_to_db(_stock_id, df, _db)

    log_info("one_to_db costs %d ms", (get_micro_second() - begin)/1000)

    # log_info("function k_15min_one_stock end")

    return 


def work():
    db = db_init()

    # step1: get from web
    # stocks = get_stock_list_df_tu() # not real time 2017-5-31

    # stocks = get_stock_quotation() # slow and no need

    table = "tbl_day"
    stocks = get_stock_list_table_quick(table, db)
    log_debug("recent list:\n%s", stocks)

    # step2: to db
    begin = get_micro_second()

    """
    # TEST mode
    stock_id = "000002"
    stock_id = "000717"
    k_15min_one_stock(stock_id, db)
    return 0
    """

    # to db
    for row_index, row in stocks.iterrows():
        stock_id = row_index
        log_debug(">>>stock: %s>>>>>>>>>>>>>>>>>>>>>>>>>>>", stock_id)

        # import to DB
        k_15min_one_stock(stock_id, db)

    log_info("save-all costs %d seconds", (get_micro_second()-begin)/1000000)

    db_end(db)


#######################################################################

def main():
    sailog_set("k_15min.log")

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

#######################################################################


# k_15min.py
