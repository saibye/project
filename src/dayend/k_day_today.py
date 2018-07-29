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


# ts.get_today_all()


#######################################################################

def k_today_to_db(_date, _df, _db):

    dt = get_today()
    tm = get_time()

    pub_date = _date

    # import dataframe to db
    for row_index, row in _df.iterrows():

        stock_id    = '%s' % (row_index)
        stock_name  = '%s' % (row.loc['name'])

        open_price  = float(row.loc['open'])
        close_price = float(row.loc['trade'])
        high_price  = float(row.loc['high'])
        low_price   = float(row.loc['low'])
        last_close  = float(row.loc['settlement'])

        changepercent   = float(row.loc['changepercent'])

        volume      = float(row.loc['volume'])
        turnoverratio   = float(row.loc['turnoverratio'])
        amount      = float(row.loc['amount'])
        per         = float(row.loc['per'])
        pb          = float(row.loc['pb'])
        mktcap      = float(row.loc['mktcap'])
        nmc         = float(row.loc['nmc'])

        # 
        sql = "insert into tbl_day_today \
(pub_date, stock_id, stock_loc, \
open_price, high_price, close_price, low_price, \
last_close_price, changepercent, \
deal_total_count, deal_total_amount, \
turnoverratio, per, pb, mktcap, nmc, \
inst_date, inst_time) \
values ('%s', '%s', '%s', \
'%.3f', '%.3f', '%.3f', '%.3f', \
'%.3f', '%.3f', \
'%.3f', '%.3f', \
'%.3f', '%.3f', '%.3f', '%.3f', '%.3f', \
'%s', '%s')" % \
       (pub_date, stock_id, 'cn',
        open_price, high_price, close_price, low_price,
        last_close,  changepercent,
        volume, amount, 
        turnoverratio, per, pb, mktcap, nmc,
        dt, tm)

        # log_debug("%s", sql)
        rv = sql_to_db_nolog(sql, _db)
        if rv != 0:
            log_error("error: sql_to_db %s", sql)

        # log_debug("%s -- %s: processed", report_date, stock_id);

    return 0



def k_today(_db):

    begin = get_micro_second()

    pub_date = get_last_workday()
    log_debug('pub_date: %s -- %s', pub_date, type(pub_date))

    try:
        df = get_stock_quotation()
    except Exception:
        log_error("warn:error: get_stock_quotation() exception!")
        return -4

    # calc cost time
    log_info("get_stock_quotation costs %d us", get_micro_second()-begin)

    if df is None :
        log_error("warn: df is None, next")
        return -1

    if df.empty:
        log_error("warn: df is empty, next")
        return -2

    if len(df) <= 1:
        log_error("warn: df is empty, next")
        return -3

    pd.options.display.max_rows = 1000
    log_debug(df)

    begin = get_micro_second()

    k_today_to_db(pub_date, df, _db)

    log_info("to_db costs %d us", get_micro_second() - begin)

    return 



def work():
    db = db_init()

    k_today(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("k_today.log")

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


# k_today.py
