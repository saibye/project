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

# 变种：不止三线
# 动态查找C点，更合理!
# case5的变种: A点收盘价没有压制，而是最高价压制！

#
# 603019
#
def thrive_analyzer7(_stock_id, _trade_date, _my_df, _used_len, _db):
    mailed = 0
    content1 = "three-five line\n"
    to_mail = False

    idx    = 0
    TECH_IDX = 0

    # A点指标
    A_RATE = 0.4
    A_ZT   = 1.0

    B_RATE = 1.2

    C_DAYS1 = 7

    C_RATE = 10


    D_DAYS1 = 3
    D_DAYS3 = 8
    D_DAYS4 = 20
    D_RPV   = 3
    D_RATE = 10

    E_DAYS1 = 1
    E_DAYS2 = 6
    E_RATE  = 20

    CONTRAST = 1.5

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

        idx  = idx + 1


    # 确认A/B点
    # log_debug("A点涨幅: %.2f%%, 柱体: %.2f%%", rt_A, zt_A)
    # log_debug("B点跌幅: %.2f%%, 柱体: %.2f%%", rt_B, zt_B)
    rule_A = p_A > p_B and h_A > h_B and \
        rt_A > A_RATE and zt_A > A_ZT and \
        rt_B < B_RATE
    if rule_A:
        log_info("nice: AB点确认: %.2f > %.2f", h_A, h_B)
    else:
        log_info("sorry: AB not match: %.3f pk %.3f", p_A, h_B)
        return 1

    # 寻找前高，确认C点
    d_C, h_C, days_C, rt_C, zt_C = thrive_desceding_days(_my_df, _used_len, d_B, C_DAYS1, _db)
    log_info("trying: C点: %s, %d", d_C, days_C)
    if days_C < 3 or days_C > 5: 
        log_info("sorry: C not match: %s, %d", d_C, days_C)
        return 1

    # BC 有下降
    rate_BC = (h_C / l_B - 1) * 100
    rule_C = rate_BC > C_RATE
    if rule_C:
        log_info("nice: C点确认: 跌幅: %.2f", rate_BC)
    else:
        log_info("sorry: C-point not match: %s, %.2f", rule_C, rate_BC)
        return 1


    # 寻找D点： C点往前n1单位内的最高点
    h_D, p_D, d_D, i_D, v_D, rt_D, vr_D = thrive_preceding_high2(_my_df, _used_len, d_C, D_DAYS1, _db)
    log_info("trying: D点: %s, %.2f%%, high(%.2f)", d_D, rt_D, h_D)
    if h_D < 1: 
        log_info("sorry: D not so high: %.2f", h_D)
        return 1

    # D点RPV
    rpv_D = thrive_rpv(_my_df, _used_len, d_D, D_DAYS3, _db)
    log_debug("rpv(D点)(%d): %.2f", D_DAYS3, rpv_D)
    if rpv_D < D_RPV:
        log_info("sorry: D rpv not match: %.2f", rpv_D)
        return 1


    # DB 深幅下跌
    rate_DB = (h_D / l_B - 1) * 100.00
    rule_D = rate_DB > D_RATE
    log_debug("DB降幅: %.2f", rate_DB)
    if not rule_D:
        log_info("sorry: D-point not match: DB幅度: %s, %.2f", rule_D, rate_DB)
        return 1


    # D点是新高
    break_days, block_date = thrive_break_days(_my_df, _used_len, d_D, h_D, _db)
    log_debug("D block days: %d @%s", break_days, block_date)
    if break_days < D_DAYS4:
        log_info("sorry: D-point not match: block-days: %d", break_days)
        return 1


    # 寻找E点： D点往前n1单位开始，n2单位内的最低点
    l_E, p_E, d_E, i_E, v_E, rt_E = thrive_preceding_low(_my_df, _used_len, d_D, E_DAYS1, E_DAYS2, _db)
    log_info("try: E点: %s, %.2f%%, low(%.2f)", d_E, rt_E, l_E)
    rate_DE = (h_D / l_E - 1) * 100.00
    log_info("rate-DE: %.2f%%", rate_DE)
    if rate_DE < E_RATE:
        log_info("sorry: E not so low: %.2f", l_E)
        return 1

    # 升降对比
    contrast = rate_DE / rate_DB
    log_info("rate-DB: %.2f%%, contrast: %.2f", rate_DE, contrast)
    if contrast < CONTRAST:
        log_info("sorry: up < down: %.2f", contrast)
        return 1

    log_info("+++++++++++++++++++++++++++++++++++++")
    log_info("bingo: %s counterback at %s", _stock_id, d_A)
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
        subject = "thrive7: %s -- %s" % (_stock_id, _trade_date)
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


