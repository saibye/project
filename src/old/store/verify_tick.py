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
from sairank import *
from saitick import *


"""
buy策略：
"""
#######################################################################


def ticks_analyze(_stock_id, _trade_date):
    df = get_tick(_stock_id, _trade_date)
    if df is None:
        log_debug("%s get tick failure", _stock_id)
        return -1

    log_debug("\n%s", df.tail(20))

    base_list = [1, 200, 400, 800, 1000, 2000, 3000]

    rank = 0.0

    open_price  = df['price'][0]
    close_price = df['price'][-1]

    # with price
    factor = close_price / 10.0

    content = "%s: %s: [%s, %s]\n" % (_stock_id, _trade_date, open_price, close_price)

    for base in base_list :
        buy, sell = get_buy_sell_sum(df, base)

        diff  = buy - sell
        diff2 = diff * factor
        content += "%04d B: %.2f, S: %.2f, N: %.2f, %.2f\n" % \
                    (base, buy/10000.00, sell/10000.00, diff/10000.00, diff2/10000.00)

    log_info("\n%s", content)

    return 0



"""
usage: 
python ct_ticks.py 
python ct_ticks.py some-day
python ct_ticks.py some-day days stockid
"""
def work(_args):
    db = db_init()

    global g_sina_mode
    # log_debug("input3: %s, %s, %s", start_date, days, stock_id)

    stock_id   = "600112"
    start_date = "2016-11-18"

    log_debug("%s - %s", stock_id, start_date);

    tick_set_sina_mode()
    rv = ticks_analyze(stock_id, start_date)

    tick_set_feng_mode()
    rv = ticks_analyze(stock_id, start_date)

    db_end(db)


#######################################################################

def main():
    sailog_set("verify_ticks.log")

    log_info("main begins")

    saimail_init()

    args = get_args()

    work(args)

    log_info("main ends, bye!")
    return

if __name__ == "__main__":
    main()
    exit()

#######################################################################

# verify_ticks.py
