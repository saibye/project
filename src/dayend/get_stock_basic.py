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
from saitu   import *

#######################################################################

def get_delete_basic_sql(_stock_id):
    sql = "delete from tbl_basic where stock_id='%s'" % (_stock_id)
    return sql

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
       (stock_id, name, industry, area,
        pe, outstanding, totals, totalAssets, liquidAssets, 
        fixedAssets, reserved, reservedPerShare, 
        eps, bvps, pb, timeToMarket, dt, tm)

    return sql


def work(_args):
    db = db_init()

    df = get_stock_list_df_tu()
    log_debug("\n%s", df)

    rownum = 0
    for row_index, row in df.iterrows():
        rownum = rownum + 1
        stock_id = row_index
        sql = get_delete_basic_sql(stock_id)
        sql_to_db(sql, db)
        sql = get_insert_basic_sql(stock_id, row)
        rv = sql_to_db(sql, db)
        log_info("%s done: %d", stock_id, rv)

    db_end(db)


#######################################################################

def main():
    sailog_set("get_stock_basic.log")

    log_info("main begins")

    args = get_args()

    work(args)

    log_info("main ends, bye!")
    return

main()
exit()

#######################################################################

# get_stock_basic.py
