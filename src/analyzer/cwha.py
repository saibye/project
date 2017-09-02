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

g_detail_fetched = 150
g_detail_used    = 100


def cwha_analyzer(_stock_id, _k_date, _a_date, _b_date, _c_date, _d_date, _e_date, _my_df, _used_len, _db):
    global g_detail_fetched 

    lowest   = 0
    mailed = 0
    content1 = "Cup with Handle\n"
    to_mail = False

    idx    = 0
    TECH_IDX = 0

    BACK1  = -10.0
    BACK2  = -4.5

    BACK1  = -8.6
    BACK2  = -1.7

    RISE1  = 10 # 柳钢股份
    RISE2  = 4

    RISE1  = 7.3 # 海康威视
    RISE2  = 3

    VR1    = 40
    VR2    = 50

    BACK_AB = -13.5

    # 茶杯左端+
    p_A = 0
    v_A = 0
    i_A = -1
    d_A = ""
    rt_A = 0
    vr_A = 0

    # 茶杯底-
    p_B = 1000
    v_B = 0
    i_B = -1
    d_B = ""
    rt_B = 0
    vr_B = 0

    # 茶杯右端+
    p_C = 0
    v_C = 0
    i_C = -1
    d_C = ""
    rt_C = 0
    vr_C = 0

    # 柄底-
    p_D = 1000
    v_D = 0
    i_D = -1
    d_D = ""
    rt_D = 0
    vr_D = 0

    # 突破点+
    p_E = 0
    v_E = 0
    i_E = -1
    d_E = ""
    rt_E = 0
    vr_E = 0

    v_max = 0
    c_max = 0
    i_max = -1
    c_min = 1000
    i_min = -1

    # 回调幅度 <0
    # A -> B
    back1 = 0
    back1_ext = 0
    # C -> D
    back2 = 0
    back2_ext = 0

    got_A = False
    got_B = False
    got_C = False
    got_D = False
    got_E = False

    AB = 0 # A到B天数
    BC = 0 # B到C天数
    CD = 0 # C到D天数

    for row_index, row in _my_df.iterrows():
        TECH_IDX = _used_len - idx - 1

        close_price      = row['close_price']
        high_price       = row['high_price']
        low_price        = row['low_price']
        last_close_price = row['last']
        open_price       = row['open_price']
        vol              = row['total']
        pub_date         = row['pub_date']
        rate = (close_price - last_close_price) / last_close_price * 100
        zt   = (close_price - open_price) / last_close_price * 100

        if ref_vma50(TECH_IDX) > 0:
            vr = (vol / ref_vma50(TECH_IDX) - 1) * 100
        else:
            vr = 0
        log_debug("--------------------%s-------------------", pub_date)


        if vol > v_max:
            v_max  = vol
            c_vmax = close_price

        if close_price > c_max:
            c_max = close_price
            i_max = idx

        if close_price < c_min:
            c_min = close_price
            i_min = idx

        # K点
        if str(_k_date) == str(pub_date):
            log_debug("nice: K-point: %s", pub_date)
            got_K = True
            v_K = vol
            p_K = close_price
            h_K = high_price
            l_K = low_price
            i_K = idx
            d_K = pub_date
            rt_K= rate
            vr_K= vr
            log_info("Data: %s-K: %s, low:%.2f, vol:%.2f, %d", _stock_id, pub_date, l_K, v_K, i_K)

        # A点
        if str(_a_date) == str(pub_date):
            log_debug("nice: A-point: %s", pub_date)
            got_A = True
            v_A = vol
            p_A = close_price
            h_A = high_price
            l_A = low_price
            i_A = idx
            d_A = pub_date
            rt_A= rate
            vr_A= vr
            log_info("Data: %s-A: %s, high:%.2f, vol:%.2f, %d", _stock_id, pub_date, h_A, v_A, i_A)

        # B点
        if str(_b_date) == str(pub_date):
            log_debug("nice: B-point: %s", pub_date)
            got_B = True
            v_B = vol
            p_B = close_price
            h_B = high_price
            l_B = low_price
            i_B = idx
            d_B = pub_date
            rt_B= rate
            vr_B= vr
            log_info("Data: %s-B: %s, low:%.2f, vol:%.2f, %d", _stock_id, pub_date, l_B, v_B, i_B)

        # C点
        if str(_c_date) == str(pub_date):
            log_debug("nice: C-point: %s", pub_date)
            got_C = True
            v_C = vol
            p_C = close_price
            h_C = high_price
            l_C = low_price
            i_C = idx
            d_C = pub_date
            rt_C= rate
            vr_C= vr
            log_info("Data: %s-C: %s, high:%.2f, vol:%.2f, %d", _stock_id, pub_date, h_C, v_C, i_C)

        # D点
        if str(_d_date) == str(pub_date):
            log_debug("nice: D-point: %s", pub_date)
            got_D = True
            v_D = vol
            p_D = close_price
            h_D = high_price
            l_D = low_price
            i_D = idx
            d_D = pub_date
            rt_D= rate
            vr_D= vr
            log_info("Data: %s-D: %s, low:%.2f, vol:%.2f, %d", _stock_id, pub_date, l_D, v_D, i_D)

        # E点
        if str(_e_date) == str(pub_date):
            log_debug("nice: E-point: %s", pub_date)
            got_E = True
            v_E = vol
            p_E = close_price
            h_E = high_price
            l_E = low_price
            i_E = idx
            d_E = pub_date
            rt_E= rate
            rt_E2= (h_E / last_close_price - 1) * 100.00
            vr_E= vr
            log_info("Data: %s-E: %s, high:%.2f, vol:%.2f, %d", _stock_id, pub_date, h_E, v_E, i_E)



        idx  = idx + 1
    # for

    if got_A and got_B and got_C and got_D and got_E and got_K:
        log_info("bingo: %s", _stock_id)
        rate_DE = h_E / l_D * 100.00
        len_DE  = i_E - i_D
        rate_CE = h_E / h_C * 100.00
        len_CD  = i_D - i_C
        rate_AE = h_A / h_E * 100.00
        len_AB  = i_B - i_A
        len_BC  = i_C - i_B
        len_AC  = i_C - i_A
        rate_AB = h_A / l_B * 100.00
        rate_BC = h_C / l_B * 100.00
        len_KA  = i_A - i_K
        rate_KA = h_A / l_K * 100.00

        log_info("data: %s: KA长度: %d", _stock_id, len_KA)
        log_info("data: %s: AB长度: %d", _stock_id, len_AB)
        log_info("data: %s: BC长度: %d", _stock_id, len_BC)
        log_info("data: %s: AC长度: %d", _stock_id, len_AC)
        log_info("data: %s: CD长度: %d", _stock_id, len_CD)
        log_info("data: %s: DE长度: %d", _stock_id, len_DE)
        log_info("data: %s: AK比率: %.2f",   _stock_id, rate_KA)
        log_info("data: %s: AB比率: %.2f",   _stock_id, rate_AB)
        log_info("data: %s: CB比率: %.2f",   _stock_id, rate_BC)
        log_info("data: %s: AE比率: %.2f",   _stock_id, rate_AE)
        log_info("data: %s: DE比率: %.2f",   _stock_id, rate_DE)
        log_info("data: %s: CE比率: %.2f",   _stock_id, rate_CE)
        log_info("data: %s: B点量比: +%.2f", _stock_id, vr_B)
        log_info("data: %s: D点量比: +%.2f", _stock_id, vr_D)
        log_info("data: %s: A点量比: +%.2f", _stock_id, vr_A) # TODO
        log_info("data: %s: C点量比: +%.2f", _stock_id, vr_C) # TODO
        log_info("data: %s: E点量比: +%.2f", _stock_id, vr_E) # TODO
        log_info("data: %s: E点涨幅:  %.2f", _stock_id, rt_E)
        log_info("data: %s: E点涨幅2: %.2f", _stock_id, rt_E2)

        # A点附近最大成交量
        A1 = 4
        A_vol_max, A_rel_vr, A_rel_rt, A_rel_rt2 = cwha_max_vol(_my_df, _used_len, _a_date, A1, _db)
        log_info("data: %s: A点附近[%d]最大成交量: %.2f, +%.2f%%, %.2f%%, high:%.2f%%",
                _stock_id, A1, A_vol_max, A_rel_vr, A_rel_rt, A_rel_rt2)

        # C点附近最大成交量
        C1 = 4
        C_vol_max, C_rel_vr, C_rel_rt, C_rel_rt2 = cwha_max_vol(_my_df, _used_len, _c_date, C1, _db)
        log_info("data: %s: C点附近[%d]最大成交量: %.2f, +%.2f%%, %.2f%%, high:%.2f%%",
                _stock_id, C1, C_vol_max, C_rel_vr, C_rel_rt, C_rel_rt2)

        # D点之前rpv
        D2 = 4
        D2 = 20
        D_rpv_rt = cwha_rpv(_my_df, _used_len, _d_date, D2, _db)
        log_info("data: %s: D点之前[%d]RPV比率: %.2f",
                _stock_id, D2, D_rpv_rt)

        # B点方差最小的平均值
        B3 = 10
        B4 = 5
        B_mean, B_std, B_rel_date, B_rel_idx = cwha_devia(_my_df, _used_len, _b_date, B3, B4, _db)
        log_info("data: %s: B点附近[%d]长度[%d]平均值: %.2f, 标准差: %.2f [%s]",
                _stock_id, B3, B4, B_mean, B_std, B_rel_date)

        rate_BS = B_mean / l_B * 100.00
        rate_AS = p_A / B_mean * 100.00
        log_info("data: %s: BS比率: %.2f",   _stock_id, rate_BS)
        log_info("data: %s: AS比率: %.2f",   _stock_id, rate_AS)
        # TODO: A点平均值

        # E点最高价突破天数
        E_days, E_block_date = cwha_price_break_days(_my_df, _used_len, _e_date, h_E, _db)
        log_info("data: %s: E突破: %d, %s, %.2f(high-price)",   _stock_id, E_days, E_block_date, h_E)

        # E点成交量突破天数
        E_days2, E_block_date2 = cwha_vol_break_days(_my_df, _used_len, _e_date, v_E, _db)
        log_info("data: %s: E突破2:%d, %s, %.2f(vol)",   _stock_id, E_days2, E_block_date2, v_E)

        # C点之前rpv
        C2 = 8
        C_rpv_rt = cwha_rpv(_my_df, _used_len, _c_date, C2, _db)
        log_info("data: %s: C点之前[%d]RPV比率: %.2f",
                _stock_id, C2, C_rpv_rt)

        # A点之前rpv
        A2 = 8
        A_rpv_rt = cwha_rpv(_my_df, _used_len, _a_date, A2, _db)
        log_info("data: %s: A点之前[%d]RPV比率: %.2f",
                _stock_id, A2, A_rpv_rt)

        # E点之前rpv2
        E3 = i_E - i_K
        E_rpv_rt = cwha_rpv(_my_df, _used_len, _e_date, E3, _db)
        log_info("data: %s: E点之前[%d]RPV比率: %.2f",
                _stock_id, E3, E_rpv_rt)

        # A点平均值
        A_mean = cwha_mean(_my_df, _used_len, _a_date, 1, 1, _db)
        log_info("A点附近[1]长度平均值: %.2f", A_mean)

        rate_ABM= A_mean / B_mean * 100.00
        log_info("data: %s: ABM比率: %.2f",   _stock_id, rate_ABM)

    else:
        log_info("error: not got all point")

    if to_mail:
        subject = "cwha: %s -- %s" % (_stock_id, _e_date)
        log_info(subject)
        log_info("mail:\n%s", content1)
        mailed = 1
        saimail_dev(subject, content1)
    else:
        log_info("--: %s, %s", _stock_id, _e_date)

    return 0



# A点附近的最大成交量
#
def cwha_max_vol(_detail_df, _used_len, _date, _n, _db):

    idx = 0
    TECH_IDX = 0
    for row_index, row in _detail_df.iterrows():
        pub_date         = row['pub_date']

        if str(_date) == str(pub_date):
            break

        idx  = idx + 1

    # log_info("date[%s] => idx[%d]", _date, idx)
    start_idx = idx - _n
    end_idx   = idx + _n
    # log_info("start:[%d] => end[%d]", start_idx, end_idx)

    if start_idx < 0 or end_idx > len(_detail_df):
        log_error("error: exceeds: %d, %d", start_idx, end_idx)
        return -1, -1, -1

    idx = 0
    max_vol = 0.0
    rel_vr  = 0.0
    rel_rt  = 0.0
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = _used_len - idx - 1
        close_price      = row['close_price']
        high_price       = row['high_price']
        vol              = row['total']
        pub_date         = row['pub_date']
        last_close_price = row['last']
        rate = (close_price - last_close_price) / last_close_price * 100
        rate2= (high_price - last_close_price) / last_close_price * 100

        if idx >= start_idx and idx < end_idx:
            # log_debug("[%s]: [%d, %d]: [%.2f, %.2f]", pub_date, idx, TECH_IDX, vol, ref_vma50(TECH_IDX))
            if ref_vma50(TECH_IDX) > 0:
                vr = (vol / ref_vma50(TECH_IDX) - 1) * 100
            else:
                vr = 0.0

            if vol > max_vol:
                max_vol = vol
                rel_vr  = vr
                rel_rt  = rate
                rel_rt2 = rate2
        else:
            pass

        idx  = idx + 1

    # log_info("max vol: %.2f, v-rate: +%.2f%%, p-rate: %.2f%%", max_vol, rel_vr, rel_rt)

    return max_vol, rel_vr, rel_rt, rel_rt2

# RPV
# avg(+rate*vol)  / avg(-rate*vol)
def cwha_rpv(_detail_df, _used_len, _till, _n, _db):
    U_sum = 0.0 # up
    U_days = 0
    D_sum = 0.0 # down
    D_days = 0

    U_rpv = 1.0
    D_rpv = 1.0

    idx = 0
    TECH_IDX = 0
    for row_index, row in _detail_df.iterrows():
        pub_date         = row['pub_date']

        if str(_till) == str(pub_date):
            break

        idx  = idx + 1

    # log_info("date[%s] => idx[%d]", _till, idx)
    start_idx = idx - _n
    end_idx   = idx
    # log_info("start:[%d] => end[%d]", start_idx, end_idx)

    if start_idx < 0:
        log_error("error: exceeds: %d, %d", start_idx, end_idx)
        return -19.99

    idx = 0
    max_vol = 0.0
    rel_vr  = 0.0
    rel_rt  = 0.0
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = _used_len - idx - 1
        close_price      = row['close_price']
        vol              = row['total']
        pub_date         = row['pub_date']
        last_close_price = row['last']
        rate = (close_price - last_close_price) / last_close_price * 100

        if idx > start_idx and idx <= end_idx:
            if rate > 0.0:
                U_sum  += rate * vol
                U_days += 1
                # log_debug("U: %s: %.2f * %.2f += %.2f, U(%d)", pub_date, rate, vol, U_sum, U_days)
            else:
                D_sum += rate * vol
                D_days+= 1
                # log_debug("D: %s: %.2f * %.2f += %.2f, D(%d)", pub_date, rate, vol, D_sum, D_days)
        else:
            pass

        idx  = idx + 1

    if U_days <= 0:
        rpv_rt = -11.11
    elif D_days <= 0:
        rpv_rt = 9.99
    else:
        # log_info("[%.2f, %d], [%.2f, %d]", U_sum, U_days, D_sum, D_days)
        U_rpv = U_sum / U_days
        D_rpv = D_sum / D_days
        rpv_rt = U_rpv / D_rpv
    # log_info("URPV[%.2f], DRPV[%.2f], RT[%.2f]", U_rpv, D_rpv, rpv_rt)

    return abs(rpv_rt)


# 方差最小时的平均值
# B-frame
def cwha_devia(_detail_df, _used_len, _date, _n1, _n2, _db):

    idx = 0
    TECH_IDX = 0
    min_std  = 1000.0
    min_mean = 0.0
    min_date = ""
    min_idx  = -1

    start_idx2 = 0
    end_idx2   = 0

    for row_index, row in _detail_df.iterrows():
        pub_date         = row['pub_date']

        if str(_date) == str(pub_date):
            break

        idx  = idx + 1

    # log_info("date[%s] => idx[%d]", _date, idx)
    start_idx = idx - _n1
    end_idx   = idx + _n1
    # log_info("start:[%d] => end[%d]", start_idx, end_idx)

    if start_idx < 0 or end_idx > len(_detail_df):
        log_error("error: exceeds: %d, %d", start_idx, end_idx)
        return -1, -1, -1, -1

    s1 = _detail_df['low_price']
    # log_debug("series: %s", s1)

    idx = 0
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = _used_len - idx - 1
        close_price      = row['close_price']
        vol              = row['total']
        pub_date         = row['pub_date']
        last_close_price = row['last']
        rate = (close_price - last_close_price) / last_close_price * 100

        if idx >= start_idx and idx < end_idx:
            start_idx2 = idx - _n2
            end_idx2   = idx + _n2
            if start_idx2 < 0 or end_idx2 > len(_detail_df):
                continue
            s2 = s1[start_idx2: end_idx2]
            # log_debug("[%s]:\n%s", pub_date, s2)
            std = s2.std()
            # log_debug("[%s]: std: %.2f, mean: %.2f", pub_date, std, s2.mean())
            if std < min_std:
                min_std  = std
                min_mean = s2.mean()
                min_date = pub_date
                min_idx  = idx
        else:
            pass

        idx  = idx + 1
    # for

    # log_debug("[%s]: %.2f, %.2f, %d", min_date, min_std, min_mean, min_idx)

    return min_mean, min_std, min_date, min_idx


# 最高价
# E点往前突破天数
#
def cwha_price_break_days(_detail_df, _used_len, _date, _my_high, _db):

    days = 0
    last_date = ""

    idx = 0
    for row_index, row in _detail_df.iterrows():
        pub_date         = row['pub_date']
        close_price      = row['close_price']
        high_price       = row['high_price']

        # log_debug("%s => %.2f", pub_date, high_price)

        if high_price > _my_high:
            days = 0
            last_date = pub_date
        else:
            days = days + 1
            # log_debug("add: %d", days)

        if str(_date) == str(pub_date):
            break

        idx  = idx + 1

    # log_info("date[%s] => idx[%d]", _date, idx)

    # log_info("max vol: %.2f, v-rate: +%.2f%%, p-rate: %.2f%%", max_vol, rel_vr, rel_rt)

    return days, last_date


# 成交量
# E点往前突破天数
#
def cwha_vol_break_days(_detail_df, _used_len, _date, _my_high_vol, _db):

    days = 0
    last_date = ""

    idx = 0
    for row_index, row in _detail_df.iterrows():
        pub_date         = row['pub_date']
        close_price      = row['close_price']
        vol              = row['total']

        # log_debug("%s => %.2f", pub_date, high_price)

        if vol > _my_high_vol:
            days = 0
            last_date = pub_date
        else:
            days = days + 1
            # log_debug("add: %d", days)

        if str(_date) == str(pub_date):
            break

        idx  = idx + 1

    # log_info("date[%s] => idx[%d]", _date, idx)

    # log_info("max vol: %.2f, v-rate: +%.2f%%, p-rate: %.2f%%", max_vol, rel_vr, rel_rt)

    return days, last_date


# A点附近平均值
# A-frame
def cwha_mean(_detail_df, _used_len, _date, _n1, _n2, _db):

    idx = 0
    my_mean  = 0.0

    for row_index, row in _detail_df.iterrows():
        pub_date         = row['pub_date']

        if str(_date) == str(pub_date):
            break

        idx  = idx + 1

    # log_info("date[%s] => idx[%d]", _date, idx)
    start_idx = idx - _n1
    end_idx   = idx + _n2+1
    # log_info("start:[%d] => end[%d]", start_idx, end_idx)

    if start_idx < 0 or end_idx > len(_detail_df):
        log_error("error: exceeds: %d, %d", start_idx, end_idx)
        return -1

    s1 = _detail_df['close_price']

    s2 = s1[start_idx: end_idx]
    # log_debug("series: %s", s2)
    my_mean = s2.mean()

    # log_debug("[%s]: %.2f, %.2f, %d", min_date, min_std, min_mean, min_idx)

    return my_mean


def cwha_dynamic_calc_tech(_df):

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


def cwha_format_ref(_stock_id, _detail_df):

    # _detail MUST be sorted
    rv = ref_init4(_detail_df)
    if rv < 0:
        log_error("error: ref_init4")
        return -1

    _detail_df.sort_index(ascending=False, inplace=True)
    cwha_dynamic_calc_tech(_detail_df)
    _detail_df.sort_index(ascending=True,  inplace=True)

    ref_set_tech5()

    """
    log_debug("ref0:  [%.3f, %.3f] -- vol:[%.3f]", ref_open(0), ref_close(0), ref_vol(0))
    log_debug("ref1:  [%.3f, %.3f] -- vol:[%.3f]", ref_open(1), ref_close(1), ref_vol(1))
    log_debug("ref2:  [%.3f, %.3f] -- vol:[%.3f]", ref_open(2), ref_close(2), ref_vol(2))

    log_debug("ma5/10 [%.3f, %.3f] - vma[%.3f, %.3f]", ref_ma5(0), ref_ma10(0), ref_vma5(0), ref_vma10(0))
    log_debug("ma5/10 [%.3f, %.3f] - vma[%.3f, %.3f]", ref_ma5(1), ref_ma10(1), ref_vma5(1), ref_vma10(1))
    log_debug("ma5/10 [%.3f, %.3f] - vma[%.3f, %.3f]", ref_ma5(2), ref_ma10(2), ref_vma5(2), ref_vma10(2))

    log_debug("macd0: [%.3f] [%.3f], [%.3f]", ref_macd(0), ref_diff(0), ref_dea(0))
    log_debug("macd1: [%.3f] [%.3f], [%.3f]", ref_macd(1), ref_diff(1), ref_dea(1))
    log_debug("macd2: [%.3f] [%.3f], [%.3f]", ref_macd(2), ref_diff(2), ref_dea(2))
    """

    return 0


def get_cwha_detail(_stock_id, _pub_date, _n, _db):
    sql = "select stock_id, pub_date, open_price, close_price, \
deal_total_count total, last_close_price last, \
high_price, low_price \
from tbl_day a \
where a.stock_id  = '%s' and a.pub_date <= '%s' \
order by pub_date desc limit %d" % (_stock_id, _pub_date, _n)

    # log_debug("detail-sql:\n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        return df


def get_cwha_stock_list(_till, _db):
    sql = "select distinct stock_id from tbl_day \
where pub_date = \
(select max(pub_date) from tbl_day \
where pub_date <= '%s')" % (_till)

    # log_debug("stock list sql:\n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _till)
        return None
    else:
        df.set_index("stock_id", inplace=True)
        return df


def cwha_work_one_day_stock(_stock_id, _k_date, _a_date, _b_date, _c_date, _d_date, _e_date, _db):

    global g_detail_fetched 
    global g_detail_used

    log_debug("================================================")
    # 获取明细数据
    # 之前n1单位的交易数据
    n1 = g_detail_fetched
    detail_df = get_cwha_detail(_stock_id, _e_date, n1, _db);
    if detail_df is None:
        log_info("[%s, %s] detail is none", _stock_id, _till)
        return -1
    elif detail_df.empty:
        log_debug("detail_df is empty: [%d]", len(detail_df))
        return 1
    else:
        # log_debug("n1: len[%d]", len(detail_df))
        pass

    length = len(detail_df)
    if length < g_detail_used:
        log_info("df-not-enough: %s: %d", _stock_id, length)
        return 1

    # 格式化数据
    rv = cwha_format_ref(_stock_id, detail_df)
    if rv < 0:
        log_error("error: cwha_format_ref: %s", _stock_id)
        return -1

    used_len = g_detail_used
    my_df = detail_df.sort_index(ascending=False).tail(used_len)
    rv = cwha_analyzer(_stock_id, _k_date, _a_date, _b_date, _c_date, _d_date, _e_date, my_df, used_len, _db)
    if rv < 0:
        log_error("error: cwha_analyzer: %s", _stock_id)
        return -1

    return 0




def regression(_db):

    # all
    max_date = "2017-06-26"
    days = 200


    # 600191 @ 2017-07-05
    max_date = "2017-07-05"
    days = 1

    # 000488  @ 2017-06-26
    max_date = "2017-06-26"
    days = 1

    # XXX
    max_date = "2017-07-20"
    days = 30

    log_info("regress")

    """
    # 柳钢股份 case1 init
    till_date = "2016-11-18"
    stock_id  = "601003"
    cwha_work_one_day_stock(stock_id, till_date, db)


    # 海康威视 3
    till_date = "2017-01-18"
    stock_id  = "002415"
    cwha_work_one_day_stock(stock_id, till_date, db)

    # 晨鸣纸业 4
    till_date = "2017-06-28"
    stock_id  = "000488"
    cwha_work_one_day_stock(stock_id, till_date, db)

    # 盐田港 5: FAIL
    till_date = "2017-04-06"
    stock_id  = "000088"
    cwha_work_one_day_stock(stock_id, till_date, db)

    # 华资实业 6 done
    till_date = "2017-07-06"
    stock_id  = "600191"
    cwha_work_one_day_stock(stock_id, till_date, db)

    # 天茂集团 7 done
    till_date = "2017-07-05"
    stock_id  = "000627"
    cwha_work_one_day_stock(stock_id, till_date, db)

    # 珠海港 2 TODO
    till_date = "2017-04-10"
    stock_id  = "000507"
    cwha_work_one_day_stock(stock_id, till_date, db)

    # 东湖高新 8 TODO: high = vol*close_price
    till_date = "2017-07-05"
    stock_id  = "600133"
    cwha_work_one_day_stock(stock_id, till_date, db)

    # 沧州大化 9  TODO: fail: dynamic search
    till_date = "2017-07-10"
    stock_id  = "600230"
    cwha_work_one_day_stock(stock_id, till_date, db)

    # 敦煌种业10  TODO
    till_date = "2017-07-18"
    stock_id  = "600354"
    cwha_work_one_day_stock(stock_id, till_date, db)
    """


    return 0


def work():
    db = db_init()

    if sai_is_product_mode():

        # 沧州大化 bingo
        stock_id  = "600230"
        K_date = "2017-04-17"
        A_date = "2017-04-26"
        B_date = "2017-06-02"
        C_date = "2017-06-30"
        D_date = "2017-07-05"
        E_date = "2017-07-10"
        cwha_work_one_day_stock(stock_id, K_date, A_date, B_date, C_date, D_date, E_date, db)

        """
        """
        # 敦煌种业
        stock_id  = "600354"
        K_date = "2017-04-25"
        A_date = "2017-05-15" # high-price
        B_date = "2017-06-02"
        C_date = "2017-07-12"
        D_date = "2017-07-17"
        E_date = "2017-07-18"
        cwha_work_one_day_stock(stock_id, K_date, A_date, B_date, C_date, D_date, E_date, db)

        # 华资实业 bingo
        stock_id  = "600191"
        K_date = "2017-05-08"
        A_date = "2017-05-16" # high-price
        B_date = "2017-06-02"
        C_date = "2017-06-26"
        D_date = "2017-06-30"
        E_date = "2017-07-05"
        cwha_work_one_day_stock(stock_id, K_date, A_date, B_date, C_date, D_date, E_date, db)

        # 晨鸣纸业 not so match
        stock_id  = "000488"
        K_date = "2017-03-30"
        A_date = "2017-04-18" # high-price
        B_date = "2017-05-11"
        C_date = "2017-06-13"
        D_date = "2017-06-19"
        E_date = "2017-06-26"
        cwha_work_one_day_stock(stock_id, K_date, A_date, B_date, C_date, D_date, E_date, db)


        # 方大碳素 VAR
        stock_id  = "600516"
        K_date = "2017-02-28"
        A_date = "2017-03-03"
        B_date = "2017-04-19"
        C_date = "2017-05-04"
        D_date = "2017-05-09"
        E_date = "2017-05-11"
        cwha_work_one_day_stock(stock_id, K_date, A_date, B_date, C_date, D_date, E_date, db)


        # 洛阳钼业
        stock_id  = "603993"
        K_date = "2017-03-30"
        A_date = "2017-04-07"
        B_date = "2017-06-01"
        C_date = "2017-06-16"
        D_date = "2017-06-23"
        E_date = "2017-07-05"
        cwha_work_one_day_stock(stock_id, K_date, A_date, B_date, C_date, D_date, E_date, db)

        # 东湖高新
        stock_id  = "600133"
        K_date = "2017-05-05"
        A_date = "2017-05-15"
        B_date = "2017-06-02"
        C_date = "2017-07-05"
        D_date = "2017-07-12"
        E_date = "2017-07-17"
        cwha_work_one_day_stock(stock_id, K_date, A_date, B_date, C_date, D_date, E_date, db)

        # 天茂集团
        stock_id  = "600133"
        K_date = "2017-05-09"
        A_date = "2017-05-15"
        B_date = "2017-06-01"
        C_date = "2017-06-26"
        D_date = "2017-06-29"
        E_date = "2017-07-06"
        cwha_work_one_day_stock(stock_id, K_date, A_date, B_date, C_date, D_date, E_date, db)

        # 晨鸣纸业
        stock_id  = "000488"
        K_date = "2017-03-31"
        A_date = "2017-04-18"
        B_date = "2017-05-11"
        C_date = "2017-06-13"
        D_date = "2017-06-19"
        E_date = "2017-06-26"
        cwha_work_one_day_stock(stock_id, K_date, A_date, B_date, C_date, D_date, E_date, db)

        # 凌钢股份
        stock_id  = "600231"
        K_date = "2017-03-29"
        A_date = "2017-04-05"
        B_date = "2017-05-11"
        C_date = "2017-07-10"
        D_date = "2017-07-17"
        E_date = "2017-07-19"
        cwha_work_one_day_stock(stock_id, K_date, A_date, B_date, C_date, D_date, E_date, db)

        # 南钢股份
        stock_id  = "600282"
        K_date = "2017-03-30"
        A_date = "2017-04-07"
        B_date = "2017-05-16"
        C_date = "2017-07-10"
        D_date = "2017-07-12"
        E_date = "2017-07-18"
        cwha_work_one_day_stock(stock_id, K_date, A_date, B_date, C_date, D_date, E_date, db)

    else:
        regression(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("cwha1.log")

    log_info("let's begin here!")

    work()

    log_info("main ends, bye!")

    return

#######################################################################

main()

#######################################################################

# cwha.py
