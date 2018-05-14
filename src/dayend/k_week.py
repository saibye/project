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


def k_week_one_to_db(_stock_id, _df, _start_date, _db):

    dt = get_today()
    tm = get_time()

    table_name = "tbl_week"

    # init last close price
    # last_close_price = _df['close'][0]
    last_close_price = _df.iloc[0,2]

    # import dataframe to db
    counter = 0
    volume  = 0
    open_price = -1
    for row_index, row in _df.iterrows():
        counter = counter + 1
        open_price = row.loc['open']
        volume     = row.loc['volume']

        # 前复权
        sql = "insert into tbl_week \
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
       (row.loc['date'], _stock_id,
        open_price, row.loc['high'], row.loc['close'], row.loc['low'],
        last_close_price,
        volume / 1000.00, 
        dt, tm)

        last_close_price = row.loc['close']

        # log_debug("%s", sql)
        rv = sql_to_db_nolog(sql, _db)
        if rv != 0:
            log_error("error: sql_to_db_week: %s", sql)
            return 0

    log_debug("%s: processed: %d", _stock_id, counter);

    return 0


def k_week_get_max_date(_stock_id, _db):
    df = get_max_pub_date_kweek(_stock_id, _db)

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


def k_week_one_stock(_stock_id, _db):
    log_info("k_week_one_stock begin")

    # clear week anyway
    sql = "delete from tbl_week where stock_id = '%s'" % (_stock_id)
    log_debug("clear week sql: [%s]", sql)
    rv = sql_to_db(sql, _db)

    # get max-date from table, as start date
    max_date = k_week_get_max_date(_stock_id, _db)
    end_date = get_date_by(0)

    log_debug("[%s, %s]", max_date, end_date)


    # qfq
    if max_date is None:
        start_date = '2010-01-01'
        log_debug("it's first time: [%s]", _stock_id)
    else:
        start_date = str(max_date)
        log_debug("a old friend: [%s]", _stock_id)

    log_debug("[%s, %s]", start_date, end_date)

    # get from web(by tushare)
    begin = get_micro_second()

    try:
        df = ts.get_k_data(_stock_id, ktype='W', autype='qfq', start=start_date, end=end_date)
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


    # df.sort_index(ascending=True, inplace=True)
    # df.sort_index(ascending=False, inplace=True)
    # df = df.sort_index(ascending=True)
    # df = df.reindex(index=range(0, len(df)))
    # log_debug("df: \n%s", df)

    begin = get_micro_second()

    k_week_one_to_db(_stock_id, df, max_date, _db)

    log_info("one_to_db costs %d us", get_micro_second() - begin)

    log_info("function k_week_one_stock end")

    return 


def work():
    db = db_init()

    # test mode
    """
    stock_id = "000725"
    k_week_one_stock(stock_id, db)
    return 0
    """

    # stocks = get_stock_quotation()
    stocks = get_stock_list_table('tbl_day', db)

    # step2: to db
    begin = get_micro_second()

    # to db
    for row_index, row in stocks.iterrows():
        stock_id = row_index
        log_debug("stock: %s", stock_id)

        # stock_id = "002458"
        # stock_id = "000025"
        # stock_id = "002591"
        # stock_id = "000725"

        # import to DB
        k_week_one_stock(stock_id, db)
        # break

    log_info("save-all costs %d us", get_micro_second()-begin)

    db_end(db)


#######################################################################

def main():
    sailog_set("k_week.log")

    log_info("let's begin here!")

    if sai_is_product_mode():
        if today_is_weekend():
            log_info("today is weekend, exit")
            work()
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

# k_week.py
