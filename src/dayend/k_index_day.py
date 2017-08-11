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

def k_index_day_one_to_db(_stock_id, _df, _start_date, _db):

    dt = get_today()
    tm = get_time()

    # assume data [1: 100]
    # 1: compare whether to fuquan
    # [1:100] to db

    if _start_date is not None:

        # 1. compare
        # new_close_price = _df['close'][0]
        new_close_price = _df.iloc[0,2]

        # the close price of max-pub-date
        tbl_df = get_one_kday(_stock_id, _start_date, _db)
        tbl_close_price = tbl_df['close_price'][0]

        log_debug("close: web[%s] : [%s]table", new_close_price, tbl_close_price)
        # compare, update if not equal
        rate = new_close_price / tbl_close_price
        if rate == 1.0:
            log_debug("[%s, %s] no need to fuquan", new_close_price, tbl_close_price)
        else:
            log_debug("warn! fuquan, rate: %.3f", rate)
            sql = "update tbl_index_day set open_price = round(open_price * %.3f, 2), \
close_price = round(close_price * %.3f, 2), \
low_price   = round(low_price * %.3f,   2), \
high_price  = round(high_price * %.3f,  2), \
last_close_price = round(last_close_price * %.3f, 2), \
deal_total_count = round(deal_total_count / %.3f, 0) \
where stock_id = '%s' \
and pub_date <= '%s'" % \
                   (rate, rate, rate, rate, rate, rate, \
                    _stock_id, _start_date)
            rv = sql_to_db(sql, _db)
            if rv != 0:
                log_error("error: sql_to_db %s", sql)
                return -1



    # init last close price
    # last_close_price = _df['close'][0]
    last_close_price = _df.iloc[0,2]

    # import dataframe to db
    counter = 0
    for row_index, row in _df.iterrows():
        counter = counter + 1

        # 前复权
        sql = "insert into tbl_index_day \
(pub_date, stock_id, stock_loc, \
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
        row.loc['open'], row.loc['high'], row.loc['close'], row.loc['low'],
        last_close_price,
        row.loc['volume'] / 1000.00, 
        dt, tm)

        last_close_price = row.loc['close']

        # log_debug("%s", sql)
        rv = sql_to_db_nolog(sql, _db)
        if rv != 0:
            log_error("error: sql_to_db %s", sql)

    log_debug("%s: processed: %d", _stock_id, counter);

    return 0



def k_index_day_get_max_date(_stock_id, _db):
    sql = "select max(pub_date) pub_date from tbl_index_day where stock_id='%s'" % _stock_id

    df = pd.read_sql_query(sql, _db);

    if df is None :
        log_error("warn: stock %s max-pub-date is None, next", _stock_id)
        return None

    if df.empty:
        log_error("warn: stock %s max-pub-date is empty, next", _stock_id)
        return None

    for row_index, row in df.iterrows():
        max_date = row['pub_date']

    if max_date is not None:
        log_info("max pub_date is %s", max_date)

    return max_date


def k_index_day_one_stock(_stock_id, _db):
    log_info("k_index_day_one_stock begin")

    # get max-date from table, as start date
    max_date = k_index_day_get_max_date(_stock_id, _db)
    end_date = get_date_by(0)

    log_debug("[%s, %s]", max_date, end_date)

    #
    if max_date is None:
        start_date = '2016-01-01'
        log_debug("it's first time: [%s]", _stock_id)
    else:
        start_date = str(max_date)
        log_debug("a old friend: [%s]", _stock_id)

    log_debug("[%s, %s]", start_date, end_date)

    # get from web(by tushare)
    begin = get_micro_second()

    try:
        df = ts.get_k_data(_stock_id, index=True, start=start_date, end=end_date)
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

    df.sort_index(ascending=True, inplace=True)
    # df = df.sort_index(ascending=True)
    # df = df.reindex(index=range(0, len(df)))
    # log_debug("df: \n%s", df)

    begin = get_micro_second()

    k_index_day_one_to_db(_stock_id, df, max_date, _db)

    log_info("one_to_db costs %d us", get_micro_second() - begin)

    log_info("function k_index_day_one_stock end")

    return 



def work():
    db = db_init()

    """
    stock_id = "601899"
    log_debug("stock: %s", stock_id)
    k_index_day_one_stock(stock_id, db)
    """

    # step1: get from web
    stocks = ts.get_index()

    # step2: to db
    begin = get_micro_second()

    # to db
    for row_index, row in stocks.iterrows():
        stock_id = row['code']
        log_debug("stock: %s", stock_id)

        # import to DB
        k_index_day_one_stock(stock_id, db)

    log_info("save-all costs %d us", get_micro_second()-begin)

    db_end(db)


#######################################################################

def main():
    sailog_set("k_index_day.log")

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


# k_index_day.py
