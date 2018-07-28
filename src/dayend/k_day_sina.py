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

def k_day_sina_one_to_db(_stock_id, _df, _db):

    dt = get_today()
    tm = get_time()


    # import dataframe to db
    for row_index, row in _df.iterrows():

        pub_date    = '%s' % (row.loc['date'])
        close_price = float(row.loc['price'])
        open_price  = float(row.loc['open'])
        low_price   = float(row.loc['low'])
        high_price  = float(row.loc['high'])
        pre_close   = float(row.loc['pre_close'])
        volume   = float(row.loc['volume'])
        amount   = float(row.loc['amount'])

        # 前复权
        sql = "insert into tbl_day_sina \
(pub_date, stock_id, stock_loc, \
open_price, high_price, close_price, low_price, last_close_price, \
deal_total_count, deal_total_amount, \
inst_date, inst_time) \
values ('%s', '%s', '%s',  \
'%.2f', '%.2f', '%.2f', '%.2f', '%.2f', \
'%.3f', '%.3f', \
'%s', '%s')" % \
       (pub_date, _stock_id, 'cn', 
        open_price, high_price, close_price, low_price, pre_close,
        volume / 1000.00, amount / 1000.00, 
        dt, tm)

        # log_debug("%s", sql)
        rv = sql_to_db_nolog(sql, _db)
        if rv != 0:
            log_error("error: sql_to_db %s", sql)

    log_debug("%s -- %s: processed", pub_date, _stock_id);

    return 0



def k_day_sina_one_stock(_stock_id, _db):

    # get from web(by tushare)
    begin = get_micro_second()

    try:
        df = ts.get_realtime_quotes(_stock_id)
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

    begin = get_micro_second()

    k_day_sina_one_to_db(_stock_id, df,_db)

    log_info("one_to_db costs %d us", get_micro_second() - begin)

    return 



def work():
    db = db_init()

    """
    stock_id = "000002"
    log_debug("stock: %s", stock_id)
    k_day_sina_one_stock(stock_id, db)
    return 0
    """


    # 2018-6-1
    stocks = get_stock_quotation()
    if stocks is None:
        log_error('error: warn:  get_stock_quotation failure')
        stocks = get_stock_list_df_tu()
        if stocks is None:
            log_error('error: warn:  get_stock_list_df_tu failure')
            stocks = get_stock_list_table('tbl_day', db)
            log_info('3: stock list used from table: %d', len(stocks))
        else:
            log_info('2: stock list used from get_stock_list_df_tu -- get_stock_basics')
    else:
        log_info('1: stock list used from get_stock_quotation -- get_today_all')


    log_info('stock list length: %d', len(stocks))

    # step2: to db
    begin = get_micro_second()

    # to db
    for row_index, row in stocks.iterrows():
        stock_id = row_index
        log_debug("stock: %s", stock_id)


        # import to DB
        k_day_sina_one_stock(stock_id, db)

    log_info("save-all costs %d us", get_micro_second()-begin)


    db_end(db)


#######################################################################

def main():
    sailog_set("kday_sina.log")

    log_info("let's begin here!")

    if sai_is_product_mode():
        if today_is_weekend():
            log_info("today is weekend, exit")
            # work()
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


# k_day_sina.py
