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


def work_one_more(_stock_list, _db):
    print "work_one_more begin %s" % _stock_list

    df = ts.get_realtime_quotes(_stock_list)
    if df is None :
        print "stock %s no data, next" % _stock_list
        return

    print df

    # DO NOT clear previous data

    # import dataframe to db
    #df_to_db(_stock_list, df, _db)

    print "work_one_more end"

    return 

def import_real(_stocks, _db):

    list1 = []
    for row_index, row in _stocks.iterrows():
        print "---index is ",  row_index
        list1.append(row_index)
        if len(list1) == 30:
            print list1
            work_one_more(list1, _db)
            list1 = []
            print list1
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
    print "let's begin here!"

    work()

    print "main ends, bye!"
    return

main()
exit()
print "can't arrive here"

#######################################################################


# import_real.py
