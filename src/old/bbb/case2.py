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

from pub_bbb import *


# 放量300+
# 变种：不要求C点
#
def bbb_analyzer2(_stock_id, _trade_date, _my_df, _used_len, _db):
    global g_detail_fetched 

    lowest   = 0
    mailed = 0
    content1 = "bbb\n"
    to_mail = False

    idx    = 0
    TECH_IDX = 0

    #

    A_RATE  = 5
    A_VR    = 300

    A_DAYS1 = 300  # 收盘价突破天数
    A_DAYS2 = 200  # 成交量突破天数

    BC_DAYS = 20
    CD_RATE = 10

    AM_RATE = 7


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
            vr_A= vr

        # B点
        if idx == 1:
            d_B = pub_date
            v_B = vol
            p_B = close_price
            o_B = open_price
            h_B = high_price
            l_B = low_price
            i_B = idx
            rt_B= rate
            zt_B= zt
            vr_B= vr

            break

        idx  = idx + 1

    # log_debug("A点: rate: %.2f%%, vr: %.2f", rt_A, vr_A)

    # 确认A点
    rule_A1 = rt_A > A_RATE
    rule_A2 = vr_A > A_VR
    if rule_A1 and rule_A2:
        log_info("A点: %s, rate: %.2f, vr: %.2f", d_A, rt_A, vr_A)
    else:
        # log_info("sorry: A not match: rate:%s, vr:%s", rule_A1, rule_A2)
        return 1

    length = len(_my_df)

    # A点收盘突破天数
    break_days_A1, block_date_A1 = bbb_break_preceding_days(_my_df, _used_len, d_A, p_A, _db)
    rate_A1 = break_days_A1 * 100.00 / length
    rule_A3 = break_days_A1 > A_DAYS1 and rate_A1 > 90
    if rule_A3:
        log_info("A点: break days: %d, %.2f%%, block_at: %s", break_days_A1, rate_A1, block_date_A1)
    else:
        log_info("sorry: A not break so much: days:%s -- %d, %.2f", rule_A3, break_days_A1, rate_A1)
        return 1

    # A点成交量突破天数
    break_days_A2, block_date_A2 = bbb_vol_break_preceding_days(_my_df, _used_len, d_A, v_A, _db)
    rate_A2 = break_days_A2 * 100.00 / length
    rule_A5 = break_days_A2 > A_DAYS2
    if rule_A5:
        log_info("A点vol: break days: %d, %.2f%%, block_at: %s", break_days_A2, rate_A2, block_date_A2)
    else:
        log_info("sorry: A(volume) not break so much: days:%s", rule_A5)
        return 1

    # B点
    # C点 -- 拐点
    # D点

    # 综合处理
    rule1 = True
    rule2 = False

    if rule1 or rule2:
        to_mail = True
        log_info("bingo: %s bbb %s", _stock_id, _trade_date)

    if to_mail:
        log_info("+++++++++++++++++++++++++++++++++++++")
        log_debug("Data: %s", _stock_id)
        content1 += "%s -- %s\n" % (_stock_id, _trade_date)
        content1 += bbb_mail_content()
        content1 += "A点: %s，涨幅: %.2f%%\n"  % (d_A, rt_A)
        content1 += "A点: %s，放量: %.2f%%+\n"  % (d_A, vr_A)
        content1 += "A点: 收盘突破: %d+\n"  % (break_days_A1)
        content1 += "A点: 成交突破: %d+\n"  % (break_days_A2)
        content1 += "+++++++++++++++++++++++++\n"
        info  = get_basic_info_all(_stock_id, _db)
        content1 += info

        subject = "bbb2(非标): %s -- %s" % (_stock_id, _trade_date)

        # bbb_save(_stock_id, _trade_date, expect_price, subject, content1, _db)

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


