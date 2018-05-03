#!/usr/bin/env python
# -*- encoding: utf8 -*-


#import tushare as ts
#import pandas as pd
#import numpy as np

from saiutil import *
from saidb   import *
from saisql  import *
from saicalc import *
from sailog  import *
from saimail import *
from sairef  import *
from saitech import *
from saifmt  import *
import saiobj


def stop_one(_stock_id, _till_date, _db):

    df = sai_fmt_simple(_stock_id, _till_date, _db)
    log_debug(df)

    length = len(df)
    if length < 60:
        log_debug('too short: %d', length)
        return -1

    amp_rate = (ref_high(0) - ref_low(0)) / ref_close(0) * 100.00
    cly_rate = (ref_close(0) - ref_open(0)) / ref_close(0) * 100.00
    v50_rate = ref_vol(0) / ref_vma50(1)
    log_debug('amp: %.2f', amp_rate)
    log_debug('cly: %.2f', cly_rate)
    log_debug('v50: %.2f', v50_rate)

    return 0

def stop_all_case():
    log_debug('stop')

    db = saiobj.g_db

    stock_id    = '002509'
    trade_date  = '2018-04-11'
    stop_one(stock_id, trade_date, db)

    return 0


saiobj.g_func_map['stop'] = stop_all_case


if __name__=="__main__":
    sailog_set("stop.log")

    test1()

    log_debug("--end")


# stop.py
