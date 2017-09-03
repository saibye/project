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

from pub_thrive import *

# 三线：三连低（high)，三连阴，三连降
# 变种：A点收盘价没有压制，而是最高价压制！

#
# 603616
#
def thrive_analyzer2(_stock_id, _trade_date, _my_df, _used_len, _db):
    mailed = 0
    content1 = "three-five line\n"
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

    # B: A点前一天
    p_B = 1000
    v_B = 0
    i_B = -1
    d_B = ""
    rt_B = 0
    vr_B = 0

    # C: B点前两天
    p_C = 0
    v_C = 0
    i_C = -1
    d_C = ""
    rt_C = 0
    vr_C = 0

    # D: C点往前最高点
    p_D = 1000
    v_D = 0
    i_D = -1
    d_D = ""
    rt_D = 0
    vr_D = 0

    # E: 从E到D一路上扬
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
    A_RATE = 5.0
    A_ZT   = 2

    B_RATE = -1
    B_ZT   = -1

    C_RATE = 20

    D_DAYS1 = 1
    D_DAYS2 = 8
    D_DAYS3 = 8

    E_DAYS1 = 1
    E_DAYS2 = 6
    E_RATE  = 30

    CONTRAST = 1.5

    for row_index, row in _my_df.iterrows():
        TECH_IDX = idx

        close_price      = row['close_price']
        high_price       = row['high_price']
        low_price        = row['low_price']
        last_close_price = row['last']
        open_price       = row['open_price']
        vol              = row['total']
        pub_date         = row['pub_date']

        # 涨幅
        rate = (close_price - last_close_price) / last_close_price * 100
        rate2= (high_price - last_close_price) / last_close_price * 100

        # 柱体
        zt   = (close_price - open_price) / last_close_price * 100
        vr   = 0
        # log_debug("%s-%s: %.2f, %.2f, %.3f", _stock_id, pub_date, close_price, open_price, zt)
        # log_debug("%s-%s: %.2f, %.2f, %.3f", _stock_id, pub_date, close_price, open_price, rate)

        # A点
        if idx == 0:
            d_A = pub_date
            v_A = vol
            p_A = close_price
            o_A = open_price
            h_A = high_price
            l_A = low_price
            i_A = idx
            rt_A= rate
            zt_A= zt

        # B点
        elif idx == 1:
            d_B = pub_date
            v_B = vol
            p_B = close_price
            o_B = open_price
            h_B = high_price
            l_B = low_price
            i_B = idx
            rt_B= rate
            zt_B= zt

        # K点 (BC中间的点)
        elif idx == 2:
            d_K = pub_date
            v_K = vol
            p_K = close_price
            o_K = open_price
            h_K = high_price
            l_K = low_price
            i_K = idx
            rt_K= rate
            zt_K= zt

        # C点
        elif idx == 3:
            d_C = pub_date
            v_C = vol
            p_C = close_price
            o_C = open_price
            h_C = high_price
            l_C = low_price
            i_C = idx
            rt_C= rate
            zt_C= zt
            break


        idx  = idx + 1


    # 确认A点
    # log_debug("A点涨幅: %.2f%%, 柱体: %.2f%%", rt_A, zt_A)
    # log_debug("B点跌幅: %.2f%%, 柱体: %.2f%%", rt_B, zt_B)
    rule_A = h_A > h_B and p_A > max(p_B, o_B) and \
        rt_A > A_RATE and zt_A > A_ZT and \
        rt_B < B_RATE and zt_B < B_ZT
    if rule_A:
        log_info("nice: AB点确认: %.2f > %.2f", h_A, h_B)
    else:
        log_info("sorry: AB not match")
        return 1

    # BC 连续下降
    rate_BC = (h_C / l_B - 1) * 100
    rule_C = h_C > h_K and h_K > h_B and rate_BC > C_RATE
    rule_B = rt_C < 0 and rt_K < 0 and rt_B < 0
    rule_K = zt_B <= 0 and zt_K <= 0 and zt_C <= 0
    if rule_C and rule_B and rule_K:
        log_info("nice: C点确认: 跌幅: %.2f", rate_BC)
    else:
        log_info("sorry: C-point not match: %s, %s, %s", rule_C, rule_B, rule_K)
        return 1

    # 寻找D点： C点往前n1单位开始，n2单位内的最高点
    h_D, p_D, d_D, i_D, v_D, rt_D, vr_D = thrive_preceding_high(_my_df, _used_len, d_C, D_DAYS1, D_DAYS2, _db)
    log_info("trying: D点: %s, %.2f%%, high(%.2f)", d_D, rt_D, h_D)
    if h_D < 1: 
        log_info("sorry: D not so high: %.2f", h_D)
        return 1

    # D点RPV
    rpv_D = thrive_rpv(_my_df, _used_len, d_D, D_DAYS3, _db)
    log_debug("rpv(D点): %.2f", rpv_D)
    if rpv_D < 3:
        log_info("sorry: D rpv not match: %.2f", rpv_D)
        return 1


    # 寻找E点： D点往前n1单位开始，n2单位内的最低点
    l_E, p_E, d_E, i_E, v_E, rt_E = thrive_preceding_low(_my_df, _used_len, d_D, E_DAYS1, E_DAYS2, _db)
    log_info("try: E点: %s, %.2f%%, low(%.2f)", d_E, rt_E, l_E)
    rate_DE = (h_D / l_E - 1) * 100.00
    log_info("rate-DE: %.2f%%", rate_DE)
    if rate_DE < E_RATE:
        log_info("sorry: E not so low: %.2f", l_E)
        return 1

    rate_DB = (h_D / l_B - 1) * 100.00
    contrast = rate_DE / rate_DB
    log_info("rate-DB: %.2f%%, contrast: %.2f", rate_DE, contrast)
    if contrast < CONTRAST:
        log_info("sorry: up < down: %.2f", contrast)
        return 1

    log_info("nice: 三五线成立")

    log_info("+++++++++++++++++++++++++++++++++++++")
    log_info("bingo: %s counterback at %s", _stock_id, d_E)
    log_info("A: %s", d_A)
    log_info("B: %s", d_B)
    log_info("C: %s", d_C)
    log_info("D: %s", d_D)
    log_info("E: %s", d_E)
    log_debug("XXX: %s", _stock_id)
    content1 += "%s -- %s\n" % (_stock_id, d_A)
    content1 += "注意：不能被ma200压制！\n"
    content1 += "注意：下降三线的开盘价接近昨收\n"
    content1 += "优先：收复ma20或伴随5/10穿越最佳！\n"
    content1 += "优先：附近有ma200支撑！！！\n\n"
    content1 += "A点: %s，涨幅: %.2f%%\n"  % (d_A, rt_A)
    content1 += "B点: %s，降幅: %.2f%%\n"  % (d_B, rate_BC)
    content1 += "C点: %s\n"  % (d_C)
    content1 += "D点: %s，升幅: %.2f%%\n"  % (d_D, rate_DE)
    content1 += "E点: %s\n"  % (d_E)
    content1 += "D点: RPV: %.2f\n" % (rpv_D)
    content1 += "+++++++++++++++++++++++++\n"
    info  = get_basic_info_all(_stock_id, _db)
    content1 += info
    to_mail = True

    if to_mail:
        subject = "thrive2: %s -- %s" % (_stock_id, _trade_date)
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


