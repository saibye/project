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

def k_top_one(_stock_id, _row, _db):
    dt = get_today()
    tm = get_time()

    # 前复权
    sql = "insert into tbl_top_list \
(pub_date, stock_id, stock_loc, stock_name, \
pchange, amount, \
buy, bratio, sell, sratio, \
reason, \
inst_date, inst_time) \
values ('%s', '%s', '%s', '%s', \
'%s', '%s', '%s', '%s', '%s', '%s', \
'%s',  '%s', '%s')" % (_row['date'], _stock_id, 'cn', _row['name'], 
    _row['pchange'], _row['amount'], 
    _row['buy'],  _row['bratio'], 
    _row['sell'], _row['sratio'], _row['reason'], dt, tm)

    # log_debug("%s", sql)

    rv = sql_to_db(sql, _db)
    if rv != 0:
        log_error("error: sql_to_db %s", sql)

    log_debug("record '%s' succeeds", _stock_id)

    return 0

#
def work_all():
    trade_date = get_today()

    i   = 0
    cnt = 500
    while i < cnt:
        trade_date = get_date_by(0-i)
        log_debug("%d -- %s", i, trade_date)
        arg_list = [trade_date]
        work(arg_list)

        i = i + 1


def work(_args):
    db = db_init()

    if len(_args) > 0:
        trade_date = _args[0]
        log_info("date passed: %s", trade_date)
    else:
        trade_date = "2017-02-24"
        trade_date = get_today()

    log_info("trade_date: %s", trade_date)

    # step1: get from web
    # 2017-02-24
    stocks = get_top_list_tu(trade_date)
    if stocks is None:
        log_error("No data found: '%s'", trade_date)
        return -1

    log_debug("\n%s", stocks)
    # step2: to db
    begin = get_micro_second()

    # to db
    for row_index, row in stocks.iterrows():
        stock_id = row['code']
        log_debug("stock: %s", stock_id)

        k_top_one(stock_id, row, db)

    log_info("save-all costs %d us", get_micro_second()-begin)


    db_end(db)


#######################################################################

def main():
    sailog_set("k_top.log")

    log_info("let's begin here!")

    args = get_args()

    if today_is_weekend():
        log_info("today is weekend, exit")
    else:
        log_info("today is workday, come on")
        work(args)

    """
    work_all()
    work(args)
    """

    log_info("main ends, bye!")
    return

main()
exit()
print "can't arrive here"

#######################################################################

# k_top.py
