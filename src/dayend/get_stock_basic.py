#!/usr/bin/env python
# -*- encoding: utf8 -*-

import tushare as ts
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

from saiutil import *
from saidb   import *
from saisql  import *
from saicalc import *
from sailog  import *
from saimail import *

#######################################################################


def get_insert_basic_sql(_stock_id, _row):
    stock_id        = _stock_id
    name            = _row['name']
    industry        = _row['industry']
    area            = _row['area']
    pe              = _row['pe']
    outstanding     = _row['outstanding']
    totals          = _row['totals']
    totalAssets     = _row['totalAssets']
    liquidAssets    = _row['liquidAssets']
    fixedAssets     = _row['fixedAssets']
    reserved        = _row['reserved']
    reservedPerShare= _row['reservedPerShare']
    eps             = _row['esp']
    bvps            = _row['bvps']
    pb              = _row['pb']
    timeToMarket    = _row['timeToMarket']

    dt = get_today()
    tm = get_time()

    sql = "insert into tbl_basic (stock_id, stock_name, industry, area, \
pe, outstanding, totals, total_assets, liquid_assets, \
fixed_assets, reserved, reserved_per, \
eps, bvps, pb, time_to_market, inst_date, inst_time) \
values ( '%s', '%s', '%s', '%s', \
'%s', '%s', '%s', '%s', '%s', \
'%s', '%s', '%s', \
'%s', '%s', '%s', '%s', '%s', '%s');" %\
       (stock_id, 'name', 'industry', 'area',
        pe, outstanding, totals, totalAssets, liquidAssets, 
        fixedAssets, reserved, reservedPerShare, 
        eps, bvps, pb, timeToMarket, dt, tm)

    return sql


def work(_args):
    db = db_init()

    dt = get_today()
    tm = get_time()

    df = ts.get_stock_basics()

    # se = pd.Series(dt, df.index)

    rownum = 0
    for row_index, row in df.iterrows():
        rownum = rownum + 1
        code= row_index
        sql = get_insert_basic_sql(code, row)
        # log_debug("sql: %s", sql)
        sql_to_db(sql, db)

    db_end(db)


#######################################################################

def main():
    sailog_set("get_stock_basic.log")

    log_info("main begins")

    saimail_init()

    args = get_args()

    work(args)

    log_info("main ends, bye!")
    return

main()
exit()

#######################################################################

# get_stock_basic.py
