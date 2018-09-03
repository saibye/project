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

def j_fund_to_db(_df, _db):

    dt = get_today()
    tm = get_time()


    # import dataframe to db
    for row_index, row in _df.iterrows():

        stock_id    = '%s' % (row.loc['code'])
        stock_name  = '%s' % (row.loc['name'])
        report_date = '%s' % (row.loc['date'])
        nums        = int(row.loc['nums'])
        nlast       = int(row.loc['nlast'])
        count       = float(row.loc['count'])
        clast       = float(row.loc['clast'])
        amount      = float(row.loc['amount'])
        ratio       = float(row.loc['ratio'])

        # 前复权
        sql = "insert into tbl_fund \
(stock_id, stock_name, report_date, \
inst_num, inst_changed, \
hold_volume, volume_changed, \
hold_amount, hold_ratio, \
inst_date, inst_time) \
values ('%s', '%s', '%s', \
'%d', '%d', \
'%.3f', '%.3f', \
'%.3f', '%.3f', \
'%s', '%s')" % \
       (stock_id, stock_name, report_date, 
        nums, nlast,
        count, clast,
        amount, ratio, 
        dt, tm)

        # log_debug("%s", sql)
        rv = sql_to_db_nolog(sql, _db)
        if rv != 0:
            log_error("error: sql_to_db %s", sql)

        # log_debug("%s -- %s: processed", report_date, stock_id);

    return 0



def j_fund(_year, _quarter, _db):

    begin = get_micro_second()

    log_debug('year: %d, quarter: %d', _year, _quarter)

    try:
        df = ts.fund_holdings(_year, _quarter)
    except Exception:
        log_error("warn:error: %s/%s fund() exception!", _year, _quarter)
        return -4

    # calc cost time
    log_info("fund [%s, %s] costs %d us", _year, _quarter, get_micro_second()-begin)

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

    j_fund_to_db(df, _db)

    log_info("to_db costs %d us", get_micro_second() - begin)

    return 



def work():
    db = db_init()

    quarte = 0
    year = int(get_year())

    for i in range(4):
        quarter = i + 1

        j_fund(year-1, quarter, db)
        j_fund(year,   quarter, db)


    db_end(db)


#######################################################################

def main():
    sailog_set("jfund.log")

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


# j_fund.py
