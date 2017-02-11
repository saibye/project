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
from saimail import *

#######################################################################


def work(_args):
    db = db_init()

    # step2: insert to db
    stock_id = _args[0]

    dt = get_today()
    tm = get_time()


    # delete first
    sql = "delete from tbl_real_trade where stock_id='%s'" % (stock_id)
    sql_to_db_nolog(sql, db)

    # insert then
    sql = "insert into tbl_real_trade \
(buy_date, stock_id, stock_loc,  holder, \
buy_price, sell_price, \
changed, sell_date, is_valid, buy_reason, \
inst_date, inst_time) \
values ('%s', '%s', '%s', '%s',  \
'%s', '%s', \
'%s', '%s', '%s', '%s', \
'%s', '%s')" % \
    (dt, stock_id, 'cn', 'sai',
     '0.00', '0.00',
     '0.00', '2000-01-01',
     '1', 'want',
     dt, tm)
    log_info("%s", sql)

    sql_to_db_nolog(sql, db)

    db_end(db)


#######################################################################

def main():
    sailog_set("add_bought.log")

    log_info("main begins")

    saimail_init()

    args = get_args()

    if len(args) == 0:
        log_info("error: invalid usage")
        log_info("add stock_id")
        print "error: invalid usage"
        print "add stock_id"
        return -1

    work(args)

    log_info("main ends, bye!")
    return

main()
exit()

#######################################################################

# add_bought.py
