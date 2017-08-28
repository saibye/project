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


def ducka_analyzer(_stock_id, _k_date, _a_date, _b_date, _c_date, _d_date, _e_date, _my_df, _used_len, _db):
    global g_detail_fetched 

    lowest   = 0
    mailed = 0
    content1 = "duck\n"
    to_mail = False

    idx    = 0
    TECH_IDX = 0

    v_max = 0
    c_max = 0
    c_min = 1000

    got_A = False
    got_B = False
    got_C = False
    got_D = False
    got_E = False

    AB = 0 # A到B天数
    BC = 0 # B到C天数
    CD = 0 # C到D天数

    for row_index, row in _my_df.iterrows():
        TECH_IDX = idx

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
            macd_A = ref_macd(TECH_IDX)
            diff_A = ref_diff(TECH_IDX)
            dea_A  = ref_dea(TECH_IDX)
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

    # A点量比
    # A点突破天数
    # A点MACD

    # B点cross4

    # C点方差
    # C点缩量天数

    # D点量比
    # D点放量天数

    # E点涨幅


    if got_A and got_B and got_C and got_D and got_E and got_K:
        log_info("bingo: %s", _stock_id)
        # len_KA  = i_A - i_K
        # rate_KA = h_A / l_K * 100.00
        # len_KA  = i_A - i_K
        # rate_KA = h_A / l_K * 100.00

        log_info("data: %s: A点量比: +%.2f", _stock_id, vr_A)
        log_info("data: %s: A点涨幅:  %.2f", _stock_id, rt_A)
        log_info("data: %s: A点macd:  macd(%.3f), diff(%.3f), dea(%.3f)", _stock_id, macd_A, diff_A, dea_A)

        # A点最高价突破天数
        A_days, A_block_date = ducka_break_days2(_my_df, _used_len, _a_date, p_A, _db)
        log_info("data: %s: A突破: %d, %s, %.2f(high-price)",   _stock_id, A_days, A_block_date, p_A)

        # B点cross4
        B1 = 5
        B_cross4, B_cross3 = ducka_has_cross(_my_df, _used_len, _a_date, B1, _db)
        log_info("data: %s: B点收复4线[%s], 3线[%s]", _stock_id, B_cross4, B_cross3)

        # A点往前缩量
        B3 = 7
        B4 = 10
        B_days, B_date = ducka_shrink_days(_my_df, _used_len, _a_date, B3, B4, _db)
        log_info("data: %s: B缩量天数: %d, %s",   _stock_id, B_days, B_date)

        # B点往前方差最小的平均值
        # C
        C1 = 10
        C2 = 5
        C_mean, C_std, C_rel_date, C_rel_idx = ducka_devia(_my_df, _used_len, _b_date, C1, C2, _db)
        log_info("data: %s: B点往前[%d]长度[%d]平均值: %.2f, 标准差: %.2f [%s]",
                _stock_id, C1, C2, C_mean, C_std, C_rel_date)

        # C点往前放量 TODO
        #
        D3 = 7
        D4 = 10
        D_days, D_date = ducka_shrink_days(_my_df, _used_len, _c_date, D3, D4, _db)
        log_info("data: %s: D放量天数: %d, %s",   _stock_id, D_days, D_date)

        # D点前高
        # 保持开口
        log_info("data: %s: D点量比: +%.2f", _stock_id, vr_D)
        D_beyond, D_days = ducka_beyond_ma60(_my_df, _used_len, _d_date, _db);
        log_info("data: %s: D点开口: %s, %d", _stock_id, D_beyond, D_days)

        # TODO E-D-C-B-A 形成盘整区域

        # K-E 涨幅
        rate_KE = (p_E / p_K - 1) * 100.00
        log_info("data: %s: KE比率: %.2f",   _stock_id, rate_KE)


        # A点之前rpv
        A1 = 8
        A_rpv_rt = ducka_rpv(_my_df, _used_len, _a_date, A1, _db)
        log_info("data: %s: A点之前[%d]RPV比率: %.2f", _stock_id, A1, A_rpv_rt)

        # E点之前rpv
        E1 = 12
        E_rpv_rt = ducka_rpv(_my_df, _used_len, _e_date, E1, _db)
        log_info("data: %s: E点之前[%d]RPV比率: %.2f", _stock_id, E1, E_rpv_rt)

    else:
        log_info("error: not got all point")

    if to_mail:
        subject = "ducka: %s -- %s" % (_stock_id, _e_date)
        log_info(subject)
        log_info("mail:\n%s", content1)
        mailed = 1
        saimail_dev(subject, content1)
    else:
        log_info("--: %s, %s", _stock_id, _e_date)

    return 0

def ducka_work_one_day_stock(_stock_id, _k_date, _a_date, _b_date, _c_date, _d_date, _e_date, _db):

    global g_detail_fetched 
    global g_detail_used

    log_debug("=====[%s, %s]=====", _stock_id, _a_date)

    # 获取明细数据
    # 之前n1单位的交易数据
    n1 = g_detail_fetched
    detail_df = get_ducka_detail(_stock_id, _a_date, n1, _db);
    if detail_df is None:
        log_info("[%s, %s] detail is none", _stock_id, _a_date)
        return -1
    elif detail_df.empty:
        log_debug("detail_df is empty: [%d]", len(detail_df))
        return 1
    else:
        # log_debug("n1: len[%d]", len(detail_df))
        pass

    length = len(detail_df)
    if length < g_detail_used:
        log_info("data-not-enough: %s: %d", _stock_id, length)
        return 1

    # 格式化数据
    rv = ducka_format_ref(_stock_id, detail_df)
    if rv < 0:
        log_error("error: ducka_format_ref: %s", _stock_id)
        return -1

    used_len = g_detail_used
    my_df = detail_df.head(used_len)

    rv = ducka_analyzer(_stock_id, _k_date, _a_date, _b_date, _c_date, _d_date, _e_date, my_df, used_len, _db)
    if rv == 0:
        log_info("nice1: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    log_debug("-------------------------------------------------")

    return 1


#
# A点往前存在cross4、3
# 
#
def ducka_has_cross(_detail_df, _used_len, _date, _n1, _db):

    days = 0
    to_count = False

    cross4 = False
    cross3 = False

    last_close = 0

    idx = 0
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx
        pub_date         = row['pub_date']
        close_price      = row['close_price']
        open_price       = row['open_price']
        # log_debug("pub_date: [%s]", pub_date)

        if str(_date) == str(pub_date):
            to_count = True

        if to_count:
            days = days + 1

            rule4 =  close_price > ref_ma5(TECH_IDX) and \
                close_price > ref_ma10(TECH_IDX) and \
                close_price > ref_ma20(TECH_IDX) and \
                close_price > ref_ma30(TECH_IDX) and \
                open_price  < ref_ma5(TECH_IDX) and \
                open_price  < ref_ma10(TECH_IDX) and \
                open_price  < ref_ma20(TECH_IDX) and \
                open_price  < ref_ma30(TECH_IDX)

            rule42 = last_close > ref_ma5(TECH_IDX) and \
                last_close > ref_ma10(TECH_IDX) and \
                last_close > ref_ma20(TECH_IDX) and \
                last_close > ref_ma30(TECH_IDX) and \
                open_price < ref_ma5(TECH_IDX) and \
                open_price < ref_ma10(TECH_IDX) and \
                open_price < ref_ma20(TECH_IDX) and \
                open_price < ref_ma30(TECH_IDX)

            rule3 =  close_price > ref_ma5(TECH_IDX) and \
                close_price > ref_ma10(TECH_IDX) and \
                close_price > ref_ma20(TECH_IDX) and \
                open_price  < ref_ma5(TECH_IDX) and \
                open_price  < ref_ma10(TECH_IDX) and \
                open_price  < ref_ma20(TECH_IDX)

            rule32 = last_close > ref_ma5(TECH_IDX) and \
                last_close > ref_ma10(TECH_IDX) and \
                last_close > ref_ma20(TECH_IDX) and \
                open_price < ref_ma5(TECH_IDX) and \
                open_price < ref_ma10(TECH_IDX) and \
                open_price < ref_ma20(TECH_IDX)

            if rule4 or rule42:
                cross4 = True
                # log_info("%s: good had cross4: %s, %s", pub_date, rule4, rule42)

            if rule3 or rule32:
                cross3 = True
                # log_info("%s: good had cross3: %s, %s", pub_date, rule3, rule32)

        if days > _n1:
            break


        last_close = close_price
        idx = idx + 1

    return cross4, cross3


# B点往前
# 缩量天数
# B点往前_n1单位, 统计_n2单位缩量最大天数
def ducka_shrink_days(_detail_df, _used_len, _date, _n1, _n2, _db):

    idx = 0
    TECH_IDX = 0

    max_days = 0
    max_date = ""

    start_idx2 = 0
    end_idx2   = 0

    for row_index, row in _detail_df.iterrows():
        pub_date         = row['pub_date']

        if str(_date) == str(pub_date):
            break

        idx  = idx + 1

    # log_info("date[%s] => idx[%d]", _date, idx)
    start_idx = idx
    end_idx   = idx + _n1
    # log_info("start:[%d] => end[%d]", start_idx, end_idx)

    if start_idx < 0 or end_idx > len(_detail_df):
        log_error("error: exceeds: %d, %d", start_idx, end_idx)
        return -1, -1

    s1 = _detail_df['total']
    # log_debug("series-full: %s", s1)

    idx = 0
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx
        close_price      = row['close_price']
        vol              = row['total']
        pub_date         = row['pub_date']
        last_close_price = row['last']
        rate = (close_price - last_close_price) / last_close_price * 100

        if idx >= start_idx and idx < end_idx:
            start_idx2 = idx
            end_idx2   = idx + _n2
            # log_debug("[%d, %d]", start_idx2, end_idx2)
            if start_idx2 < 0 or end_idx2 > len(_detail_df):
                idx = idx + 1
                continue
            s2 = s1[start_idx2: end_idx2]
            # log_debug("series-this:\n%s", s2)
            rownum = 0
            days = 0
            for s_index, s_val in s2.iteritems():
                TECH_IDX = start_idx2 + rownum
                rownum = rownum + 1
                # log_debug("[%s]: vol[%.2f], ma10[%.2f]", s_index, s_val, ref_vma10(TECH_IDX))
                if s_val < ref_vma10(TECH_IDX) and s_val < ref_vma50(TECH_IDX):
                    days += 1

            # log_debug("[%s] below days: [%d]", pub_date, days)
            if days > max_days:
                max_days = days
                max_date = pub_date
        else:
            pass

        idx  = idx + 1
    # for

    # log_debug("[%s]: %.2f, %.2f, %d", min_date, min_std, min_mean, min_idx)

    return max_days, max_date


# C点往前
# 放量天数
# B点往前_n1单位, 统计_n2单位放量最大天数
def ducka_magnify_days(_detail_df, _used_len, _date, _n1, _n2, _db):

    idx = 0
    TECH_IDX = 0

    max_days = 0
    max_date = ""

    start_idx2 = 0
    end_idx2   = 0

    for row_index, row in _detail_df.iterrows():
        pub_date         = row['pub_date']

        if str(_date) == str(pub_date):
            break

        idx  = idx + 1

    # log_info("date[%s] => idx[%d]", _date, idx)
    start_idx = idx
    end_idx   = idx + _n1
    # log_info("start:[%d] => end[%d]", start_idx, end_idx)

    if start_idx < 0 or end_idx > len(_detail_df):
        log_error("error: exceeds: %d, %d", start_idx, end_idx)
        return -1, -1

    s1 = _detail_df['total']
    # log_debug("series-full: %s", s1)

    idx = 0
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx
        close_price      = row['close_price']
        vol              = row['total']
        pub_date         = row['pub_date']
        last_close_price = row['last']
        rate = (close_price - last_close_price) / last_close_price * 100

        if idx >= start_idx and idx < end_idx:
            start_idx2 = idx
            end_idx2   = idx + _n2
            # log_debug("[%d, %d]", start_idx2, end_idx2)
            if start_idx2 < 0 or end_idx2 > len(_detail_df):
                idx = idx + 1
                continue
            s2 = s1[start_idx2: end_idx2]
            # log_debug("series-this:\n%s", s2)
            rownum = 0
            days = 0
            for s_index, s_val in s2.iteritems():
                TECH_IDX = start_idx2 + rownum
                rownum = rownum + 1
                # log_debug("[%s]: vol[%.2f], ma10[%.2f]", s_index, s_val, ref_vma10(TECH_IDX))
                if s_val > ref_vma10(TECH_IDX) and s_val > ref_vma50(TECH_IDX):
                    days += 1

            # log_debug("[%s] below days: [%d]", pub_date, days)
            if days > max_days:
                max_days = days
                max_date = pub_date
        else:
            pass

        idx  = idx + 1
    # for

    # log_debug("[%s]: %.2f, %.2f, %d", min_date, min_std, min_mean, min_idx)

    return max_days, max_date


#
# D point
# D点往后 low > ma60
#
def ducka_beyond_ma60(_detail_df, _used_len, _date, _db):
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
        low_price        = row['low_price']

        last_close_price = row['last']
        open_price       = row['open_price']
        vol              = row['total']

        if str(_date) == str(pub_date):
            break

        if low_price < ref_ma60(TECH_IDX):
            log_info("[%s] below ma60: [%.2f < %.2f]", pub_date, low_price, ref_ma60(TECH_IDX))
            return False, idx

        idx  = idx + 1

    return True, idx


# 
# A点往前突破天数
# 最高价
#
def ducka_break_days(_detail_df, _used_len, _date, _my_high, _db):

    days = 0
    last_date = ""
    to_count = False

    for row_index, row in _detail_df.iterrows():
        pub_date         = row['pub_date']
        close_price      = row['close_price']
        high_price       = row['high_price']
        # log_debug("pub_date: [%s]", pub_date)

        if to_count:
            days = days + 1

        if high_price > _my_high:
            last_date = pub_date
            break

        if str(_date) == str(pub_date):
            to_count = True

    return days, last_date


#
# A点往前突破天数
# 收盘价
#
def ducka_break_days2(_detail_df, _used_len, _date, _my_high, _db):

    days = 0
    last_date = ""
    to_count = False

    for row_index, row in _detail_df.iterrows():
        pub_date         = row['pub_date']
        close_price      = row['close_price']
        high_price       = row['high_price']
        # log_debug("pub_date: [%s]", pub_date)

        if to_count:
            days = days + 1

        if close_price > _my_high:
            last_date = pub_date
            break

        if str(_date) == str(pub_date):
            to_count = True

    return days, last_date


# 
# A点往前突破天数
# 成交量
#
def ducka_vol_break_days(_detail_df, _used_len, _date, _my_high, _db):

    days = 0
    last_date = ""
    to_count = False

    for row_index, row in _detail_df.iterrows():
        pub_date         = row['pub_date']
        vol              = row['total']
        # log_debug("pub_date: [%s]", pub_date)

        if to_count:
            days = days + 1

        if vol > _my_high:
            last_date = pub_date
            break

        if str(_date) == str(pub_date):
            to_count = True

    return days, last_date


#
# case1:
# C point
# E点往前C1单位起始，C2单位内的最高high价
#
# case2:
# A point
# C点往前A1单位起始，A2单位内的最高high价
#
def ducka_preceding_high(_detail_df, _used_len, _date, _n1, _n2, _db):
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
                if high_price > max_high and close_price > ref_ma20(TECH_IDX):
                    max_high  = high_price
                    high_close= close_price
                    high_date = pub_date
                    high_idx  = idx
                    high_vol  = vol
                    # log_debug("high:[%s.2f, %s]", max_high, high_date)
                    high_rate = (close_price - last_close_price) / last_close_price * 100
                    if ref_vma50(TECH_IDX) > 0:
                        high_vr = (vol / ref_vma50(TECH_IDX) - 1) * 100
                    else:
                        high_vr = 0

        if str(_date) == str(pub_date):
            to_start = True

        idx  = idx + 1

    return max_high, high_close, high_date, high_idx, high_vol, high_rate, high_vr


#
# X点往前x1单位内，阳线最大成交量
# C point
#
#
def ducka_preceding_high_red(_detail_df, _used_len, _date, _n1, _high, _db):
    idx = 0
    days = 0
    to_start = False
    to_count = False

    refined_high = _high * 0.97
    max_vol = 0

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


        if str(_date) == str(pub_date):
            to_start = True

        if to_start:
            days = days + 1
            if days > _n1:
                # log_debug("reach n2: %d", days)
                break
            else:
                # log_debug("[%d, %s]", days, pub_date)
                if high_price > refined_high and close_price > last_close_price and vol > max_vol:
                    max_vol   = vol
                    max_high  = high_price
                    high_close= close_price
                    high_date = pub_date
                    high_idx  = idx
                    high_vol  = vol
                    # log_debug("high:[%s.2f, %s]", max_high, high_date)
                    high_rate = (close_price - last_close_price) / last_close_price * 100
                    if ref_vma50(TECH_IDX) > 0:
                        high_vr = (vol / ref_vma50(TECH_IDX) - 1) * 100
                    else:
                        high_vr = 0


        idx  = idx + 1

    return max_high, high_close, high_date, high_idx, high_vol, high_rate, high_vr


# X点往前
# RPV
# avg(+rate*vol)  / avg(-rate*vol)
def ducka_rpv(_detail_df, _used_len, _till, _n, _db):
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

#
# D point
# C点和E点之间最低点
#
# B point
# A点和C点之间最低点
#
# date1 < date2
#
def ducka_between_low(_detail_df, _used_len, _date1, date2, _db):
    idx = 0
    days = 0
    high_date = ""
    to_start = False
    to_count = False
    min_low = 1000.0

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

        # exceed left-min
        if str(_date1) > str(pub_date):
            # log_debug("small_date: %s < %s, break", pub_date, _date1)
            break
        elif str(pub_date) > str(_date1) and str(pub_date) < str(date2):
            if low_price < min_low:
                min_low = low_price
                low_date = pub_date
                low_idx  = idx
                low_vol  = vol
                # log_debug("low:[%s.2f, %s]", min_low, low_date)
                low_rate = (close_price - last_close_price) / last_close_price * 100
                if ref_vma50(TECH_IDX) > 0:
                    low_vr = (vol / ref_vma50(TECH_IDX) - 1) * 100
                else:
                    low_vr = 0
        else:
            # log_debug("big_date: %s > %s", pub_date, date2)
            pass

        idx  = idx + 1

    return min_low, low_date, low_idx, low_vol, low_rate, low_vr

#
# A点附近的最大成交量
#
def ducka_max_vol(_detail_df, _used_len, _date, _n1, _n2, _db):

    idx = 0
    TECH_IDX = 0
    for row_index, row in _detail_df.iterrows():
        pub_date = row['pub_date']

        if str(_date) == str(pub_date):
            break

        idx  = idx + 1

    # log_info("date[%s] => idx[%d]", _date, idx)
    start_idx = idx - _n2
    end_idx   = idx + _n1
    # log_info("start:[%d] => end[%d]", start_idx, end_idx)

    if start_idx < 0 or end_idx > len(_detail_df):
        log_error("error: exceeds: %d, %d", start_idx, end_idx)
        return -1, -1, -1

    idx = 0
    max_vol = 0.0
    rel_vr  = 0.0
    rel_rt  = 0.0
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx
        close_price      = row['close_price']
        high_price       = row['high_price']
        vol              = row['total']
        pub_date         = row['pub_date']
        last_close_price = row['last']
        rate = (close_price - last_close_price) / last_close_price * 100
        rate2= (high_price - last_close_price) / last_close_price * 100

        if idx >= start_idx and idx <= end_idx:
            # log_debug("[%s]: [%d, %d, %d]: [%.2f, %.2f]", pub_date, idx, start_idx, end_idx, vol, ref_vma50(TECH_IDX))
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


# B点往前
# 方差最小时的平均值
# C-frame
def ducka_devia(_detail_df, _used_len, _date, _n1, _n2, _db):

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
    start_idx = idx
    end_idx   = idx + _n1
    # log_info("start:[%d] => end[%d]", start_idx, end_idx)

    if start_idx < 0 or end_idx > len(_detail_df):
        log_error("error: exceeds: %d, %d", start_idx, end_idx)
        return -1, -1, -1, -1

    s1 = _detail_df['low_price']
    # log_debug("series: %s", s1)

    idx = 0
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx
        close_price      = row['close_price']
        vol              = row['total']
        pub_date         = row['pub_date']
        last_close_price = row['last']
        rate = (close_price - last_close_price) / last_close_price * 100

        if idx >= start_idx and idx < end_idx:
            start_idx2 = idx - _n2
            end_idx2   = idx + _n2
            # log_debug("[%d, %d]", start_idx2, end_idx2)
            if start_idx2 < 0 or end_idx2 > len(_detail_df):
                idx = idx + 1
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


# A点附近平均值
# A-frame
def ducka_mean(_detail_df, _used_len, _date, _n1, _n2, _db):

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


#
# K point
# A点往前k1单位起始，k2单位内的最低low价
#
def ducka_preceding_low(_detail_df, _used_len, _date, _n1, _n2, _db):
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
                    if ref_vma50(TECH_IDX) > 0:
                        low_vr = (vol / ref_vma50(TECH_IDX) - 1) * 100
                    else:
                        low_vr = 0

        if str(_date) == str(pub_date):
            to_start = True

        idx  = idx + 1

    return min_low, low_close, low_date, low_idx, low_vol, low_rate, low_vr



def ducka_dynamic_calc_tech(_df):

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


def ducka_format_ref(_stock_id, _detail_df):

    # _detail MUST be sorted
    rv = ref_init4(_detail_df)
    if rv < 0:
        log_error("error: ref_init4")
        return -1

    _detail_df.sort_index(ascending=False, inplace=True)
    ducka_dynamic_calc_tech(_detail_df)
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



def get_ducka_detail(_stock_id, _pub_date, _n, _db):
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


def get_ducka_stock_list(_till, _db):
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


def regression(_db):

    return 0


def work():
    db = db_init()


    # 西部建设 bingo
    stock_id  = "002302"
    A_date = "2017-03-20"
    B_date = "2017-03-17"
    C_date = "2017-03-10"
    D_date = "2017-02-10"
    E_date = "2017-01-20"
    K_date = "2017-01-09"
    ducka_work_one_day_stock(stock_id, K_date, A_date, B_date, C_date, D_date, E_date, db)


    db_end(db)


#######################################################################

def main():
    sailog_set("ducka0.log")

    log_info("let's begin here!")

    work()

    log_info("main ends, bye!")

    return

#######################################################################

main()

#######################################################################

# ducka.py
