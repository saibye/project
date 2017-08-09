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
from pub_CwH import *


# 2017-8-9
# VAR：A点较高，到B深幅，C反弹不高，E点仅超过C点，可能远离A点
# 

# 601388
def CupWithHandle_analyzer7(_stock_id, _trade_date, _my_df, _used_len, _db):
    global g_detail_fetched 

    lowest   = 0
    mailed = 0
    content1 = "Cup with Handle\n"
    to_mail = False

    idx    = 0
    TECH_IDX = 0

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
    E_RATE = 3.0
    E_RATE2= 5
    E_VR   = 230
    E_DAYS = 50

    # C点指标
    C_VR   = 40
    C_DAYS1 = 3
    C_DAYS2 = 10
    # C_DAYS2 = 13 #new
    C_DAYS3 = 8
    C_RPV   = 2
    LEN_CE_MIN = 4
    LEN_CE_MAX = 14
    # LEN_CE_MAX = 16 # new
    RATE_EC_MAX = 5 # 5%

    # D点指标
    LEN_CD_MIN = 3
    RATE_ED_MIN = 5  # n%
    RATE_ED_MAX = 16 # n%

    # A点指标
    A_VR   = 0 # XXX
    A_DAYS1 = 5
    A_DAYS2 = 65
    AA_DAYS3 = 4 # before
    AA_DAYS4 = 0 # after
    LEN_AC_MIN = 25
    LEN_AC_MAX = 70
    RATE_AE_MIN = -8.0
    RATE_AE_MAX = 11

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
                E_break_days, E_block_date = CupWithHandle_break_days2(_my_df, _used_len, d_E, h_E, _db)
                log_debug("E-break: %d, block: %s", E_break_days, E_block_date)
                if E_break_days > E_DAYS:
                    log_info("nice: E点确认: 突破:%d, 阻塞:%s", E_break_days, E_block_date)
                    to_get_E = False
                    to_get_C = True
                    got_E = True
                else:
                    return 1

                E_vol_break_days, E_vol_block_date = CupWithHandle_vol_break_days(_my_df, _used_len, d_E, v_E, _db)
                log_debug("E-vol-break: %d, vol-block: %s", E_vol_break_days, E_vol_block_date)

        # 寻找C点： E点往前n1单位开始，n2单位内的最高点
        if to_get_C:
            log_debug("to-get C-point")
            h_C, p_C, d_C, i_C, v_C, rt_C, vr_C = CupWithHandle_preceding_high(_my_df, _used_len, d_E, C_DAYS1, C_DAYS2, _db)
            log_info("trying: C点: %s, %.2f%%, +%.2f%%", d_C, rt_C, vr_C)
            if h_C < 1: 
                log_info("sorry: C not high: %.2f", h_C)
                return 1

            h_C, p_C, d_C, i_C, v_C, rt_C, vr_C = CupWithHandle_preceding_high_red(_my_df, _used_len, d_C, 12, h_C, _db)
            log_info("trying: C点2: %s, %.2f%%, +%.2f%%", d_C, rt_C, vr_C)
            if h_C < 1: 
                log_info("sorry: C2 not high: %.2f", h_C)
                return 1

            rate_EC = (p_E / p_C - 1) * 100.00
            len_CE  = i_C - i_E
            log_info("rate-EC: %.2f%%, len-CE: %d", rate_EC, len_CE)


            if vr_C > C_VR and rate_EC > -0.5 and rate_EC < RATE_EC_MAX and len_CE >= LEN_CE_MIN and len_CE < LEN_CE_MAX:
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
                if E_vol_break_days >= 70:
                    log_info("nice: A点即将确认2: max-vr: %.2f, len-AC: %d, rate-AE: %.2f", AA_vr, len_AC, rate_AE)
                    to_get_A = False
                    to_get_B = True
                elif AA_vr > 50 and AA_rt > 0.5:
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

            if rate_AB > 10 and rate_AB < 50 and len_AB >= 10:
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

            if B_mean <= 0:
                log_debug("warn: B-point mean zero")
                return 1

            # A点平均值
            A_mean = CupWithHandle_mean(_my_df, _used_len, d_A, 1, 1, _db)
            log_info("A点附近[1]长度平均值: %.2f", A_mean)

            rate_ABM = (A_mean / B_mean - 1) * 100.00
            rate_SB = (B_mean / l_B - 1) * 100.00
            log_info("rate-AS: %.2f%%, rate-SB: %.2f%%", rate_ABM, rate_SB)

            if B_std <= 0.10 and rate_ABM < 35 and rate_ABM > 5:
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
        content1 += "A点: RPV: %.2f\n" % (rpv_A)
        content1 += "C点: RPV: %.2f\n" % (rpv_C)
        content1 += "+++++++++++++++++++++++++\n"
        info  = get_basic_info_all(_stock_id, _db)
        content1 += info
        # log_info("mail:\n%s", content1)
        to_mail = True


    if to_mail:
        subject = "CwH7: %s -- %s" % (_stock_id, _trade_date)
        log_info(subject)
        log_info("mail:\n%s", content1)
        if sai_is_product_mode():
            mailed = 1
            saimail_dev(subject, content1)
            return 0
    else:
        # log_info("sorry: %s, %s", _stock_id, _trade_date)
        pass

    return 1


