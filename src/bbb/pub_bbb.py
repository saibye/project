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


def bbb_mail_content():
    content = ""
    content += "优先：需要结合箱体形态！\n"

    return content




# X点往前
# RPV
# avg(+rate*vol)  / avg(-rate*vol)
def bbb_rpv(_detail_df, _used_len, _till, _n, _db):
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
        rpv_rt = 99.99
        # log_debug("D_days: %d", D_days)
    elif abs(D_sum) <= 1:
        rpv_rt = 99.99
        # log_debug("D_sum: %d",  D_sum)
    else:
        # log_info("[%.2f, %d], [%.2f, %d]", U_sum, U_days, D_sum, D_days)
        U_rpv = U_sum / U_days
        D_rpv = D_sum / D_days
        rpv_rt = U_rpv / D_rpv
    # log_info("URPV[%.2f], DRPV[%.2f], RT[%.2f]", U_rpv, D_rpv, rpv_rt)

    return abs(rpv_rt)



def bbb_dynamic_calc_tech(_df):

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


def bbb_format_ref(_stock_id, _detail_df):

    # _detail MUST be sorted
    rv = ref_init4(_detail_df)
    if rv < 0:
        log_error("error: ref_init4")
        return -1

    _detail_df.sort_index(ascending=False, inplace=True)
    bbb_dynamic_calc_tech(_detail_df)
    _detail_df.sort_index(ascending=True,  inplace=True)

    ref_set_tech5()


    return 0


#
# X点往前突破天数
# 收盘价
#
def bbb_break_preceding_days(_detail_df, _used_len, _date, _my_price, _db):

    days = 0
    last_date = ""
    to_start = False

    for row_index, row in _detail_df.iterrows():
        pub_date         = row['pub_date']
        close_price      = row['close_price']
        # log_debug("pub_date: [%s]", pub_date)

        if to_start:
            if _my_price > close_price:
                days = days + 1
            else:
                last_date = pub_date
                break

        if not to_start and str(_date) == str(pub_date):
            to_start = True

    return days, last_date

# 
# X点往前突破天数
# 成交量
#
def bbb_vol_break_preceding_days(_detail_df, _used_len, _date, _my_high, _db):

    days = 0
    last_date = ""
    to_start = False

    for row_index, row in _detail_df.iterrows():
        pub_date = row['pub_date']
        vol      = row['total']
        # log_debug("pub_date: [%s]", pub_date)

        if to_start:
            if _my_high > vol:
                days = days + 1
            else:
                last_date = pub_date
                break

        if not to_start and str(_date) == str(pub_date):
            to_start = True

    return days, last_date



# X点往前n单位内的最大升幅
def bbb_get_max_raise(_detail_df, _till, _n, _db):

    idx  = 0
    days = 0

    to_start = False
    from_price = 0.0

    max_rate  = 0.0
    max_step  = 0.0

    max_rate_idx = 0
    max_rate_step = 0.0

    max_rate_date = ""
    max_step_date = ""

    for row_index, row in _detail_df.iterrows():
        close_price      = row['close_price']
        pub_date         = row['pub_date']
        # log_debug("date: %s pk %s", _till, pub_date)

        if to_start:

            days = days + 1
            if days > _n:
                # log_debug("bye: %s -- %d", pub_date, days)
                break

            rate = (from_price - close_price) * 100.00 / close_price
            step = rate / days
            # log_debug("%s -- rate:%.2f%%, step:%.2f%%", pub_date, rate, step)

            if rate > max_rate:
                max_rate = rate
                max_rate_date = pub_date
                max_rate_step = step
                max_rate_idx  = idx


        if not to_start and str(_till) == str(pub_date):
            to_start = True
            from_price = close_price

        idx  = idx + 1

    return max_rate, max_rate_step, max_rate_date, max_rate_idx


# 寻找拐点
#
#
def bbb_inflection_point(_detail_df, _till, _p1, _p2, _db):

    to_start = False

    idx  = 0
    D1 = 50 # 50单位内最大最大涨幅
    D2 = 200 # 只处理前200

    max_step = 0.0
    max_step_start = ""
    max_step_end   = ""

    max_rate = 0.0
    max_rate_step = 0.0
    max_rate_start = ""
    max_rate_end   = ""
    max_rate_start_idx = 0
    max_rate_end_idx   = 0

    for row_index, row in _detail_df.iterrows():
        close_price      = row['close_price']
        pub_date         = row['pub_date']

        if to_start:
            if close_price < _p1 or close_price > _p2:
                # not in range [p1, p2] region, ignore
                idx = idx + 1
                continue

            this_rate, this_step, this_rate_date, this_idx = bbb_get_max_raise(_detail_df, pub_date, D1, _db)
            if this_rate > 10.0:

                if this_rate > max_rate:
                    max_rate = this_rate
                    max_rate_step  = this_step
                    max_rate_start = this_rate_date
                    max_rate_end   = pub_date
                    max_rate_start_idx = this_idx
                    max_rate_end_idx   = idx

            else:
                # log_debug("no raise, don't care: %s, %.2f%%", pub_date, this_rate)
                pass

        if not to_start and str(_till) == str(pub_date):
            # log_debug("let's start1: %s", pub_date)
            to_start = True

        idx  = idx + 1

    # log_info("rate-max: %.2f%%, step:%.2f%% -- [%s, %s]", max_rate, max_rate_step, max_rate_start, max_rate_end)

    return max_rate, max_rate_step, max_rate_start, max_rate_end, max_rate_start_idx, max_rate_end_idx


# 取区域的标准差、平均值
# BC-frame
def bbb_devia(_detail_df, _n1, _n2, _db):

    s1 = _detail_df['close_price']
    # log_debug("series: %s", s1)

    s2 = s1[_n1: _n2]
    # log_debug("[%s]:\n%s", s2)
    my_std  = s2.std()
    my_mean = s2.mean()

    # log_debug("[%d, %d]: %.2f, %.2f", _n1, _n2, my_std, my_mean)

    return my_std, my_mean

# pub_bbb.py
