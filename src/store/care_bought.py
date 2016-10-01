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
from ct_ticks import work_one_stock

#######################################################################


def work(_args):
    days = 7
    db = db_init()

    dt = get_today()
    tm = get_time()

    sql = "select distinct stock_id from tbl_real_trade where is_valid='1' and TO_DAYS(NOW())-TO_DAYS(buy_date) < %d" % days
    log_info("%s", sql)

    df = pd.read_sql_query(sql, db);
    log_info("df:\n%s", df)

    df = df.set_index('stock_id')

    for row_index, row in df.iterrows():
        stock_id = row_index
        log_debug("---stock is %s",  stock_id)
        start_date = get_date_by(0-days)
        log_debug("watch: %s, %s, %s", stock_id, start_date, days)
        work_one_stock(stock_id, start_date, days+1, db)

    db_end(db)


#######################################################################

def main():
    sailog_set("care_bought.log")

    log_info("main begins")

    saimail_init()

    args = get_args()

    work(args)

    log_info("main ends, bye!")
    return

main()
exit()

#######################################################################

# care_bought.py
