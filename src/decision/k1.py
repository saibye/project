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
from sairef  import *

#######################################################################

"""
def check_chance(_stocks, _db):
    for row_index, row in _stocks.iterrows():
        stock_id = row_index
        info_row = basic_info.loc[stock_id, :]
        log_debug("--------------------------------------------")
    return
"""


def citou():
    rate1 = (ref_close(1) - ref_close(2)) / ref_close(2) * 100
    rate2 = (ref_close(0) - ref_close(1)) / ref_close(1) * 100
    mid   = (ref_open(1)  + ref_close(1)) / 2
    """
    log_debug("rate1: %.2f", rate1)
    log_debug("rate2: %.2f", rate2)
    log_debug("mid:   %.2f", mid)
    log_debug("low:   %.2f", ref_low(1))
    log_debug("close: %.2f", ref_close(0))
    log_debug("open:  %.2f", ref_open(0))
    """

    # if rate1 <= -5 and rate2 >= 5 and ref_open(0) < ref_low(1) and ref_close(0) > mid: # 2016-11-20
    if rate1 <= -5 and rate2 >= 4 and ref_open(0) <= ref_close(1) and ref_close(0) >= mid:
        rv = 1
        # log_debug("nice: citou")
    else:
        rv = 0
        # log_debug("not match")

    return rv

def work_one(_trade_date, _db):
    ref_set_date(_trade_date)

    rv = ref_init(_db)
    if rv != 0:
        log_error("error: ref_init")
        return rv

    begin = get_micro_second()

    stocks = ref_get_list()
    rownum = 0
    content = ""
    for s_index, s_val in stocks.iteritems():
        rownum = rownum + 1
        stock_id = s_index
        log_debug("%s-%s", stock_id, _trade_date)
        rv = ref_set(stock_id)
        if rv < 0:
            log_error("error: ref_set: %s", stock_id)
            return rv
        elif rv < 3:
            log_error("warn: small %d", rv)
            continue

        rv = citou()
        if rv == 1:
            one = "%s -- %s\n" % (_trade_date, stock_id)
            log_info("nice: %s", one)
            content += one
        else:
            # log_debug("wait...")
            pass

    log_info("%d costs %d us", rownum, get_micro_second() - begin)

    subject = "citou: %s" % (_trade_date)
    if len(content) > 0:
        log_debug(subject)
        log_debug("\n%s", content)
        # saimail(subject,  content)

    """
    stock_id = "000002"

    rv = ref_set(stock_id)
    if rv != 0:
        log_error("error: ref_set")
        return rv
    """

def regression(_db):

    max_date = "2016-11-21"
    days = 3

    date_df = get_recent_pub_date(max_date, days, _db)
    if date_df is None:
        log_error("error: get_recent_pub_date failure")
        return -1
    else:
        date_df.set_index("pub_date", inplace=True)

    for row_index, row in date_df.iterrows():
        trade_date = row_index
        log_debug("[%s]------------------", trade_date)
        work_one(trade_date, _db)

    return 0


def work():
    db = db_init()

    """
    trade_date = "2016-08-02"
    work_one(trade_date, db)
    """

    regression(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("k1.log")

    log_info("let's begin here!")

    """
    # check holiday
    if today_is_weekend():
        log_info("today is weekend, exit")
    else:
        log_info("today is workday, come on")
        work()
    """
    work()

    log_info("main ends, bye!")
    return

main()
exit()

#######################################################################


# k1.py
