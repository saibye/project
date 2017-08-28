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

from pub_duck import *


# 2017-8-28

#
# 002302
#
def duck_analyzer1(_stock_id, _trade_date, _my_df, _used_len, _db):
    global g_detail_fetched 

    lowest   = 0
    mailed = 0
    content1 = "Cup with Handle\n"
    to_mail = False

    idx    = 0
    TECH_IDX = 0

    # A: 今日！ 突破点
    p_A = 0
    v_A = 0
    i_A = -1
    d_A = ""
    rt_A = 0
    vr_A = 0

    # B: 穿越日
    p_B = 1000
    v_B = 0
    i_B = -1
    d_B = ""
    rt_B = 0
    vr_B = 0

    # C: 缩量横盘
    p_C = 0
    v_C = 0
    i_C = -1
    d_C = ""
    rt_C = 0
    vr_C = 0

    # D: 最高点
    p_D = 1000
    v_D = 0
    i_D = -1
    d_D = ""
    rt_D = 0
    vr_D = 0

    # E: 一路上扬
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

    got_A = False
    got_B = False
    got_C = False
    got_D = False
    got_E = False

    AB = 0 # A到B天数
    BC = 0 # B到C天数
    CD = 0 # C到D天数

    to_get_A = True
    to_get_B = False
    to_get_C = False
    to_get_D = False
    to_get_E = False
    to_get_K = False

    # A点指标
    A_VR   = 100
    A_RATE = 8
    A_DAYS1 = 80
    A_DAYS2 = 20
    AA_DAYS3 = 4 # before
    AA_DAYS4 = 0 # after
    LEN_AC_MIN = 25
    LEN_AC_MAX = 70
    RATE_AE_MIN = -8.0
    RATE_AE_MAX = 5

    # E点指标
    E_RATE = 4.5
    E_RATE2= 5
    E_VR   = 130
    E_DAYS = 50

    # C点指标
    C_VR   = 40
    C_DAYS1 = 3
    C_DAYS2 = 13
    C_DAYS3 = 8
    C_RPV   = 2
    LEN_CE_MIN = 4
    LEN_CE_MAX = 16
    RATE_EC_MAX = 5 # 5%
    RATE_EC_MAX2= 12

    # D点指标
    LEN_CD_MIN = 2
    RATE_ED_MIN = 8  # n%
    RATE_ED_MAX = 16 # n%
    RATE_ED_MAX2= 32 # n%


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

        # 寻找A点：阳柱+上涨+放量+突破+macd
        if to_get_A:
            log_debug("to-get A-point: rate: %.2f%%, %.2f%% vr:%.2f", rate, rate2, vr)
            if vr > A_VR and rate > A_RATE:
                d_A = pub_date
                v_A = vol
                p_A = close_price
                h_A = high_price
                i_A = idx
                rt_A= rate
                vr_A= vr

                # MACD:
                macd_A = ref_macd(TECH_IDX)
                diff_A = ref_diff(TECH_IDX)
                dea_A  = ref_dea(TECH_IDX)
                macd_AA= ref_macd(TECH_IDX+3) 
                log_debug("macd: %.3f, diff: %.3f, dea: %.3f, prev: %.3f", macd_A, diff_A, dea_A, macd_AA)

                if macd_A > 0 and diff_A > 0 and dea_A > 0 and macd_AA < 0:
                    log_info("nice: A点MACD满足: %.3f, %.3f, %.3f", macd_A, diff_A, dea_A)
                else:
                    log_debug("nice: A点MACD不满足: %.3f, %.3f, %.3f", macd_A, diff_A, dea_A)
                    return 1

                # 收盘价突破天数
                A_break_days, A_block_date = duck_break_days2(_my_df, _used_len, d_A, h_A, _db)
                log_debug("A-break: %d, block: %s", A_break_days, A_block_date)
                if A_break_days > A_DAYS1:
                    log_info("nice: A点即将确认: 突破:%d, 阻塞:%s", A_break_days, A_block_date)
                else:
                    return 1

                # 成交量突破天数
                A_vol_break_days, A_vol_block_date = duck_vol_break_days(_my_df, _used_len, d_A, v_A, _db)
                log_debug("A-vol-break: %d, vol-block: %s", A_vol_break_days, A_vol_block_date)
                if A_vol_break_days > A_DAYS2:
                    log_info("nice: A点确认: vol-突破:%d, 阻塞:%s", A_vol_break_days, A_vol_block_date)
                    to_get_A = False
                    to_get_B = True
                    got_A = True
                else:
                    return 1


        return 0

        # 寻找C点： E点往前n1单位开始，n2单位内的最高点
        if to_get_C:
            log_debug("to-get C-point")
            h_C, p_C, d_C, i_C, v_C, rt_C, vr_C = duck_preceding_high(_my_df, _used_len, d_E, C_DAYS1, C_DAYS2, _db)
            log_info("trying: C点: %s, %.2f%%, +%.2f%%", d_C, rt_C, vr_C)
            if h_C < 1: 
                log_info("sorry: C not high: %.2f", h_C)
                return 1

            h_C, p_C, d_C, i_C, v_C, rt_C, vr_C = duck_preceding_high_red(_my_df, _used_len, d_C, 12, h_C, _db)
            log_info("trying: C点2: %s, %.2f%%, +%.2f%%", d_C, rt_C, vr_C)
            if h_C < 1: 
                log_info("sorry: C2 not high: %.2f", h_C)
                return 1

            rate_EC = (p_E / p_C - 1) * 100.00
            len_CE  = i_C - i_E
            log_info("rate-EC: %.2f%%, len-CE: %d", rate_EC, len_CE)


            C_rule1=  vr_C > C_VR and rate_EC > -0.5 and rate_EC < RATE_EC_MAX \
                      and len_CE >= LEN_CE_MIN and len_CE < LEN_CE_MAX
            if C_rule1:
                log_info("C to check RPV")
                # RPV-rt
                rpv_C   = duck_rpv(_my_df, _used_len, d_C, C_DAYS3, _db)
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
            l_D, d_D, i_D, v_D, rt_D, vr_D = duck_between_low(_my_df, _used_len, d_C, d_E, _db)
            log_info("trying: D点: %s, %.2f, %d, %.2f, %.2f%%, +%.2f%%",
                    d_D, l_D, i_D, v_D, rt_D, vr_D)
            rate_ED = (h_E / l_D - 1) * 100.00
            len_CD  = i_C - i_D
            log_info("rate-ED: %.2f%%, len-CD: %d", rate_ED, len_CD)

            D_rule1 = rate_ED > RATE_ED_MIN and rate_ED < RATE_ED_MAX and len_CD >= LEN_CD_MIN

            if D_rule1:
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
            h_A, p_A, d_A, i_A, v_A, rt_A, vr_A = duck_preceding_high(_my_df, _used_len, d_C, A_DAYS1, A_DAYS2, _db)
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
            rpv_A   = duck_rpv(_my_df, _used_len, d_A, A_DAYS3, _db)
            log_info("rpv-A: %.2f", rpv_A)

            # A点附近最大量比
            AA_vol, AA_vr, AA_rt, AA_rt2 = duck_max_vol(_my_df, _used_len, d_A, AA_DAYS3, AA_DAYS4, _db)
            log_info("A点附近：最大量比: +%.2f, 涨幅: %.2f%%, high: %.2f%%", AA_vr, AA_rt, AA_rt2)

            # E点突破天数
            if E_break_days >= 70 and AA_vr > 20 and AA_rt > 0:
                log_info("nice: A点即将确认1: max-vr: %.2f, len-AC: %d, rate-AE: %.2f", AA_vr, len_AC, rate_AE)
                to_get_A = False
                to_get_B = True
                # warn: not make: got_A
            elif E_break_days >= 50 and AA_vr > 100 and AA_rt > 0:
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
            l_B, d_B, i_B, v_B, rt_B, vr_B = duck_between_low(_my_df, _used_len, d_A, d_C, _db)
            log_info("try: B点: %s, %.2f, %d, %.2f, %.2f%%, vr:%.2f%%",
                    d_B, l_B, i_B, v_B, rt_B, vr_B)
            rate_AB = (h_A / l_B - 1) * 100.00
            len_AB  = i_A - i_B
            log_info("rate-AB: %.2f%%, len-AB: %d", rate_AB, len_AB)

            if rate_AB > 10 and rate_AB < 46 and len_AB >= 10:
                log_info("nice: 即将B点确认: %s, rate-AB:%.2f, len:%d", d_B, rate_AB, len_AB)
            else:
                log_debug("B-point not match")
                return 1

            # B点方差最小的平均值
            B3 = 10
            B4 = 5
            B_mean, B_std, B_rel_date, B_rel_idx = duck_devia(_my_df, _used_len, d_B, B3, B4, _db)
            log_info("B点附近[%d]长度[%d]平均值: %.2f, 标准差: %.2f [%s]",
                    B3, B4, B_mean, B_std, B_rel_date)

            if B_mean <= 0:
                log_debug("warn: B-point mean zero")
                return 1

            # A点平均值
            A_mean = duck_mean(_my_df, _used_len, d_A, 1, 1, _db)
            log_info("A点附近[1]长度平均值: %.2f", A_mean)

            rate_ABM = (A_mean / B_mean - 1) * 100.00
            rate_SB = (B_mean / l_B - 1) * 100.00
            log_info("rate-ABM: %.2f%%, rate-SB: %.2f%%", rate_ABM, rate_SB)

            if B_std <= 0.20 and rate_ABM < 32 and rate_ABM > 5:
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
            h_K, p_K, d_K, i_K, v_K, rt_K, vr_K = duck_preceding_low(_my_df, _used_len, d_A, K_DAYS1, K_DAYS2, _db)
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
        content1 += "A点: RPV: %.2f\n" % (rpv_A)
        content1 += "C点: RPV: %.2f\n" % (rpv_C)
        content1 += "+++++++++++++++++++++++++\n"
        info  = get_basic_info_all(_stock_id, _db)
        content1 += info
        # log_info("mail:\n%s", content1)
        to_mail = True


    if to_mail:
        subject = "CwH5（weak）: %s -- %s" % (_stock_id, _trade_date)
        log_info(subject)
        log_info("mail:\n%s", content1)
        if sai_is_product_mode():
            mailed = 1
            # saimail_dev(subject, content1)
            return 0
    else:
        # log_info("sorry: %s, %s", _stock_id, _trade_date)
        pass

    return 1


