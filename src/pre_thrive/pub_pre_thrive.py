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
from saitech import *

#######################################################################
#
#######################################################################


def pre_thrive_mail_content():
    content = ""
    content += "注意：不能被ma200压制！\n"
    content += "优先：附近有ma200支撑！\n"
    content += "优先：收复ma20或伴随5/10穿越最佳！\n"

    return content



# X点往前
# RPV
# avg(+rate*vol)  / avg(-rate*vol)
def pre_thrive_rpv(_detail_df, _used_len, _till, _n, _db):
    U_sum = 0.0 # up
    U_days = 0
    D_sum = 0.0 # down
    D_days = 0

    U_rpv = 1.0
    D_rpv = 1.0

    TECH_IDX = 0
    to_start = False

    idx = 0
    max_vol = 0.0
    rel_vr  = 0.0
    rel_rt  = 0.0
    days    = 0
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx
        close_price      = row['close_price']
        vol              = row['total']
        pub_date         = row['pub_date']
        last_close_price = row['last']
        rate = (close_price - last_close_price) / last_close_price * 100

        if not to_start and str(_till) == str(pub_date):
            to_start = True

        if to_start:
            days = days + 1
            if days > _n:
                # log_debug("finished: %d > %d", days, _n)
                break
            else:
                if rate > 0.0:
                    U_sum  += rate * vol
                    U_days += 1
                    # log_debug("U: %s: %.2f * %.2f += %.2f, U(%d)", pub_date, rate, vol, U_sum, U_days)
                else:
                    D_sum += rate * vol
                    D_days+= 1
                    # log_debug("D: %s: %.2f * %.2f += %.2f, D(%d)", pub_date, rate, vol, D_sum, D_days)
        else:
            # log_debug("%s not ready", pub_date)
            pass

        idx  = idx + 1

    if U_days <= 0:
        rpv_rt = -11.11
    elif D_days <= 0:
        rpv_rt = 9.99
        # log_debug("D_days: %d", D_days)
    elif abs(D_sum) <= 1:
        rpv_rt = 9.99
        # log_debug("D_sum: %d",  D_sum)
    else:
        # log_info("[%.2f, %d], [%.2f, %d]", U_sum, U_days, D_sum, D_days)
        U_rpv = U_sum / U_days
        D_rpv = D_sum / D_days
        rpv_rt = U_rpv / D_rpv
    # log_info("URPV[%.2f], DRPV[%.2f], RT[%.2f]", U_rpv, D_rpv, rpv_rt)

    return abs(rpv_rt)



def pre_thrive_dynamic_calc_tech(_df):

    sc = _df['close_price']

    # sma5
    se = calc_sma(sc, 5)
    _df['ma5'] = se;

    # sma10
    se = calc_sma(sc, 10)
    _df['ma10'] = se;

    # sma20
    se = calc_sma(sc, 20)
    _df['ma20'] = se;

    # sma30
    se = calc_sma(sc, 30)
    _df['ma30'] = se;

    # sma60
    se = calc_sma(sc, 60)
    _df['ma60'] = se;

    # sma120
    se = calc_sma(sc, 120)
    _df['ma120'] = se;

    # sma150
    se = calc_sma(sc, 150)
    _df['ma150'] = se;

    # sma200
    se = calc_sma(sc, 200)
    _df['ma200'] = se;

    # macd: ema(12), ema(26), diff, dea(9), macd
    sm, sn, sd, se, sa = calc_macd_list0(sc, 12, 26, 9)
    _df['ema12'] = sm;
    _df['ema26'] = sn;
    _df['diff']  = sd;
    _df['dea']   = se;
    _df['macd']  = sa;

    sv = _df['total']

    # volume - sma5
    se = calc_sma(sv, 5)
    _df['vma5'] = se;

    se = calc_sma(sv, 10)
    _df['vma10'] = se;

    se = calc_sma(sv, 50)
    _df['vma50'] = se;

    return 0


def pre_thrive_format_ref(_stock_id, _detail_df):

    # _detail MUST be sorted
    rv = ref_init4(_detail_df)
    if rv < 0:
        log_error("error: ref_init4")
        return -1

    _detail_df.sort_index(ascending=False, inplace=True)
    pre_thrive_dynamic_calc_tech(_detail_df)
    _detail_df.sort_index(ascending=True,  inplace=True)

    ref_set_tech5()


    return 0


#
# X点往前n1单位起始，n2单位内的最高high价
#
def pre_thrive_preceding_high(_detail_df, _used_len, _date, _n1, _n2, _db):
    idx = 0
    days = 0
    to_start = False
    to_count = False

    max_high = 0.0
    high_close = 0.0
    high_date = ""
    high_rate = 0.0
    high_idx = 0
    high_vol = 0
    high_vr = 0

    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx

        pub_date         = row['pub_date']
        close_price      = row['close_price']
        high_price       = row['high_price']

        last_close_price = row['last']
        open_price       = row['open_price']
        vol              = row['total']


        # log_debug("pub_date: [%s]", pub_date)

        if to_start:
            days = days + 1
            if days >= _n1:
                # log_debug("to count: %s", pub_date)
                to_start = False
                to_count = True
                days = 0

        if to_count:
            days = days + 1
            if days > _n2:
                # log_debug("reach n2: %d", days)
                break
            else:
                # log_debug("[%d, %s, %.2f]", days, pub_date, high_price)
                if high_price > max_high:
                    max_high  = high_price
                    high_close= close_price
                    high_date = pub_date
                    high_idx  = idx
                    high_vol  = vol
                    # log_debug("high:[%s.2f, %s]", max_high, high_date)
                    high_rate = (close_price - last_close_price) / last_close_price * 100
                    high_zt = (close_price - open_price) / last_close_price * 100

        if str(_date) == str(pub_date):
            to_start = True

        idx  = idx + 1

    return max_high, high_close, high_date, high_idx, high_vol, high_rate, high_zt


#
# X点往前n1单位起始，n2单位内的最低low价
#
def pre_thrive_preceding_low(_detail_df, _used_len, _date, _n1, _n2, _db):
    idx = 0
    days = 0
    low_date = ""
    to_start = False
    to_count = False
    min_low = 1000.0
    low_close = 0.0

    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx

        pub_date         = row['pub_date']
        close_price      = row['close_price']
        high_price       = row['high_price']
        low_price        = row['low_price']

        last_close_price = row['last']
        open_price       = row['open_price']
        vol              = row['total']


        # log_debug("pub_date: [%s]", pub_date)

        if to_start:
            days = days + 1
            if days >= _n1:
                # log_debug("to count: %s", pub_date)
                to_start = False
                to_count = True
                days = 0

        if to_count:
            days = days + 1
            if days > _n2:
                # log_debug("reach n2: %d", days)
                break
            else:
                # log_debug("[%d, %s]", days, pub_date)
                if low_price < min_low:
                    min_low = low_price
                    low_close= close_price
                    low_date = pub_date
                    low_idx  = idx
                    low_vol  = vol
                    # log_debug("low:[%s.2f, %s]", min_low, low_date)
                    low_rate = (close_price - last_close_price) / last_close_price * 100

        if str(_date) == str(pub_date):
            to_start = True

        idx  = idx + 1

    return min_low, low_close, low_date, low_idx, low_vol, low_rate


#
# X点往前n1单位内的最高high价
#
def pre_thrive_preceding_high2(_detail_df, _used_len, _date, _n1, _db):
    idx = 0
    days = 0
    to_start = False
    to_count = False

    max_high = 0.0
    high_close = 0.0
    high_date = ""
    high_rate = 0.0
    high_idx = 0
    high_vol = 0
    high_vr = 0

    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx

        pub_date         = row['pub_date']
        close_price      = row['close_price']
        high_price       = row['high_price']

        last_close_price = row['last']
        open_price       = row['open_price']
        vol              = row['total']

        # log_debug("pub_date: [%s]", pub_date)

        if str(_date) == str(pub_date):
            to_start = True

        if to_start:
            days = days + 1
            if days > _n1:
                # log_debug("reach n2: %d", days)
                break
            else:
                # log_debug("[%d, %s, %.2f]", days, pub_date, high_price)
                if high_price > max_high:
                    max_high  = high_price
                    high_close= close_price
                    high_date = pub_date
                    high_idx  = idx
                    high_vol  = vol
                    # log_debug("high:[%s.2f, %s]", max_high, high_date)
                    high_rate = (close_price - last_close_price) / last_close_price * 100


        idx  = idx + 1

    return max_high, high_close, high_date, high_idx, high_vol, high_rate, high_vr


#
# X点往前n1单位内最高价连续走低的天数
#
def pre_thrive_desceding_days(_detail_df, _used_len, _date, _n1, _db):
    idx = 0
    days = 0
    to_start = False
    to_count = False

    counter = 0
    top_date = ""
    top_price = 0.0

    last_high = 0.0

    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx

        pub_date         = row['pub_date']
        close_price      = row['close_price']
        high_price       = row['high_price']

        last_close_price = row['last']
        open_price       = row['open_price']
        vol              = row['total']

        rate = (close_price - last_close_price) / last_close_price * 100
        # log_debug("pub_date: [%s]", pub_date)

        if str(_date) == str(pub_date):
            to_start = True

        if to_start:
            days = days + 1
            if days > _n1:
                # log_debug("reach n2: %d", days)
                break
            else:
                # log_debug("[%d, %s, %.2f, %.2f]", days, pub_date, high_price, rate)
                if rate < 3 and high_price > last_high:
                    counter += 1
                    top_date = pub_date
                    top_price = high_price
                    # log_debug("desceding high:[%s, %.2f]", pub_date, rate)
                else:
                    # log_debug("not match: rate[%.2f], this[%.2f], [%.2f]last", rate, high_price, last_high)
                    break

            last_high = high_price


        idx  = idx + 1

    return top_date, top_price, counter

# 
# X点往前突破天数
# 最高价
#
def pre_thrive_break_days(_detail_df, _used_len, _date, _my_high, _db):

    days = 0
    last_date = ""
    to_count = False

    for row_index, row in _detail_df.iterrows():
        pub_date         = row['pub_date']
        close_price      = row['close_price']
        high_price       = row['high_price']
        # log_debug("pub_date: [%s]", pub_date)

        if to_count:
            if high_price > _my_high:
                last_date = pub_date
                break
            else:
                days = days + 1


        if str(_date) == str(pub_date):
            to_count = True

    return days, last_date


def pre_thrive_save(_stock_id, _pub_date, _price, _title, _message, _db):
    inst_date = get_today()
    inst_time = get_time()

    sql = "insert into tbl_watch \
(pub_date, stock_id, stock_loc, good_type, \
expect_price, expect_direction, \
title, message, \
inst_date, inst_time) \
values ('%s', '%s', '%s', '%s', \
'%.2f', '%s', \
'%s', '%s', \
'%s', '%s')" % \
    (_pub_date, _stock_id, 'cn', 'pre-thrive',
     _price, '00',
     _title, _message, 
     inst_date, inst_time)

    log_debug("sql: [%s]", sql)
    rv = sql_to_db(sql, _db)

    return rv

# pub_pre_thrive.py
