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

from pub_malaw import *

# 巨量突破

#
# 
#
def malaw_analyzer2(_stock_id, _trade_date, _my_df, _used_len, _db):
    global g_detail_fetched 

    lowest   = 0
    mailed = 0
    content1 = "malaw\n"
    to_mail = False

    idx    = 0
    TECH_IDX = 0

    #
    p_A = 1000
    v_A = 0
    i_A = -1
    d_A = ""
    rt_A = 0
    vr_A = 0

    #
    p_B = 1000
    v_B = 0
    i_B = -1
    d_B = ""
    rt_B = 0
    vr_B = 0

    #
    p_C = 0
    v_C = 0
    i_C = -1
    d_C = ""
    rt_C = 0
    vr_C = 0


    A_RATE  = 4.5
    A_VR50  = 300
    A_RPV   = 1.5

    A_DAYS1 = 35
    A_DAYS2 = 50

    A_DAYS3 = 8
    A_DAYS4 = 2

    A_BREAK_DAYS = 50


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

        if ref_ma200(TECH_IDX) <= 1:
            log_info("no ma200 value")
            return 1

        # 量比 vol/ma50
        if ref_vma50(TECH_IDX) > 0:
            vr50 = (vol / ref_vma50(TECH_IDX) - 1) * 100
        else:
            vr50 = 0.0

        # 量比 vol/ma10
        if ref_vma10(TECH_IDX) > 0:
            vr10 = (vol / ref_vma10(TECH_IDX) - 1) * 100
        else:
            vr10 = 0.0

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

            break


        idx  = idx + 1


    ma5   = ref_ma5(TECH_IDX)
    ma10  = ref_ma10(TECH_IDX)
    ma20  = ref_ma20(TECH_IDX)
    ma200 = ref_ma200(TECH_IDX)
    bond2 = min(ma5, ma10) / max(ma5, ma10) * 100
    bond4 = 100-min(abs(close_price/ma200-1), abs(open_price/ma200-1), abs(high_price/ma200-1), abs(low_price/ma200-1)) * 100
    log_debug("A点: rate: %.2f%%, open: %.2f, close: %.2f", rt_A, o_A, p_A)
    log_debug("A点: ma5:  %.2f,   ma10: %.2f, ma20: %.2f, ma200: %.2f", ma5, ma10, ma20, ma200)
    log_debug("A点: ma5-10 bond2:  %.2f%%", bond2)
    log_debug("A点: ma200  bond4:  %.2f%%", bond4)
    log_debug("A点: vr50: %.2f, vr10: %.2f", vr50, vr10)

    # 确认A点
    rule_A1 = rt_A > A_RATE
    rule_A2 = close_price >= max(ma5, ma10, ma200)
    rule_A3 = low_price <= ma200 or last_close_price <= ma200
    rule_A4 = vr50 > A_VR50
    if rule_A1 and rule_A2 and rule_A3 and rule_A4:
        log_info("A点: %s, rate: %.2f, vr50: %.2f", d_A, rt_A, vr50)
    else:
        log_info("sorry: A not match: %s, %s, %s, %s", rule_A1, rule_A2, rule_A3, rule_A4)
        return 1

    # A点新高天数
    break_days_A, block_date = malaw_break_preceding_days(_my_df, _used_len, d_A, p_A, _db)
    if break_days_A < A_BREAK_DAYS:
        log_info("sorry: A not break too much: %d", break_days_A)
        return 1
    else:
        log_info("A点: break days: %d, block_at: %s", break_days_A, block_date)

    # A点RPV
    rpv_A = malaw_rpv(_my_df, _used_len, d_A, A_DAYS3, _db)
    if rpv_A < A_RPV:
        log_info("sorry: A rpv too small: %.2f", rpv_A)
        return 1
    else:
        log_debug("A点: rpv(A点): %.2f", rpv_A)

    # A点有GAP
    gap_A, gap_date = malaw_has_gap(_my_df, _used_len, d_A, A_DAYS4, _db)
    log_debug("A点: gap: %s, %s", gap_A, gap_date)

    log_info("Data: %s: rate: %.2f,\t vr50: %.2f, rpv: %.2f,\t break: %3d, gap: %s",
            _stock_id, rt_A, vr50, rpv_A, break_days_A, gap_A)

    # 综合处理
    rule_strong = rt_A >= 9 and rpv_A >= 8
    rule_medium = rt_A >= 8 and rt_A < 9 and vr50 > 300 and rpv_A > 8 and break_days_A > 80
    rule_weak   = rt_A < 8  and vr50 > 400 and rpv_A > 10 and break_days_A > 80
    rule_one    = rt_A < 5  and vr50 > 500 and rpv_A > 1.8 and break_days_A > 60  # 000932

    if rule_strong:
        to_mail = True
        subject = "malaw2: strong %s -- %s" % (_stock_id, _trade_date)
    elif rule_medium:
        to_mail = True
        subject = "malaw2: medium %s -- %s" % (_stock_id, _trade_date)
    elif rule_weak:
        to_mail = True
        subject = "malaw2: weak   %s -- %s" % (_stock_id, _trade_date)
    elif rule_one:
        to_mail = True
        subject = "malaw2: one    %s -- %s" % (_stock_id, _trade_date)
    else:
        return 1

    if to_mail:
        log_info("bingo: %s", subject)

        log_info("+++++++++++++++++++++++++++++++++++++")
        content1 += "%s -- %s\n" % (_stock_id, _trade_date)
        content1 += malaw_mail_content2()
        content1 += "A点: %s，涨幅: %.2f%%\n"  % (d_A, rt_A)
        content1 += "A点: vr50: %.2f%%+\n" % (vr50)
        content1 += "A点: gap: %s\n"  % (gap_A)
        content1 += "A点: RPV: %.2f+\n" % (rpv_A)
        content1 += "A点: 突破: %d+\n"  % (break_days_A)
        content1 += "+++++++++++++++++++++++++\n"
        info  = get_basic_info_all(_stock_id, _db)
        content1 += info


        good_type = "malaw2"
        # malaw_save(_stock_id, _trade_date, good_type, expect_price, subject, content1, _db)

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


