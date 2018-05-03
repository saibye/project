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
from saitu   import *


"""
"""
#######################################################################


def data_15min(_stock_id, _db):
    df = None

    try:
        df = ts.get_k_data(_stock_id, ktype='15', autype='qfq')
    except Exception:
        log_error("warn: %s get_sina_dd exception!", _stock_id)
        time.sleep(5)
        return -1

    if df is None :
        log_error("warn: stock %s is None, next", _stock_id)
        return -2

    if df.empty:
        log_error("warn: stock %s is empty, next", _stock_id)
        return -3

    log_info("15min: length: %d", len(df))
    log_info("15min: df:\n%s", df)
 
    return 0


def data_day(_stock_id, _db):
    df = None

    start_date = "2017-08-31"
    end_date   = get_date_by(1)

    try:
        df = ts.get_k_data(_stock_id, autype='qfq', start=start_date, end=end_date)
    except Exception:
        log_error("warn: %s get_sina_dd exception!", _stock_id)
        time.sleep(5)
        return -1

    if df is None :
        log_error("warn: stock %s is None, next", _stock_id)
        return -2

    if df.empty:
        log_error("warn: stock %s is empty, next", _stock_id)
        return -3

    log_info("day: length: %d", len(df))
    log_info("day: df:\n%s", df)
 
    return 0



"""
浠