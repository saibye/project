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

from pub_week import *

# 标准
# ma5, 10, 200粘合

#
# 
#
def week_analyzer1(_stock_id, _trade_date, _my_df, _used_len, _db):
    global g_detail_fetched 

    lowest   = 0
    mailed = 0
    content1 = "week\n"
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


    A_RATE  = 1
    A_BOND21= 99
    A_BOND31= 99
    A_BOND22= 98
    A_BOND32= 97
    A_BOND23= 99
    A_BOND33= 98
    A_DAYS1 = 35
    A_DAYS2 = 50

    A_DAYS3 = 8
    B_DAYS1 = 8


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

        # 量比 vol/ma50
        if ref_vma50(TECH_IDX) > 0:
            vr = (vol / ref_vma50(TECH_IDX) - 1) * 100
        else:
            vr = 0
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
    ma200 = ref_ma200(TECH_IDX)
    bond2 = min(ma5, ma10) / max(ma5, ma10) * 100
    bond3 = min(ma5, ma10, ma200) / max(ma5, ma10, ma200) * 100
    log_debug("A点: rate: %.2f%%, open: %.2f, close: %.2f", rt_A, o_A, p_A)
    log_debug("A点: ma5:  %.2f,   ma10: %.2f, ma200: %.2f", ma5, ma10, ma200)
    log_debug("A点: vr50:  %.2f%%", vr)

    break_days_A1, block_date_A1 = week_break_days(_my_df, _used_len, d_A, p_A, _db)
    log_debug("A点: 收盘价突破: %d, %s", break_days_A1, block_date_A1)

    break_days_A2, block_date_A2 = week_vol_break_days(_my_df, _used_len, d_A, v_A, _db)
    log_debug("A点: 成交量突破: %d, %s", break_days_A2, block_date_A2)

    # 确认A点
    """
    rule_A1 = rt_A > A_RATE
    rule_A2 = close_price >= max(ma5, ma10, ma200)
    rule_A3 = open_price  <= min(ma5, ma10, ma200)
    rule_A41= bond2 > A_BOND21 and bond3 > A_BOND31
    rule_A42= rt_A > 9.8 and bond2 > A_BOND22 and bond3 > A_BOND32
    rule_A43= rt_A > 5   and bond2 > A_BOND23 and bond3 > A_BOND33
    rule_A4 = rule_A41 or rule_A42 or rule_A43
    if rule_A1 and rule_A2 and rule_A3 and rule_A4:
        log_info("A点: %s, rate: %.2f, bond2: %.2f%%, bond3: %.2f%%", d_A, rt_A, bond2, bond3)
    else:
        log_info("sorry: A not match: %s, %s, %s, %s", rule_A1, rule_A2, rule_A3, rule_A4)
        return 1

    # 确认B点
    d_B, i_B, rt_B, vr_B, days_BC, d_C = week_break_point(_my_df, _used_len, d_A, A_DAYS1, A_DAYS2, _db)
    if d_B == "":
        log_info("sorry: no B point in %d unit for %d break", A_DAYS1, A_DAYS2)
        return 1
    else:
        log_debug("B点: %s, rate: %.2f%%, vr: %.2f%%", d_B, rt_B, vr_B)
        log_debug("C点: %s, region(%d)", d_C, days_BC)

    # A点新高天数
    break_days_A, block_date = week_break_preceding_days(_my_df, _used_len, d_A, p_A, _db)
    log_info("A点: break days: %d, block_at: %s", break_days_A, block_date)

    # A、B区域内涨停个数
    violent_unit = week_bump_units(_my_df, _used_len, d_A, d_B, _db)
    log_info("AB: violent days: %d", violent_unit)

    # A/B点RPV
    rpv_A = week_rpv(_my_df, _used_len, d_A, A_DAYS3, _db)
    log_debug("A点: %s: rpv(A点): %.2f", _stock_id, rpv_A)

    rpv_B = week_rpv(_my_df, _used_len, d_B, B_DAYS1, _db)
    log_debug("B点: %s: rpv(B点): %.2f", _stock_id, rpv_B)


    # 综合处理
    rule1 = violent_unit > 0        # 有涨停
    rule2 = break_days_A > 100      # A点强突破

    if rule1 or rule2:
        to_mail = True
        log_info("bingo: %s week %s", _stock_id, _trade_date)

    if to_mail:

        log_info("+++++++++++++++++++++++++++++++++++++")
        log_debug("Data: %s", _stock_id)
        content1 += "%s -- %s\n" % (_stock_id, _trade_date)
        content1 += week_mail_content()
        content1 += "A点: %s，涨幅: %.2f%%\n"  % (d_A, rt_A)
        content1 += "B点: %s, 涨幅: %.2f%%\n"  % (d_B, rt_B)
        content1 += "A点: 突破: %d+\n"  % (break_days_A)
        content1 += "AB:  涨停次数: %d\n" % (violent_unit)
        content1 += "A点: RPV: %.2f+\n" % (rpv_A)
        content1 += "B点: RPV: %.2f+\n" % (rpv_B)
        content1 += "AB:  区间长度: %d\n" % (i_B - i_A)
        content1 += "+++++++++++++++++++++++++\n"
        info  = get_basic_info_all(_stock_id, _db)
        content1 += info

        subject = "week1: %s -- %s" % (_stock_id, _trade_date)

        # week_save(_stock_id, _trade_date, expect_price, subject, content1, _db)

        log_info(subject)
        log_info("mail:\n%s", content1)
        if sai_is_product_mode():
            mailed = 1
            # saimail_dev(subject, content1)
            return 0
    else:
        # log_info("sorry: %s, %s", _stock_id, _trade_date)
        pass
    """

    return 1


