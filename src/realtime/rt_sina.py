#!/usr/bin/env python
# -*- encoding: utf8 -*-

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


def work_one_more(_stock_list, _db):
    log_info("work_one_more begin: \n%s", _stock_list)

    begin = get_micro_second()

    df = ts.get_realtime_quotes(_stock_list)
    if df is None :
        log_error("stock %s no data, next", _stock_list)
        return

    diff = get_micro_second() - begin;
    log_debug("tu costs %d us", diff)

    log_debug("df: \n%s", df)

    # TODO anaylize realtime data
    #analyze_sina_df(df, _db)

    log_info("work_one_more end")

    return 

def import_real(_stocks, _db):

    list1 = []
    group = 100
    for row_index, row in _stocks.iterrows():
        #log_debug("---index is %s", row_index)
        list1.append(row_index)
        if len(list1) == group:
            work_one_more(list1, _db)
            break

    return


def work():
    db = db_init()

    # step1: get from web
    stocks = get_stock_list_df_tu()

    # step2: insert to db
    import_real(stocks, db)

    # test data
    #stock_id = '300028'
    #work_one_more(stock_id, db)

    # step3:
    # TODO: 复权数据 rehabilitation

    db_end(db)


#######################################################################

def main():
    sailog_set("rt_sina.log")

    log_info("let's begin here!")

    work()

    log_info("main ends, bye!")
    return

main()
exit()
print "can't arrive here"

#######################################################################


# rt_sina.py
