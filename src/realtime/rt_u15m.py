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

#######################################################################
# 15min-unit ma-law
#######################################################################



def work_one(_stock_id, _row, _db):
    rs = False
    content = ""

    begin = get_micro_second()

    try:
        df = ts.get_k_data(_stock_id, ktype='15', autype='qfq')
    except Exception:
        log_error("warn:error: %s get_k_data exception!", _stock_id)
        return -4

    # calc cost time
    log_info("get_k_data [%s](%d) costs %d us", _stock_id, len(df), get_micro_second()-begin)

    if df is None :
        log_error("warn: stock %s is None, next", _stock_id)
        return -1

    if df.empty:
        log_error("warn: stock %s is empty, next", _stock_id)
        return -2



    rt_u15m_format_ref(_stock_id, df)

    # log_debug("+++++++++++++++++\n%s", df)


    rv = rt_u15m_case1(_stock_id, df, _db)
    if rv == 0:
        rs = True
        log_info("nice1: %s single pivot", _stock_id)
        return rs
    log_debug("-----------------------------------------")

    """
    rv = rt_u15m_case2(_stock_id, df, _db)
    if rv == 0:
        rs = True
        log_info("nice2: %s six-cross", _stock_id)
        return rs
    log_debug("-----------------------------------------")
    """


    return rs



# 单点支撑
def rt_u15m_case1(_stock_id, _detail_df, _db):
    to_mail = False

    # get B point
    B_UNIT = 10
    B_date_time, B_len = rt_u15m_recent_touch(_stock_id, _detail_df, B_UNIT, _db)
    if B_date_time == "":
        log_info("sorry: B: no recent touch point: %s, %d", B_date_time, B_len)
        return 1
    else:
        log_info("point-B: [%s, %d]", B_date_time, B_len)

    # get C, D point
    C_UNIT = 100
    C_date_time, C_len, D_date_time =  rt_u15m_pivot_touch(_stock_id, _detail_df, B_date_time, C_UNIT, _db)
    if C_len < C_UNIT:
        log_info("sorry: C: [%s, %d]", C_date_time, C_len)
        return 2
    else:
        log_info("point-C: [%s, %d]", C_date_time, C_len)
        log_info("point-D: [%s]", D_date_time)

    # 逐步阳线！
    A_red_unit, A_zt_unit = rt_u15m_red_units(_stock_id, _detail_df, B_date_time, B_len, _db)
    log_info("red-unit: %d, zt_unit: %d", A_red_unit, A_zt_unit)
    if A_red_unit < 4 or A_zt_unit < 4:
        log_info("sorry: after B: red too little: %d", A_red_unit)
        return 3

    # after B point
    A_upper_unit, A_below_unit = rt_u15m_after_units(_stock_id, _detail_df, B_date_time, _db)
    log_debug("upper: %d, under: %d", A_upper_unit, A_below_unit)


    # TODO: 巨大涨幅?
    # TODO: rpv?
    # TODO: rate(AB), rate(CD)

    # B,C重合
    rule1 =  str(B_date_time) == str(C_date_time)
    rule2 = B_len >= 2
    rule3 = A_upper_unit >= 2
    rule4 = C_len > 120
    if rule1 and rule2 and rule3 and rule4:
        to_mail = True
    else:
        log_debug("1: %s, 2: %s, 3: %s, 4: %s", rule1, rule2, rule3, rule4)


    if to_mail:
        curr_date = get_today()
        curr_time = get_time()
        subject = "malaw(15)-single: %s#%s" % (_stock_id, B_date_time)
        content  = "u15min-ma200-single-pivot\n"
        content += "B点: %s\n" % (B_date_time)
        content += "C点: %s\n" % (C_date_time)
        content += "D点: %s\n" % (D_date_time)
        content += "CD距离: %d+\n" % (C_len)
        content += "AB距离: %d+\n" % (B_len)
        content += "AB-upper: %d+\n" % (A_upper_unit)
        content += "AB-below: %d+\n" % (A_below_unit)
        content += "+++++++++++++++++++++++++\n"
        info  = get_basic_info_all(_stock_id, _db)
        content += info
        log_info("subject: \n%s", subject)
        log_info("mail: \n%s", content)
        saimail_dev(subject, content)
        saimail2(subject, content)
        return 0

    return 1

"""
        B_date_time, B_len, B_close_price = rt_u15m_recent_touch6(_stock_id, _detail_df, B_UNIT, _db)
        if B_date_time == "":
            log_info("sorry: B: no recent touch point: %s, %d", B_date_time, B_len)
            return 1
        else:
            is_touch6 = True
            log_info("point-B: [%s, %d, %.2f] touch", B_date_time, B_len, B_close_price)
"""

# 6线突破
#
def rt_u15m_case2(_stock_id, _detail_df, _db):
    to_mail = False
    is_cross6 = False
    is_touch6 = False

    # get B point
    # 先检查cross，再检查touch
    B_UNIT = 300
    B_date_time, B_len, B_close_price = rt_u15m_recent_cross6(_stock_id, _detail_df, B_UNIT, _db)
    if B_date_time == "":
        log_info("sorry: B: no recent touch point: %s, %d", B_date_time, B_len)
        return 1
    else:
        is_cross6 = True
        log_info("point-B: [%s, %d, %.2f] cross", B_date_time, B_len, B_close_price)

    B_idx = B_len

    # get A point
    A_date_time, A_vr50, A_vr10, A_rate, A_close_price = rt_u15m_volume_rate(_stock_id, _detail_df, B_date_time, B_idx, _db)
    # log_debug("point-A: [%s, vr50:%.2f, vr10:%.2f, rate:%.2f%%]", A_date_time, A_vr50, A_vr10, A_rate)
    if A_vr50 >= 2 and A_vr10 >= 1.4 and A_rate >= 0.0: # TODO: FIXME
        log_info("point-A: [%s, vr50:%.2f, vr10:%.2f, rate:%.2f%%] %s", A_date_time, A_vr50, A_vr10, A_rate, _stock_id)
    else:
        log_info("sorry: A: not volume surge: %.2f, %.2f, %.2f%%", A_vr50, A_vr10, A_rate)
        return 1

    # B点后高位徘徊
    B_unit1, B_unit2, B_unit3, upper_date_time, upper_price = rt_u15m_upper_wander_units(_stock_id, _detail_df, B_date_time, B_idx, B_close_price, _db)
    if B_unit1 >= 1 or B_unit2 >= 2:
        log_info("after-upper-wander: [%d, %d, %d; %s, %.2f] %s", B_unit1, B_unit2, B_unit3, upper_date_time, upper_price, _stock_id)
    else:
        log_info("sorry: B: not upper wander: %d, %d", B_unit1, B_unit2)
        return 1

    # 综合检查
    # 000560: 大放量，大涨幅，可降低高位徘徊要求
    # 000996: 小放量，要求持续阳线+阳柱 TODO
    if A_vr50 > 8:
        # 放巨量
        to_mail = True
    elif A_vr50 > 4:
        # 放量
        if B_unit1 >= 2 or B_unit2 >= 2:
            to_mail = True
    else:
        # 放小量
        if B_unit1 >= 3 and B_unit3 >= 3:
            to_mail = True

    if to_mail:
        log_info("bingo: %s surge with volume after %s", _stock_id, B_date_time)
        curr_date = get_today()
        curr_time = get_time()
        subject = "malaw(15)-cross6: %s#%s" % (_stock_id, B_date_time)
        content  = "u15min-ma200-cross6\n"
        content += "B点: %s\n" % (B_date_time)
        content += "A点: %s\n" % (A_date_time)
        content += "高位徘徊: %d\n" % (B_unit1)
        content += "最大放量: %.2f(+)\n" % (A_vr50)
        content += "+++++++++++++++++++++++++\n"
        info  = get_basic_info_all(_stock_id, _db)
        content += info
        log_info("subject: \n%s", subject)
        log_info("mail: \n%s", content)
        # saimail_dev(subject, content)
        # saimail2(subject, content)
        return 0

    return 1


# 新高
#
# X点往前突破的单位数
# case2
def rt_u15m_new_high_units(_stock_id, _detail_df, _till, _price,  _db):

    idx = 0
    TECH_IDX = 0

    unit = 0
    to_start = False

    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx
        stock_id   = row['stock_id']
        open_price = row['open_price']
        close_price= row['close_price']
        high_price = row['high_price']
        low_price  = row['low_price']
        last_close_price = row['last']
        pub_date_time =  row['pub_date_time']
        vol   = row['volume']

        # log_debug("----[%s, close: %.2f, ma200: %.2f]----", pub_date_time, close_price, ma200)
        # log_debug("----[%s, volum: %.2f, vma10: %.2f, vma50: %.2f]----", pub_date_time, vol, vol10, vol50)

        if to_start:
            if _price > close_price:
                unit += 1
            else:
                break

        if not to_start and str(_till) == str(pub_date_time):
            to_start = True

        idx += 1


    return unit


# 放巨量
#
# X点后3单位内
# 放的最大量
# 包含X点
# case2
def rt_u15m_volume_rate(_stock_id, _detail_df, _from, _from_idx, _db):

    idx = 0
    TECH_IDX = 0

    max_vr50 = 0.0
    max_vr10 = 0.0
    max_rate = 0.0
    max_date = ""
    max_close = 0.0

    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx
        stock_id   = row['stock_id']
        open_price = row['open_price']
        close_price= row['close_price']
        high_price = row['high_price']
        low_price  = row['low_price']
        last_close_price = row['last']
        pub_date_time =  row['pub_date_time']
        vol   = row['volume']
        ma200 = ref_ma200(TECH_IDX)
        vol10 = ref_vma10(TECH_IDX)
        vol50 = ref_vma50(TECH_IDX)
        rate  = (close_price - last_close_price) / last_close_price * 100

        if vol10 > 0:
            vr10  = vol / vol10
        else:
            vr10  = 0.0

        if vol50 > 0:
            vr50  = vol / vol50
        else:
            vr50  = 0.0

        diff = _from_idx - idx
        # log_debug("----[%s, close: %.2f, ma200: %.2f]----", pub_date_time, close_price, ma200)
        # log_debug("----[%s, volum: %.2f, vma10: %.2f, vma50: %.2f]----", pub_date_time, vol, vol10, vol50)


        # 只关心X点之后3个单位
        if diff >= 0 and diff <= 3:
            # log_info("vr10: %.2f, vr50: %.2f, rate: %.2f", vr10, vr50, rate)
            if vr50 > max_vr50:
                max_vr50 = vr50
                max_vr10 = vr10
                max_rate = rate
                max_date = pub_date_time
                max_close = close_price
                # log_debug("max-refresh: %s -- %.2f", max_date, max_vr50)
        else:
            pass

        if str(_from) == str(pub_date_time):
            break

        idx += 1


    return max_date, max_vr50, max_vr10, max_rate, max_close


# 高位徘徊
#
# X点后3单位内
# 高于X点收盘价的单位数
# 不包括自己 
# case2
def rt_u15m_upper_wander_units(_stock_id, _detail_df, _from, _from_idx, _price, _db):

    idx = 0
    TECH_IDX = 0

    unit1 = 0
    unit2 = 0 # ALT
    unit3 = 0 # rate

    max_close = 0.0
    max_date = ""

    alt_price = _price * 0.995

    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx
        stock_id   = row['stock_id']
        open_price = row['open_price']
        close_price= row['close_price']
        high_price = row['high_price']
        low_price  = row['low_price']
        last_close_price = row['last']
        pub_date_time =  row['pub_date_time']
        vol   = row['volume']
        ma200 = ref_ma200(TECH_IDX)
        rate  = (close_price - last_close_price) / last_close_price * 100

        if str(_from) == str(pub_date_time):
            break

        diff = _from_idx - idx
        # log_debug("----[%s, close: %.2f, ma200: %.2f]----", pub_date_time, close_price, ma200)
        # log_debug("----[%s, volum: %.2f, vma10: %.2f, vma50: %.2f]----", pub_date_time, vol, vol10, vol50)


        # 只关心X点之后3个单位
        if diff >= 0 and diff <= 3:
            # log_debug("[%s] -- close: %.2f, p1: %.2f, p2: %.2f", pub_date_time, close_price, _price, alt_price)
            if close_price >= _price:
                unit1 += 1

            if close_price >= alt_price:
                unit2 += 1

            if rate > 0:
                unit3 += 1

            if close_price > max_close:
                max_close = close_price
                max_date  = pub_date_time
        else:
            pass


        idx += 1


    return unit1, unit2, unit3, max_date, max_close

# 
# 寻找B点
# 开盘 -- 收盘
# case2
def rt_u15m_recent_cross6(_stock_id, _detail_df, _n1, _db):

    idx = 0
    TECH_IDX = 0
    touch_date_time = ""
    touch_close_price = 0.0
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx
        stock_id   = row['stock_id']
        open_price = row['open_price']
        close_price= row['close_price']
        high_price = row['high_price']
        low_price  = row['low_price']
        last_close_price = row['last']
        pub_date_time =  row['pub_date_time']

        ma200 = ref_ma200(TECH_IDX)
        ma5   = ref_ma5(TECH_IDX)
        ma10  = ref_ma10(TECH_IDX)
        ma20  = ref_ma20(TECH_IDX)
        ma30  = ref_ma30(TECH_IDX)
        ma60  = ref_ma60(TECH_IDX)

        # log_debug("-----[%s, %d, %.2f]----", pub_date_time, TECH_IDX, ma200)
        if idx >= _n1:
            break

        rule = close_price >= ma200 and open_price <= ma200 \
               and close_price >= ma60 and open_price <= ma60 \
               and close_price >= ma30 and open_price <= ma30 \
               and close_price >= ma20 and open_price <= ma20 \
               and close_price >= ma10 and open_price <= ma10 \
               and close_price >= ma5  and open_price <= ma5
        if rule:
            # log_info("nice: %s cross-6", pub_date_time)
            touch_date_time = pub_date_time
            touch_close_price = close_price
            break

        idx += 1


    return touch_date_time, idx, touch_close_price

# 寻找B点
# 最低 -- 最高
# case2
def rt_u15m_recent_touch6(_stock_id, _detail_df, _n1, _db):

    idx = 0
    TECH_IDX = 0
    touch_date_time = ""
    touch_close_price = 0.0
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx
        stock_id   = row['stock_id']
        open_price = row['open_price']
        close_price= row['close_price']
        high_price = row['high_price']
        low_price  = row['low_price']
        last_close_price = row['last']
        pub_date_time =  row['pub_date_time']

        ma200 = ref_ma200(TECH_IDX)
        ma5   = ref_ma5(TECH_IDX)
        ma10  = ref_ma10(TECH_IDX)
        ma20  = ref_ma20(TECH_IDX)
        ma30  = ref_ma30(TECH_IDX)
        ma60  = ref_ma60(TECH_IDX)

        # log_debug("-----[%s, %d, %.2f]----", pub_date_time, TECH_IDX, ma200)
        if idx >= _n1:
            break

        rule = close_price >= ma200 and low_price <= ma200 \
               and close_price >= ma60 and low_price <= ma60 \
               and close_price >= ma30 and low_price <= ma30 \
               and close_price >= ma20 and low_price <= ma20 \
               and close_price >= ma10 and low_price <= ma10 \
               and close_price >= ma5  and low_price <= ma5

        if rule:
            # log_info("nice: %s touch-6", pub_date_time)
            touch_date_time   = pub_date_time
            touch_close_price = close_price
            break

        idx += 1


    return touch_date_time, idx, touch_close_price


# 寻找B点
# case1
def rt_u15m_recent_touch(_stock_id, _detail_df, _n1, _db):

    idx = 0
    TECH_IDX = 0
    touch_date_time = ""
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx
        stock_id   = row['stock_id']
        open_price = row['open_price']
        close_price= row['close_price']
        high_price = row['high_price']
        low_price  = row['low_price']
        last_close_price = row['last']
        pub_date_time =  row['pub_date_time']
        ma200 = ref_ma200(TECH_IDX)

        # log_debug("-----[%s, %d, %.2f]----", pub_date_time, TECH_IDX, ma200)
        if idx >= _n1:
            break

        if high_price >= ma200 and low_price <= ma200:
            log_info("nice: %s touched", pub_date_time)
            touch_date_time = pub_date_time
            break

        idx += 1


    return touch_date_time, idx


# 持续上涨
#
# X点后5单位内
# 上涨个数、阳柱个数
# 不包括自己 
# case1
def rt_u15m_red_units(_stock_id, _detail_df, _from, _from_idx, _db):

    idx = 0
    TECH_IDX = 0

    unit1 = 0 # rate
    unit2 = 0 # zt

    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx
        stock_id   = row['stock_id']
        open_price = row['open_price']
        close_price= row['close_price']
        high_price = row['high_price']
        low_price  = row['low_price']
        last_close_price = row['last']
        pub_date_time =  row['pub_date_time']
        vol   = row['volume']
        ma200 = ref_ma200(TECH_IDX)
        rate  = (close_price - last_close_price) / last_close_price * 100
        zt    = (close_price - open_price) / last_close_price * 100

        if str(_from) == str(pub_date_time):
            break

        diff = _from_idx - idx


        # 只关心X点之后5个单位
        if diff >= 0 and diff <= 5:
            if rate > 0:
                unit1 += 1

            if zt > 0:
                unit2 += 1

        else:
            pass


        idx += 1


    return unit1, unit2

# 寻找C点
# B点往前，存在点C，使得有N单位在ma200之上。
# BC可以同点
def rt_u15m_pivot_touch(_stock_id, _detail_df, _till, _n1, _db):

    idx = 0
    unit = 0
    TECH_IDX = 0

    to_start = False

    pub_date_time = ""
    touch_date_time = ""
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx
        stock_id   = row['stock_id']
        open_price = row['open_price']
        close_price= row['close_price']
        high_price = row['high_price']
        low_price  = row['low_price']
        last_close_price = row['last']
        pub_date_time =  row['pub_date_time']
        ma200 = ref_ma200(TECH_IDX)

        if str(_till) == str(pub_date_time):
            to_start = True

        # log_debug("-----[%s, %d, %.2f]----", pub_date_time, TECH_IDX, ma200)

        if to_start:
            if high_price >= ma200 and low_price <= ma200:
                touch_date_time, idx, unit = rt_u15m_before_upper_units(_stock_id, _detail_df, pub_date_time, _db)
                if unit > _n1:
                    log_info("nice: pivot found: %s, %d", pub_date_time, unit)
                    break
            else:
                pass

        if idx >= _n1:
            break

        if high_price >= ma200 and low_price <= ma200:
            log_info("nice: %s touched", pub_date_time)
            touch_date_time = pub_date_time
            break

        idx += 1


    return pub_date_time, unit, touch_date_time

#
# X点往前，在ma200之上的单位数
#
def rt_u15m_before_upper_units(_stock_id, _detail_df, _till, _db):

    idx = 0
    unit = 0

    to_start = False

    TECH_IDX = 0
    touch_date_time = ""
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx
        stock_id   = row['stock_id']
        open_price = row['open_price']
        close_price= row['close_price']
        high_price = row['high_price']
        low_price  = row['low_price']
        last_close_price = row['last']
        pub_date_time =  row['pub_date_time']
        ma200 = ref_ma200(TECH_IDX)

        # log_debug("-----[%s, %d, %.2f]----", pub_date_time, TECH_IDX, ma200)

        if to_start:
            if low_price > ma200:
                unit += 1
                touch_date_time = pub_date_time
            else:
                break

        if str(_till) == str(pub_date_time):
            to_start = True


        idx += 1


    return touch_date_time, idx, unit


# X点往后
# 最低价 > ma200的单位数
# 最高价 < ma200的单位数
def rt_u15m_after_units(_stock_id, _detail_df, _from, _db):

    idx = 0
    TECH_IDX = 0
    below_unit = 0
    upper_unit = 0
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx
        stock_id   = row['stock_id']
        open_price = row['open_price']
        close_price= row['close_price']
        high_price = row['high_price']
        low_price  = row['low_price']
        last_close_price = row['last']
        pub_date_time =  row['pub_date_time']
        ma200 = ref_ma200(TECH_IDX)

        # log_debug("-----[%s, %d, %.2f]----", pub_date_time, TECH_IDX, ma200)

        if low_price > ma200:
            upper_unit += 1

        if high_price < ma200:
            below_unit += 1

        if str(_from) == str(pub_date_time):
            break

        idx += 1


    return upper_unit, below_unit




def rt_u15m_format_ref(_stock_id, _detail_df):

    _detail_df['close_price'] = _detail_df['close']
    _detail_df['open_price']  = _detail_df['open']
    _detail_df['high_price']  = _detail_df['high']
    _detail_df['low_price']   = _detail_df['low']
    _detail_df['total']       = _detail_df['volume']
    _detail_df['stock_id']    = _detail_df['code']
    _detail_df['pub_date_time'] = _detail_df['date']

    # get last
    _detail_df['last'] = calc_last(_detail_df['close'])


    rt_u15m_dynamic_calc_tech(_detail_df)

    # _detail_df.sort_index(ascending=False, inplace=True)

    _detail_df.sort_index(ascending=False, inplace=True)
    _detail_df.reset_index(drop=True, inplace=True)

    # log_debug("#################\n%s", _detail_df)

    # _detail MUST be sorted
    rv = ref_init4(_detail_df)
    if rv < 0:
        log_error("error: ref_init4")
        return -1


    ref_set_tech5()

    """
    log_debug("000: open: %.2f, close: %.2f", ref_open(0), ref_close(0))
    log_debug("001: open: %.2f, close: %.2f", ref_open(1), ref_close(1))
    log_debug("002: open: %.2f, close: %.2f", ref_open(2), ref_close(2))

    log_debug("000: ma5: %.2f, ma10: %.2f", ref_ma5(0), ref_ma10(0))
    log_debug("001: ma5: %.2f, ma10: %.2f", ref_ma5(1), ref_ma10(1))
    log_debug("002: ma5: %.2f, ma10: %.2f", ref_ma5(2), ref_ma10(2))

    log_debug("000: ma20: %.2f, ma200: %.2f", ref_ma20(0), ref_ma200(0))
    log_debug("001: ma20: %.2f, ma200: %.2f", ref_ma20(1), ref_ma200(1))
    log_debug("002: ma20: %.2f, ma200: %.2f", ref_ma20(2), ref_ma200(2))

    log_debug("000: vma10: %.2f, vma50: %.2f", ref_vma10(0), ref_vma50(0))
    log_debug("001: vma10: %.2f, vma50: %.2f", ref_vma10(1), ref_vma50(1))
    log_debug("002: vma10: %.2f, vma50: %.2f", ref_vma10(2), ref_vma50(2))
    """


    return 0


def rt_u15m_dynamic_calc_tech(_df):

    sc = _df['close_price']

    # sma5
    se = calc_sma(sc, 5)
    _df['ma5'] = se;

    # sma10
    se = calc_sma(sc, 10)
    _df['ma10'] = se;

    # sma20
    se = calc_sma(sc, 20)
    _df['ma20'] = se;

    # sma30
    se = calc_sma(sc, 30)
    _df['ma30'] = se;

    # sma60
    se = calc_sma(sc, 60)
    _df['ma60'] = se;

    # sma120
    se = calc_sma(sc, 120)
    _df['ma120'] = se;

    # sma150
    se = calc_sma(sc, 150)
    _df['ma150'] = se;

    # sma200
    se = calc_sma(sc, 200)
    _df['ma200'] = se;

    # macd: ema(12), ema(26), diff, dea(9), macd
    sm, sn, sd, se, sa = calc_macd_list0(sc, 12, 26, 9)
    _df['ema12'] = sm;
    _df['ema26'] = sn;
    _df['diff']  = sd;
    _df['dea']   = se;
    _df['macd']  = sa;

    sv = _df['total']

    # volume - sma5
    se = calc_sma(sv, 5)
    _df['vma5'] = se;

    se = calc_sma(sv, 10)
    _df['vma10'] = se;

    se = calc_sma(sv, 50)
    _df['vma50'] = se;

    return 0



def xxx(_db):
    has_noticed = {}

    if sai_is_product_mode():
        last_date = get_date_by(-1)
        last_date = "2017-08-30"
        last_date = get_newest_trade_date(_db)
    else:
        last_date = "2017-09-05"


    log_info("date: [%s]", last_date)

    list_df = get_u15m_list(last_date, _db) 
    if list_df is None:
        log_error("error: get list failure")
        return -1
    elif list_df.empty:
        log_error("[%s] no u15m data", last_date)
        return 1
    else:
        log_debug("list df: \n%s", list_df)

    end_time  = '15:05:00'
    lun_time1 = '11:40:00'
    lun_time2 = '13:00:00'

    # TODO: delete me!
    # end_time  = '23:05:00'
    end_time  = '15:05:00'
    lun_time1 = '01:40:00'
    lun_time2 = '03:00:00'

    counter  = 0
    while 1:
        counter = counter + 1

        curr = get_time()

        # 中午休息
        if curr >= lun_time1 and curr <= lun_time2:
            log_info("'%s' means noon time", curr)
            time.sleep(300)
            continue

        log_info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

        begin = get_micro_second()

        # 
        for row_index, row in list_df.iterrows():
            stock_id   = row['stock_id']
            log_debug("new<<<------------[%s]------------------", stock_id)

            if has_noticed.has_key(stock_id):
                log_debug("%s already done", stock_id)
                continue
            else:
                has_trigger = work_one(stock_id, row, _db)
                if has_trigger:
                    has_noticed[stock_id] = 1
                    log_debug("mark: %s as has done", stock_id)
            # for

        log_info("one-loop costs %d us", get_micro_second()-begin)

        # 当日结束
        curr = get_time()
        if curr >= end_time:
            log_info("'%s' means end today", curr)
            break

        # TODO: delete me
        break

        time.sleep(600)
        # time.sleep(20)

        # while


    return 0




def work():
    db = db_init()

    xxx(db)

    db_end(db)


def get_u15m_list(_trade_date, _db):


    # CASE2
    sql = "select distinct stock_id from tbl_day a \
where  a.pub_date  = '%s' \
and    (a.stock_id in ('000717', '300064', '000560', '600516', '600804', '600405', '002192', '300457') or a.stock_id in ('000996')) \
order by 1" % (_trade_date) # case2


    # CASE1
    sql = "select distinct stock_id from tbl_day a \
where  a.pub_date  = '%s' \
and    (a.stock_id in ( '000807') or a.stock_id in ('002850')) \
order by 1" % (_trade_date) # case1

    # real
    sql = "select distinct stock_id from tbl_day a \
where  a.pub_date  = '%s' \
order by 1" % (_trade_date)



    log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        # df.set_index("stock_id", inplace=True)
        return df



#######################################################################

def main():
    sailog_set("rt_u15m.log")

    log_info("let's begin here!")

    if sai_is_product_mode():
        if today_is_weekend():
            log_info("today is weekend, exit")
            # work()
        else:
            log_info("today is workday, come on")
            work()
    else:
        log_debug("test mode")
        work()

    log_info("main ends, bye!")
    return

main()

#######################################################################


# u15m.py
