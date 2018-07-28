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

def k_profit_to_db(_df, _db):

    dt = get_today()
    tm = get_time()


    # import dataframe to db
    for row_index, row in _df.iterrows():

        stock_id    = '%s' % (row.loc['code'])
        report_date = '%s' % (row.loc['report_date'])
        year        = row.loc['year']
        divi        = float(row.loc['divi'])
        shares      = int(row.loc['shares'])

        # 前复权
        sql = "insert into tbl_profit \
(stock_id, report_date, \
year, \
divi, shares, \
inst_date, inst_time) \
values ('%s', '%s', \
'%s', \
'%.3f', '%d', \
'%s', '%s')" % \
       (stock_id, report_date, 
        year,
        divi, shares, 
        dt, tm)

        # log_debug("%s", sql)
        rv = sql_to_db_nolog(sql, _db)
        if rv != 0:
            log_error("error: sql_to_db %s", sql)

        log_debug("%s -- %s: processed", report_date, stock_id);

    return 0



def k_profit(_db):

    begin = get_micro_second()

    top = 1000

    try:
        df = ts.profit_data(top=top)
    except Exception:
        log_error("warn:error: %s profit_data() exception!", top)
        return -4

    # calc cost time
    log_info("profit_data [%s] costs %d us", top, get_micro_second()-begin)

    if df is None :
        log_error("warn: df is None, next")
        return -1

    if df.empty:
        log_error("warn: df is empty, next")
        return -2

    if len(df) <= 1:
        log_error("warn: df is empty, next")
        return -3

    # pd.options.display.max_rows = 1000
    log_debug(df)
    begin = get_micro_second()

    k_profit_to_db(df, _db)

    log_info("to_db costs %d us", get_micro_second() - begin)

    return 



def work():
    db = db_init()

    k_profit(db)


    db_end(db)


#######################################################################

def main():
    sailog_set("kprofit.log")

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


# k_profit.py
