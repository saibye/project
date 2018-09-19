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

def k_no_fuquan_one_to_db(_stock_id, _df, _db):

    dt = get_today()
    tm = get_time()


    # import dataframe to db
    counter = 0
    last_row    = None
    last_date   = ''
    last_close_price = 0.0
    for row_index, row in _df.iterrows():
        counter = counter + 1

        # pub_date = '%s' % (row.loc['date']) # api for  get-k-data
        pub_date = '%s' % (row_index) # api for  h-data

        if last_row is not None:
            last_close_price = row.loc['close']

            # 前复权
            sql = "insert into tbl_day_no_fuquan \
(pub_date, stock_id, \
open_price, high_price, close_price, low_price, \
last_close_price, \
deal_total_count, \
inst_date, inst_time) \
values ('%s', '%s', \
'%.2f', '%.2f', '%.2f', '%.2f', \
'%.2f', \
'%.3f', \
'%s', '%s')" % \
           (last_date, _stock_id,
            last_row.loc['open'], last_row.loc['high'], last_row.loc['close'], last_row.loc['low'],
            last_close_price,
            last_row.loc['volume'] / 1000.00, 
            dt, tm)

            begin = get_micro_second()

            log_debug("%s", sql)
            rv = sql_to_db_nolog(sql, _db)
            if rv != 0:
                log_error("error: sql_to_db %s", sql)
                return 1

            log_info("insert costs %d us", get_micro_second()-begin)

        last_row  = row
        last_date = pub_date

    log_debug("%s: processed: %d", _stock_id, counter);

    return 0



def k_no_fuquan_one_stock(_stock_id, _db):
    # log_info("k_no_fuquan_one_stock begin")


    # get from web(by tushare)
    begin = get_micro_second()

    try:
        df = ts.get_hist_data(_stock_id)
    except Exception:
        log_error("warn:error: %s get_k_data exception!", _stock_id)
        return -4

    # calc cost time
    log_info("get_data [%s] costs %d us", _stock_id, get_micro_second()-begin)

    if df is None :
        log_error("warn: stock %s is None, next", _stock_id)
        return -1

    if df.empty:
        log_error("warn: stock %s is empty, next", _stock_id)
        return -2

    # df.sort_index(ascending=True, inplace=True)

    begin = get_micro_second()

    k_no_fuquan_one_to_db(_stock_id, df, _db)

    log_info("one_to_db costs %d us", get_micro_second() - begin)

    # log_info("function k_no_fuquan_one_stock end")

    return 



def work():
    db = db_init()

    """
    stock_id = '000002'
    k_no_fuquan_one_stock(stock_id, db)
    return 0
    """

    # max-much
    # stocks = get_stock_quotation() # bug only 100 rows 2017-6-7 -- fixed by upgrade 2017-7-5

    # much
    # step1: get from web
    # stocks = get_stock_list_df_tu() # not real time 2017-5-31

    # TODO: TMP 2017-6-7
    # table = "tbl_day"
    # stocks = get_stock_list_table(table, db)


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
        k_no_fuquan_one_stock(stock_id, db)

    log_info("save-all costs %d us", get_micro_second()-begin)


    db_end(db)


#######################################################################

def main():
    sailog_set("k_nofuquan.log")

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

# k_no_fuquan.py
