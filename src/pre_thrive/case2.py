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

from pub_pre_thrive import *

# 4连阴，4连跌

#
# 002201 @2017-9-6
#
def pre_thrive_analyzer2(_stock_id, _trade_date, _my_df, _used_len, _db):
    global g_detail_fetched 

    lowest   = 0
    mailed = 0
    content1 = "pre-three-five line\n"
    to_mail = False

    idx    = 0
    TECH_IDX = 0


    # 今日：有近三日最低的high-price
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


    B_RATE = -1.8

    C_RATE = -2
    BC_RATE= 7.9

    D_DAYS1 = 1
    D_DAYS2 = 2
    D_DAYS3 = 8
    D_RATE  = 4
    D_ZT  = 4
    D_RPV   = 5

    E_DAYS1 = 1
    E_DAYS2 = 6
    E_DAYS2 = 5
    E_RATE  = 20

    E_STEP  = 5

    CONTRAST = 1.8

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

        # B点
        if idx == 0:
            d_B = pub_date
            v_B = vol
            p_B = close_price
            h_B = high_price
            l_B = low_price
            i_B = idx
            rt_B= rate
            zt_B= zt

        # K点 (BC中间的点)
        elif idx == 1:
            d_K = pub_date
            v_K = vol
            p_K = close_price
            h_K = high_price
            l_K = low_price
            i_K = idx
            rt_K= rate
            zt_K= zt

        # C点
        elif idx == 2:
            d_C = pub_date
            v_C = vol
            p_C = close_price
            h_C = high_price
            l_C = low_price
            i_C = idx
            rt_C= rate
            zt_C= zt

        # X点
        elif idx == 3:
            d_X = pub_date
            v_X = vol
            p_X = close_price
            h_X = high_price
            l_X = low_price
            i_X = idx
            rt_X= rate
            zt_X= zt

            break


        idx  = idx + 1


    # 确认B点
    # log_debug("B点跌幅: %.2f%%, 柱体: %.2f%%", rt_B, zt_B)
    rule_B = rt_B < B_RATE
    if not rule_B:
        # log_info("sorry: B not green")
        return 1

    # 确认C点
    if  rt_C > C_RATE:
        # log_info("sorry: B not green")
        return 1

    # BC 连续下降
    rate_BC = (h_C / l_B - 1) * 100
    rule_B = rate_BC > BC_RATE
    rule_C = h_X > h_C and h_C > h_K and h_K > h_B
    rule_X = rt_X < 0 and rt_C < 0 and rt_K < 0 and rt_B < 0
    rule_K = zt_X <= 0 and zt_C <= 0 and zt_K <= 0 and zt_B <= 0
    if rule_C and rule_B and rule_X and rule_K:
        log_info("nice: C点确认: %s, 跌幅: %.2f", d_C, rate_BC)
    else:
        log_info("sorry: C-point not match: %s, %s, X: %s, K:%s", rule_C, rule_B, rule_X, rule_K)
        return 1

    # 寻找D点： C点往前n1单位开始，n2单位内的最高点
    h_D, p_D, d_D, i_D, v_D, rt_D, zt_D = pre_thrive_preceding_high(_my_df, _used_len, d_C, D_DAYS1, D_DAYS2, _db)
    log_info("trying: D点: %s, %.2f%%, high(%.2f)", d_D, rt_D, h_D)
    if h_D < 1: 
        log_info("sorry: D not so high: %.2f", h_D)
        return 1

    # D点阳线 
    if rt_D < D_RATE or zt_D < D_ZT:
        log_info("sorry: D not up: %.2f, %.2f", rt_D, zt_D)
        return 1

    # D点RPV
    rpv_D = pre_thrive_rpv(_my_df, _used_len, d_D, D_DAYS3, _db)
    log_debug("rpv(D点): %.2f", rpv_D)
    if rpv_D < D_RPV:
        log_info("sorry: D rpv not match: %.2f", rpv_D)
        return 1


    # 寻找E点： D点往前n1单位开始，n2单位内的最低点
    l_E, p_E, d_E, i_E, v_E, rt_E = pre_thrive_preceding_low(_my_df, _used_len, d_D, E_DAYS1, E_DAYS2, _db)
    log_info("try: E点: %s, %.2f%%, low(%.2f)", d_E, rt_E, l_E)
    rate_DE = (h_D / l_E - 1) * 100.00
    log_info("rate-DE: %.2f%%", rate_DE)
    if rate_DE < E_RATE:
        log_info("sorry: E not so low: %.2f", l_E)
        return 1

    len_DE  = i_E - i_D
    step_DE = rate_DE / len_DE
    log_info("step-DE: %.2f", step_DE)
    if step_DE < E_STEP:
        log_info("sorry: E very slow: %.2f", step_DE)
        return 1

    # D点降幅
    rate_DB = (h_D / l_B - 1) * 100.00
    log_info("rate-DB: %.2f%%", rate_DB)

    # 升降对比
    contrast = rate_DE / rate_DB
    log_info("contrast: %.2f", contrast)
    if contrast < CONTRAST:
        log_info("sorry: up < down: %.2f", contrast)
        return 1

    # 综合处理

    log_info("+++++++++++++++++++++++++++++++++++++")
    log_info("bingo: %s foresee %s", _stock_id, _trade_date)
    log_info("B: %s", d_B)
    log_info("C: %s", d_C)
    log_info("D: %s", d_D)
    log_info("E: %s", d_E)
    log_debug("XXX: %s", _stock_id)
    content1 += "%s -- %s\n" % (_stock_id, _trade_date)
    content1 += pre_thrive_mail_content()
    content1 += "B点: %s，降幅: %.2f%%\n"  % (d_B, rate_BC)
    content1 += "C点: %s\n"  % (d_C)
    content1 += "D点: %s，升幅: %.2f%%+\n"  % (d_D, rate_DE)
    content1 += "E点: %s\n"  % (d_E)
    content1 += "D点: RPV: %.2f+\n" % (rpv_D)
    content1 += "D点: 对比: %.2f+\n" % (contrast)
    content1 += "D点: 步长: %.2f+\n" % (step_DE)
    content1 += "+++++++++++++++++++++++++\n"
    info  = get_basic_info_all(_stock_id, _db)
    content1 += info
    to_mail = True

    if to_mail:

        subject = "pre_thrive2: %s -- %s" % (_stock_id, _trade_date)

        pre_thrive_save(_stock_id, _trade_date, h_B, subject, content1, _db)

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


