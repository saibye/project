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

from pub_u15m import *

# 大阳线穿越6线
# 放巨量
# 高位徘徊3+单位


#
# 000717
#
def u15m_analyzer2(_stock_id, _trade_date, _my_df, _used_len, _db):
    global g_detail_fetched 

    lowest   = 0
    mailed = 0
    content1 = "ma-law\n"
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


    # B点指标
    B_RATE = 4
    B_VR1 = 200
    B_VR2 = 400
    B_VR3 = 500
    B_UNIT = 2

    B_RATE = 1
    B_VR1 = 50
    B_VR2 = 100
    B_VR3 = 100


    """
    log_debug("ref0: o[%.3f] - p[%.3f] - l[%.3f] - h[%.3f] -- v[%.3f]", ref_open(0), ref_close(0), ref_low(0), ref_high(0), ref_vol(0))
    log_debug("ma0:  5[%.3f] - 10[%.3f] - 20[%.3f] - 200[%.3f]", ref_ma5(0), ref_ma10(0), ref_ma20(0), ref_ma200(0))
    log_debug("vma0: 5[%.3f] - 10[%.3f] - 50[%.3f]", ref_vma5(0), ref_vma10(0), ref_vma50(0))
    """

    for row_index, row in _my_df.iterrows():
        TECH_IDX = idx

        close_price      = row['close_price']
        high_price       = row['high_price']
        low_price        = row['low_price']
        last_close_price = row['last']
        open_price       = row['open_price']
        vol              = row['total']
        pub_date_time    = row['pub_date_time']

        # 涨幅
        rate = (close_price - last_close_price) / last_close_price * 100
        rate2= (high_price - last_close_price) / last_close_price * 100
        # log_debug("%s-%s: rate: %.3f, %.3f, %.3f", _stock_id, pub_date_time, rate, close_price, last_close_price)

        # 柱体
        zt   = (close_price - open_price) / last_close_price * 100

        vr1 = 0
        vr2 = 0
        vr3 = 0
        # 量比
        if ref_vma5(TECH_IDX) > 0:
            vr1 = (vol / ref_vma5(TECH_IDX) - 1) * 100

        if ref_vma10(TECH_IDX) > 0:
            vr2 = (vol / ref_vma10(TECH_IDX) - 1) * 100

        if ref_vma50(TECH_IDX) > 0:
            vr3 = (vol / ref_vma50(TECH_IDX) - 1) * 100

        # log_debug("%s-%s: vr5: %.2f, vr10: %.2f, vr50: %.2f", _stock_id, pub_date_time, vr1, vr2, vr3)


        ma200 = ref_ma200(TECH_IDX)

        ma5   = ref_ma5(TECH_IDX)
        ma10  = ref_ma10(TECH_IDX)
        ma20  = ref_ma20(TECH_IDX)
        ma30  = ref_ma30(TECH_IDX)
        ma60  = ref_ma60(TECH_IDX)

        """
        log_debug("%s-%s: open: %.3f, ma200: %.3f, close:%.3f", _stock_id, pub_date_time, open_price, ma200, close_price)
        log_debug("%s-%s: open: %.3f, ma5:   %.3f, close:%.3f", _stock_id, pub_date_time, open_price, ma5, close_price)
        log_debug("%s-%s: open: %.3f, ma10:  %.3f, close:%.3f", _stock_id, pub_date_time, open_price, ma10, close_price)
        log_debug("%s-%s: open: %.3f, ma20:  %.3f, close:%.3f", _stock_id, pub_date_time, open_price, ma20, close_price)
        log_debug("%s-%s: open: %.3f, ma30:  %.3f, close:%.3f", _stock_id, pub_date_time, open_price, ma30, close_price)
        log_debug("%s-%s: open: %.3f, ma60:  %.3f, close:%.3f", _stock_id, pub_date_time, open_price, ma60, close_price)
        """

        rule1 = close_price >= ma200 and open_price <= ma200 and \
                          close_price >= ma5 and open_price <= ma5 and \
                          close_price >= ma10 and open_price <= ma10 and \
                          close_price >= ma20 and open_price <= ma20 and \
                          close_price >= ma30 and open_price <= ma30 and \
                          close_price >= ma60 and open_price <= ma60

        rule2 = close_price >= ma200 and low_price <= ma200 and \
                          close_price >= ma5 and low_price <= ma5 and \
                          close_price >= ma10 and low_price <= ma10 and \
                          close_price >= ma20 and low_price <= ma20 and \
                          close_price >= ma30 and low_price <= ma30 and \
                          close_price >= ma60 and low_price <= ma60
        if rule1 or rule2:
            log_info("nice: get B point: %s", pub_date_time)

            d_B = pub_date_time
            v_B = vol
            p_B = close_price
            h_B = high_price
            l_B = low_price
            i_B = idx
            rt_B= rate
            zt_B= zt
            vr1_B= vr1
            vr2_B= vr2
            vr3_B= vr3
            log_info("B点：rate: %.2f%%，IDX: %d", rt_B, i_B)
            log_debug("B点：vr: %.2f, %.2f, %.2f", vr1_B, vr2_B, vr3_B)

            break
        else:
            # log_info("sorry: %s not cross!", pub_date_time)
            pass



        idx  = idx + 1

        if idx > 16:
            log_info("sorry: %s, %s not match: %d!", _stock_id, pub_date_time, idx)
            return 1


    # 大涨
    if rt_B < B_RATE:
        log_info("sorry: 上涨不足: %.2f", rt_B)
        return 1

    # 放巨量
    if vr1_B > B_VR1 and vr2_B > B_VR2 and vr3_B > B_VR3:
        log_info("nice: 放巨量: %.2f, %.2f, %.2f", vr1_B, vr2_B, vr3_B)
    else:
        log_info("sorry: 放量不足: %.2f, %.2f, %.2f", vr1_B, vr2_B, vr3_B)
        return 1


    # 之后高位徘徊
    upper_units = u15m_upper_hover_units(_my_df, _used_len, p_B, i_B, _db)
    log_debug("upper-hover units: %d", upper_units)
    if upper_units < B_UNIT:
        log_info("sorry: 需要突破后高位徘徊: %d", upper_units)
        return 1


    # 往前存在N个单位低于ma200
    break_units, touch_date_time, touch_idx = u15m_break_ma200_unit(_my_df, _used_len, d_B, _db)
    log_debug("break units: %d, %s, %d", break_units, touch_date_time, touch_idx)
    # TOOD: check ?


    # 加分：开盘高于昨高 TODO

    # 确认A点

    log_info("+++++++++++++++++++++++++++++++++++++")
    log_info("bingo: %s break-6lines %s", _stock_id, d_B)
    log_info("B: %s", d_B)
    log_debug("XXX: %s", _stock_id)
    content1 += "%s -- %s\n" % (_stock_id, d_B)
    content1 += "%s -- 穿越6线\n" % (d_B)
    content1 += "%s -- 放量: vma10: +%.2f\n" % (d_B, vr2_B)
    content1 += "%s -- 放量: vma50: +%.2f\n" % (d_B, vr3_B)
    content1 += "高位徘徊: %d(unit)\n" % (upper_units)
    content1 += "突破单位: %d(unit)\n" % (break_units)
    content1 += "+++++++++++++++++++++++++\n"
    info  = get_basic_info_all(_stock_id, _db)
    content1 += info
    to_mail = True

    if to_mail:
        subject = "15min-ma200: %s -- %s" % (_stock_id, _trade_date)
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


