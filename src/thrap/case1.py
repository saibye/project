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

from pub_thrap import *

# 标准

#
# 
#
def thrap_analyzer1(_stock_id, _trade_date, _my_df, _used_len, _db):
    global g_detail_fetched 

    lowest   = 0
    mailed = 0
    content1 = "thrap\n"
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


    B_RATE = 3

    BC_RATE= 2.3

    D_DAYS1 = 3
    D_DAYS2 = 2
    D_DAYS3 = 8
    D_RPV   = 9.8
    D_RATE  = 1.3
    D_ZT  = 2.6

    E_DAYS1 = 1
    E_DAYS2 = 6
    E_DAYS2 = 5
    E_RATE  = 18

    E_STEP  = 4.8
    E_STEP  = 3.8

    CONTRAST = 1.29

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
            o_B = open_price
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
            o_K = open_price
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
            o_C = open_price
            h_C = high_price
            l_C = low_price
            i_C = idx
            rt_C= rate
            zt_C= zt
        # D点
        elif idx == 3:
            d_D = pub_date
            v_D = vol
            p_D = close_price
            o_D = open_price
            h_D = high_price
            l_D = low_price
            i_D = idx
            rt_D= rate
            zt_D= zt
        # P点
        elif idx == 4:
            d_P = pub_date
            v_P = vol
            p_P = close_price
            o_P = open_price
            h_P = high_price
            l_P = low_price
            i_P = idx
            rt_P= rate
            zt_P= zt
            break


        idx  = idx + 1


    # 确认B点
    # log_debug("B点跌幅: %.2f%%, 柱体: %.2f%%", rt_B, zt_B)
    if rt_B > B_RATE:
        # log_info("sorry: B not green")
        return 1


    # BC 连续下降
    rate_BC = (h_C / l_B - 1) * 100
    rule_C = h_C > h_K and h_K > h_B
    rule_B = rate_BC > BC_RATE
    if rule_C and rule_B:
        log_info("Data: %s: C点确认: %s, 三线跌幅: %.2f", _stock_id, d_C, rate_BC)
    else:
        log_info("sorry: C-point not match: %s, %s, %.2f%%", rule_C, rule_B, rate_BC)
        return 1

    # 寻找D点： C点往前n1单位内的最高点
    """
    h_D, p_D, d_D, i_D, v_D, rt_D, zt_D = thrap_preceding_high2(_my_df, _used_len, d_C, D_DAYS1, _db)
    log_info("Data: %s: D点: %s, %.2f%%, high(%.2f)", _stock_id, d_D, rt_D, h_D)
    if h_D < 1: 
        log_info("sorry: D not so high: %.2f", h_D)
        return 1
    """
    log_info("Data: %s: D点: %s, %.2f%%, high(%.2f)", _stock_id, d_D, rt_D, h_D)
    log_info("Data: %s: P点: %s, %.2f%%, high(%.2f)", _stock_id, d_P, rt_P, h_P)

    # D点RPV
    rpv_D = thrap_rpv(_my_df, _used_len, d_D, D_DAYS3, _db)
    log_debug("Data: %s: rpv(D点): %.2f", _stock_id, rpv_D)


    # 寻找E点： D点往前n1单位开始，n2单位内的最低点
    l_E, p_E, d_E, i_E, v_E, rt_E = thrap_preceding_low(_my_df, _used_len, d_D, E_DAYS1, E_DAYS2, _db)
    log_info("Data: %s: E点: %s, %.2f%%, low(%.2f)", _stock_id, d_E, rt_E, l_E)
    rate_DE = (h_D / l_E - 1) * 100.00
    log_info("Data: %s: rate-DE: %.2f%%", _stock_id, rate_DE)

    len_DE  = i_E - i_D
    step_DE = rate_DE / len_DE
    log_info("Data: %s: step-DE: %.2f", _stock_id, step_DE)

    # D点降幅
    rate_DB = (h_D / l_B - 1) * 100.00
    log_info("Data: %s: rate-DB: %.2f%%", _stock_id, rate_DB)
    if rate_DB < 1: 
        log_info("sorry: DB not downing: %.2f", h_D)
        return 1

    # 升降对比
    if rate_DB > 0:
        contrast = rate_DE / rate_DB
    else:
        contrast = 0.1
    log_info("Data: %s: contrast: %.2f", _stock_id, contrast)

    # 综合处理
    rule1 = rt_D > 9.8 or rt_P > 9.8 or rt_C > 9.6
    rule2 = rpv_D > 5
    rule3 = rpv_D > 2.5 and rate_DE > 10 and contrast > 2
    rule4 = rpv_D > 2.0 and rate_DE > 6  and contrast > 4

    log_info("Data: %s: rule1: %s, rule2: %s, rule3:%s", _stock_id, rule1, rule2, rule3)
    expect_price = 1000.0
    if rule1 or rule2:
        to_mail = True
        expect_price = max(o_B, p_B)
        log_info("rule12: expect: %.2f", expect_price)
    elif rule3 or rule4:
        to_mail = True
        expect_price = max(o_C, p_C, o_D, p_D)
        log_info("rule34: expect: %.2f", expect_price)
    else:
        return 1

    log_info("+++++++++++++++++++++++++++++++++++++")
    log_info("bingo: %s precast %s", _stock_id, _trade_date)
    log_info("B: %s", d_B)
    log_info("C: %s", d_C)
    log_info("D: %s", d_D)
    log_info("E: %s", d_E)
    log_debug("XXX: %s", _stock_id)
    content1 += "%s -- %s\n" % (_stock_id, _trade_date)
    content1 += thrap_mail_content()
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

    if to_mail:

        subject = "thrap1: %s -- %s" % (_stock_id, _trade_date)

        thrap_save(_stock_id, _trade_date, expect_price, subject, content1, _db)

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


