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

#######################################################################


def work_one_once(_stock_id, _db):
    print "work_one_once begin %s" % _stock_id

    # full data
    minute = '30'
    df = ts.get_hist_data(_stock_id, ktype=minute)
    if df is None :
        print "stock %s no data, next" % _stock_id
        return

    #print df

    # clear previous data
    clear_stock_from_db(_stock_id, _db)

    # import dataframe to db
    df_to_db(_stock_id, df, _db)

    print "work_one_once end"

    return 

def import_once(_stocks, _db):

    for row_index, row in _stocks.iterrows():
        print "---index is ",  row_index
        work_one_once(row_index, _db)

    return


def work():
    db = db_init()

    # step1: get from web
    #stocks = get_stock_list_df_tu()

    # step2: insert to db
    #import_once(stocks, db)


    # step3:
    # TODO: 复权数据 rehabilitation

    db_end(db)


#######################################################################

def main():
    print "let's begin here!"

    #work()

    print "main ends, bye!"
    return

main()
exit()
print "can't arrive here"

#######################################################################


# import_once.py
