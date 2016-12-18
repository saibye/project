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


def get_insert_xsg_sql(_row):
    stock_id        = _row['code']
    name            = _row['name']
    free_date       = _row['date']
    free_count      = _row['count']
    ratio           = _row['ratio']

    dt = get_today()
    tm = get_time()

    sql = "insert into tbl_xsg (stock_id, free_date, free_count, ratio, inst_date, inst_time) \
values ( '%s', '%s', '%s', '%s', '%s', '%s');" % \
       (stock_id, free_date, free_count, ratio, dt, tm)

    return sql


def one_month(_year, _month, _db):
    df = ts.xsg_data(_year, _month)

    rownum = 0
    for row_index, row in df.iterrows():
        rownum   = rownum + 1
        sql = get_insert_xsg_sql(row)
        # log_debug("sql: %s", sql)
        sql_to_db(sql, _db)

def one_year(_year, _db):
    for mon in range(1, 13):
        log_debug("month: --%d--", mon)
        one_month(_year, str(mon), _db)


def work(_args):
    db = db_init()

    one_year("2016", db)
    one_year("2017", db)
    one_year("2018", db)

    # get_xsg_info("000413", db)

    db_end(db)

#######################################################################

def main():
    sailog_set("get_xsg.log")

    log_info("main begins")

    args = get_args()

    work(args)

    log_info("main ends, bye!")
    return

main()
exit()

#######################################################################

# get_xsg.py
