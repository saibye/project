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


def CupWithHandle_analyzer(_stock_id, _trade_date, _my_df, _used_len, _db):
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

    to_get_E = True
    to_get_D = False
    to_get_C = False
    to_get_B = False
    to_get_A = False
    to_get_K = False

    # E点指标
    E_RATE = 5
    E_RATE2= 5
    E_VR   = 130
    E_DAYS = 40

    # C点指标
    C_VR   = 40
    C_DAYS1 = 3
    C_DAYS2 = 10
    C_DAYS2 = 13 #new
    C_DAYS3 = 8
    C_RPV   = 2
    LEN_CE_MIN = 4
    LEN_CE_MAX = 8
    LEN_CE_MAX = 16 # new
    RATE_EC_MAX = 5 # 5%

    # D点指标
    LEN_CD_MIN = 3
    RATE_ED_MIN = 9  # 9%
    RATE_ED_MAX = 15 # 4%

    # A点指标
    A_VR   = 0 # XXX
    A_DAYS1 = 5
    A_DAYS2 = 40
    A_DAYS2 = 80
    AA_DAYS3 = 4 # before
    AA_DAYS4 = 0 # after
    LEN_AC_MIN = 25
    LEN_AC_MAX = 70
    RATE_AE_MIN = -7.0
    RATE_AE_MAX = 5

    # B点指标

    # A点指标
    K_DAYS1 = 3
    K_DAYS2 = 10


    for row_index, row in _my_df.iterrows():
        TECH_IDX = idx

        close_price      = row['close_price']
        high_price       = row['high_price']
        last_close_price = row['last']
        open_price       = row['open_price']
        vol              = row['total']
        pub_date         = row['pub_date']

        # 涨幅
        rate = (close_price - last_close_price) / last_close_price * 100
        rate2= (high_price - last_close_price) / last_close_price * 100

        # 柱体
        zt   = (close_price - open_price) / last_close_price * 100

        # 量比 vol/ma50
        if ref_vma50(TECH_IDX) > 0:
            vr = (vol / ref_vma50(TECH_IDX) - 1) * 100
        else:
            vr = 0


        if vol > v_max:
            v_max  = vol
            c_vmax = close_price

        if close_price > c_max:
            c_max = close_price
            i_max = idx

        if close_price < c_min:
            c_min = close_price
            i_min = idx

        # 寻找E点：阳柱+上涨
        if to_get_E:
            log_debug("to-get E-point: rate: %.2f%%, %.2f%% vr:%.2f", rate, rate2, vr)
            if vr > E_VR and (rate > E_RATE or rate2 > E_RATE2):
                d_E = pub_date
                v_E = vol
                p_E = close_price
                h_E = high_price
                i_E = idx
                rt_E= rate
                vr_E= vr
                E_break_days, E_block_date = CupWithHandle_break_days(_my_df, _used_len, d_E, h_E, _db)
                log_debug("E-break: %d, block: %s", E_break_days, E_block_date)
                if E_break_days > E_DAYS:
                    log_info("nice: E点确认: 突破:%d, 阻塞:%s", E_break_days, E_block_date)
                    to_get_E = False
                    to_get_C = True
                    got_E = True
                else:
                    return 1

        # 寻找C点： E点往前n1单位开始，n2单位内的最高点
        if to_get_C:
            log_debug("to-get C-point")
            h_C, p_C, d_C, i_C, v_C, rt_C, vr_C = CupWithHandle_preceding_high(_my_df, _used_len, d_E, C_DAYS1, C_DAYS2, _db)
            log_info("trying: C点: %s, %.2f%%, +%.2f%%", d_C, rt_C, vr_C)
            if h_C < 1: 
                log_info("sorry: C not high: %.2f", h_C)
                return 1
            rate_EC = (h_E / h_C - 1) * 100.00
            len_CE  = i_C - i_E
            log_info("rate-EC: %.2f%%, len-CE: %d", rate_EC, len_CE)
            if vr_C > C_VR and rate_EC > 0 and rate_EC < RATE_EC_MAX and len_CE >= LEN_CE_MIN and len_CE < LEN_CE_MAX:
                log_info("C to check RPV")
                # RPV-rt
                rpv_C   = CupWithHandle_rpv(_my_df, _used_len, d_C, C_DAYS3, _db)
                log_info("rpv-C: %.2f", rpv_C)
                # if rpv_C > 2:
                if rpv_C > 1.9:
                    log_info("nice: C点即将确认: rate-EC:%.2f, len:%d, rpv:%.2f", rate_EC, len_CE, rpv_C)
                    to_get_C = False
                    to_get_D = True
                    # warn: not make: got_C
                else:
                    log_debug("RPV不足: %.2f", rpv_C)
                    return 1
            else:
                log_debug("C-point not match")
                return 1

        # 寻找D点： C/E之间的最低点
        if to_get_D:
            log_debug("to-get D-point")
            l_D, d_D, i_D, v_D, rt_D, vr_D = CupWithHandle_between_low(_my_df, _used_len, d_C, d_E, _db)
            log_info("trying: D点: %s, %.2f, %d, %.2f, %.2f%%, +%.2f%%",
                    d_D, l_D, i_D, v_D, rt_D, vr_D)
            rate_ED = (h_E / l_D - 1) * 100.00
            len_CD  = i_C - i_D
            log_info("rate-ED: %.2f%%, len-CD: %d", rate_ED, len_CD)

            if rate_ED > RATE_ED_MIN and rate_ED < RATE_ED_MAX and len_CD >= LEN_CD_MIN:
                # TODO: get rpv(D) ?
                log_info("nice: D点确认: %s, rate-ED:%.2f, len-CD:%d", d_D, rate_ED, len_CD)
                log_info("nice: C点确认: %s", d_C)
                to_get_A = True
                to_get_C = False
                to_get_D = False
                got_C    = True
                got_D    = True
            else:
                log_debug("D-point not match")
                return 1

        # 寻找A点： C点往前5单位开始，40单位内的最高点
        if to_get_A:
            log_debug("to-get A-point")
            h_A, p_A, d_A, i_A, v_A, rt_A, vr_A = CupWithHandle_preceding_high(_my_df, _used_len, d_C, A_DAYS1, A_DAYS2, _db)
            log_info("try: A点: %s, %.2f, %d, %.2f, %.2f%%, +%.2f%%",
                    d_A, h_A, i_A, v_A, rt_A, vr_A)
            if h_A < 1: 
                log_info("sorry: A not high: %.2f", h_A)
                return 1
            rate_AE = (h_A / h_E - 1) * 100.00
            len_AC  = i_A - i_C
            log_info("rate-AE: %.2f%%, len-AC: %d", rate_AE, len_AC)

            # check AE rate
            if rate_AE < RATE_AE_MIN or rate_AE > RATE_AE_MAX:
                log_debug("sorry: A-point: rate-AE exceed: %.2f%%", rate_AE)
                return 1

            # check AC length
            if len_AC < LEN_AC_MIN or len_AC > LEN_AC_MAX:
                log_debug("sorry: A-point: len-AC exceed: %d", len_AC)
                return 1

            # RPV-rt
            A_DAYS3 = 8
            rpv_A   = CupWithHandle_rpv(_my_df, _used_len, d_A, A_DAYS3, _db)
            log_info("rpv-A: %.2f", rpv_A)

            # A点附近最大量比
            AA_vol, AA_vr, AA_rt, AA_rt2 = CupWithHandle_max_vol(_my_df, _used_len, d_A, AA_DAYS3, AA_DAYS4, _db)
            log_info("A点附近：最大量比: +%.2f, 涨幅: %.2f%%, high: %.2f%%", AA_vr, AA_rt, AA_rt2)

            # E点突破天数
            if E_break_days >= 70:
                if AA_vr > 50 and AA_rt > 0.5:
                    log_info("nice: A点即将确认1: max-vr: %.2f, len-AC: %d, rate-AE: %.2f", AA_vr, len_AC, rate_AE)
                    to_get_A = False
                    to_get_B = True
                    # warn: not make: got_A
                else:
                    log_debug("A点附近vr不满足: +%.2f, %.2f", AA_vr, AA_rt)
                    return 1
            else:
                if AA_vr > 200 and max(AA_rt, AA_rt2) > 6.0:
                    log_info("nice: A点即将确认2: max-vr: %.2f, len-AC: %d, rate-AE: %.2f", AA_vr, len_AC, rate_AE)
                    to_get_A = False
                    to_get_B = True
                    # warn: not make: got_A
                else:
                    log_debug("A点附近vr不满足: +%.2f, %.2f", AA_vr, AA_rt)
                    return 1

        # 寻找B点： A/C之间的最低点
        if to_get_B:
            log_debug("searching B-point: %.2f, %.2f", rate, vr)
            l_B, d_B, i_B, v_B, rt_B, vr_B = CupWithHandle_between_low(_my_df, _used_len, d_A, d_C, _db)
            log_info("try: B点: %s, %.2f, %d, %.2f, %.2f%%, vr:%.2f%%",
                    d_B, l_B, i_B, v_B, rt_B, vr_B)
            rate_AB = (h_A / l_B - 1) * 100.00
            len_AB  = i_A - i_B
            log_info("rate-AB: %.2f%%, len-AB: %d", rate_AB, len_AB)

            if rate_AB > 15 and rate_AB < 45 and len_AB >= 10:
                log_info("nice: 即将B点确认: %s, rate-AB:%.2f, len:%d", d_B, rate_AB, len_AB)
            else:
                log_debug("B-point not match")
                return 1

            # B点方差最小的平均值
            B3 = 10
            B4 = 5
            B_mean, B_std, B_rel_date, B_rel_idx = CupWithHandle_devia(_my_df, _used_len, d_B, B3, B4, _db)
            log_info("B点附近[%d]长度[%d]平均值: %.2f, 标准差: %.2f [%s]",
                    B3, B4, B_mean, B_std, B_rel_date)

            # A点平均值
            A_mean = CupWithHandle_mean(_my_df, _used_len, d_A, 1, 1, _db)
            log_info("A点附近[1]长度平均值: %.2f", A_mean)

            rate_ABM = (A_mean / B_mean - 1) * 100.00
            rate_SB = (B_mean / l_B - 1) * 100.00
            log_info("rate-AS: %.2f%%, rate-SB: %.2f%%", rate_ABM, rate_SB)

            if B_std <= 0.42 and rate_ABM < 24 and rate_ABM > 10:
                log_info("nice: B点确认: %s, 方差: %.2f, rate-ABM: %.2f", d_B, B_std, rate_ABM)
                to_get_K = True
                to_get_B = False
                got_B    = True
            else:
                log_debug("B-point not match final")
                return 1


        # 寻找K点： A点往前n1单位开始，n2单位内的最低点
        if to_get_K:
            log_debug("searching K-point: %.2f, %.2f", rate, vr)
            h_K, p_K, d_K, i_K, v_K, rt_K, vr_K = CupWithHandle_preceding_low(_my_df, _used_len, d_A, K_DAYS1, K_DAYS2, _db)
            log_info("try: K点: %s, %.2f, %d, %.2f, %.2f%%, %.2f%%",
                    d_K, h_K, i_K, v_K, rt_K, vr_K)
            rate_AK = (h_A / h_K - 1) * 100.00
            len_KA  = i_K - i_A
            log_info("rate-AK: %.2f%%, len-KA: %d", rate_AK, len_KA)
            if rate_AK > 6 and len_KA >= 4:
                log_info("nice: A点确认: %s, vr:+%.2f, rate: %.2f%%, %.2f%%",
                        d_A, AA_vr, AA_rt, AA_rt2)
                to_get_K = False
                got_K    = True
                got_A    = True


        idx  = idx + 1

        break

    if got_A:
        log_info("+++++++++++++++++++++++++++++++++++++")
        log_info("bingo: %s break at %s", _stock_id, d_E)
        log_info("K: %s", d_K)
        log_info("A: %s", d_A)
        log_info("B: %s", d_B)
        log_info("C: %s", d_C)
        log_info("D: %s", d_D)
        log_info("E: %s", d_E)
        log_debug("XXX: %s", _stock_id)
        content1 += "%s -- %s\n" % (_stock_id, d_E)
        content1 += "突破: %s, 放量(+): %.2f%%\n"  % (d_E, vr_E)
        content1 += "A点: %s,  放量(+): %.2f%%\n"  % (d_A, vr_A)
        content1 += "B点: %s,  缩量(-): %.2f%%\n"  % (d_B, vr_B)
        content1 += "C点: %s,  放量(+): %.2f%%\n"  % (d_C, vr_C)
        content1 += "D点: %s,  缩量(-): %.2f%%\n"  % (d_D, vr_D)
        content1 += "C点: RPV: %.2f\n" % (rpv_C)
        content1 += "+++++++++++++++++++++++++\n"
        info  = get_basic_info_all(_stock_id, _db)
        content1 += info
        log_info("mail:\n%s", content1)
        to_mail = True


    if to_mail:
        subject = "CwH1: %s -- %s" % (_stock_id, _trade_date)
        log_info(subject)
        log_info("mail:\n%s", content1)
        if sai_is_product_mode():
            mailed = 1
            saimail_dev(subject, content1)
    else:
        log_info("sorry: %s, %s", _stock_id, _trade_date)

    return 0



# E点往前突破天数
#
def CupWithHandle_break_days(_detail_df, _used_len, _date, _my_high, _db):

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
# case1:
# C point
# E点往前C1单位起始，C2单位内的最高high价
#
# case2:
# A point
# C点往前A1单位起始，A2单位内的最高high价
#
def CupWithHandle_preceding_high(_detail_df, _used_len, _date, _n1, _n2, _db):
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
                # log_debug("[%d, %s]", days, pub_date)
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


# X点往前
# RPV
# avg(+rate*vol)  / avg(-rate*vol)
def CupWithHandle_rpv(_detail_df, _used_len, _till, _n, _db):
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
    elif D_sum <= 1:
        rpv_rt = 9.99
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
def CupWithHandle_between_low(_detail_df, _used_len, _date1, date2, _db):
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
        elif str(pub_date) >= str(_date1) and str(pub_date) <= str(date2):
            log_debug
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
def CupWithHandle_max_vol(_detail_df, _used_len, _date, _n1, _n2, _db):

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


# 方差最小时的平均值
# B-frame
def CupWithHandle_devia(_detail_df, _used_len, _date, _n1, _n2, _db):

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
        TECH_IDX = idx
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


# A点附近平均值
# A-frame
def CupWithHandle_mean(_detail_df, _used_len, _date, _n1, _n2, _db):

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
def CupWithHandle_preceding_low(_detail_df, _used_len, _date, _n1, _n2, _db):
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


def sum_CupWithHandle_detail(_detail_df, _days, _db):

    counter = 0
    sum1 = 0.0
    sum2 = 0.0
    for row_index, row in _detail_df.iterrows():
        close_price = row['close_price']
        open_price  = row['open_price']
        vol         = row['total']

        if close_price > open_price:
            # log_debug("<%s> red: %.3f", row_index, vol)
            sum1 += vol
        elif close_price < open_price:
            # log_debug("<%s> gre: %.3f", row_index, vol)
            sum2 += vol
        else:
            pass
        counter = counter + 1
        if counter >= _days:
            # log_debug("counter: reach: %d", _days)
            break

    return sum1, sum2

"""
价格突破前高
"""
def get_CupWithHandle_max_price_days(_detail_df, _max_price):
    counter = 0
    for row_index, row in _detail_df.iterrows():
        if counter == 0:
            counter = 1
            continue

        close_price = row['close_price']
        if close_price <= _max_price:
            counter += 1
            # log_debug("[%s][%.3f] < [%.3f]", row['pub_date'], close_price, _max_price)
        else:
            break
    return counter

"""
价格突破前高 -- 容错
"""
def get_CupWithHandle_almost_max_price_days(_detail_df, _max_price):
    counter = 0
    for row_index, row in _detail_df.iterrows():
        if counter == 0:
            counter = 1
            continue

        close_price = row['close_price']
        if close_price <= _max_price*1.01:
            counter += 1
            # log_debug("[%s][%.3f] < [%.3f]", row['pub_date'], close_price, _max_price)
        else:
            break
    return counter

"""
量突破前高
"""
def get_CupWithHandle_max_volume_days(_detail_df, _max_volume):
    counter = 0
    for row_index, row in _detail_df.iterrows():
        if counter == 0:
            counter = 1
            continue

        volume = row['total']
        if volume < _max_volume:
            counter += 1
            # log_debug("[%s][%.3f] < [%.3f]", row['pub_date'], close_price, _max_price)
        else:
            break
    return counter



def CupWithHandle_dynamic_calc_tech(_df):

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


def CupWithHandle_format_ref(_stock_id, _detail_df):

    # _detail MUST be sorted
    rv = ref_init4(_detail_df)
    if rv < 0:
        log_error("error: ref_init4")
        return -1

    _detail_df.sort_index(ascending=False, inplace=True)
    CupWithHandle_dynamic_calc_tech(_detail_df)
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


def get_CupWithHandle_detail(_stock_id, _pub_date, _n, _db):
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


def get_CupWithHandle_stock_list(_till, _db):
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


def CupWithHandle_work_one_day_stock(_stock_id, _till,  _db):

    global g_detail_fetched 
    global g_detail_used

    log_debug("=====[%s, %s]=====", _stock_id, _till)

    # 获取明细数据
    # 之前n1单位的交易数据
    n1 = g_detail_fetched
    detail_df = get_CupWithHandle_detail(_stock_id, _till, n1, _db);
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
        log_info("data-not-enough: %s: %d", _stock_id, length)
        return 1

    # 格式化数据
    rv = CupWithHandle_format_ref(_stock_id, detail_df)
    if rv < 0:
        log_error("error: CupWithHandle_format_ref: %s", _stock_id)
        return -1

    used_len = g_detail_used
    my_df = detail_df.head(used_len)
    rv = CupWithHandle_analyzer(_stock_id, _till, my_df, used_len, _db)
    if rv < 0:
        log_error("error: CupWithHandle_analyzer1: %s", _stock_id)
        return -1

    return 0


def CupWithHandle_work_one_day(_till_date, _db):

    log_info("date: %s", _till_date)

    list_df = get_CupWithHandle_stock_list(_till_date, _db)
    if list_df is None:
        log_error("error: get_CupWithHandle_stock_list failure")
        return -1
    else:
        # log_debug("list df:\n%s", list_df)
        pass

    begin = get_micro_second()

    for row_index, row in list_df.iterrows():

        stock_id = row_index

        # log_debug("==============================")

        CupWithHandle_work_one_day_stock(stock_id, _till_date, _db)

    log_info("DAY [%s] costs %d us", _till_date, get_micro_second() - begin)

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
    max_date = "2017-07-21"
    days = 30

    log_info("regress")

    date_df = get_recent_pub_date(max_date, days, _db)
    if date_df is None:
        log_error("error: get_recent_pub_date failure")
        return -1
    else:
        date_df.set_index("pub_date", inplace=True)

    for row_index, row in date_df.iterrows():
        till_date = row_index
        log_debug("[%s]------------------", till_date)
        CupWithHandle_work_one_day(till_date, _db)

    return 0


def work():
    db = db_init()

    """
    regression(db)
    return 0
    """

    if sai_is_product_mode():
        till_date = get_date_by(0)
        till_date = get_newest_trade_date(db)
        log_info("till_date: %s", till_date)
        CupWithHandle_work_one_day(till_date, db)

        """
        # 沧州大化 1 done
        till_date = "2017-07-10"
        stock_id  = "600230"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 华资实业 2 done
        till_date = "2017-07-05"
        stock_id  = "600191"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # 敦煌种业 3 done
        till_date = "2017-07-18"
        stock_id  = "600354"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # VAR 中天金融 4 done
        till_date = "2017-07-17"
        stock_id  = "000540"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)

        # VAR 东湖高新 TODO
        till_date = "2017-07-17"
        stock_id  = "600133"
        CupWithHandle_work_one_day_stock(stock_id, till_date, db)
        """


    else:
        regression(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("CupWithHandle0.log")

    log_info("let's begin here!")

    if sai_is_product_mode():
        if today_is_weekend():
            log_info("today is weekend, exit")
            work()
        else:
            log_info("today is workday, come on")
            work()
    else:
        log_debug("test mode")
        work()

    log_info("main ends, bye!")

    return

#######################################################################

main()

#######################################################################

# CupWithHandle.py
