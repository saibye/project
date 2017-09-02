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

#######################################################################
#
#######################################################################

g_detail_fetched = 120
g_detail_used    = 70


def CwH_analyzer(_stock_id, _trade_date, _my_df, _used_len, _db):
    global g_detail_fetched 

    lowest   = 0
    mailed = 0
    content1 = "Cup with Handle\n"
    to_mail = False

    idx    = 0
    TECH_IDX = 0

    BACK1  = -10.0
    BACK2  = -4.5

    BACK1  = -8.6
    BACK2  = -1.7

    RISE1  = 10 # 柳钢股份
    RISE2  = 4

    RISE1  = 7.3 # 海康威视
    RISE2  = 3

    VR1    = 40
    VR2    = 50

    BACK_AB = -13.5

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

    for row_index, row in _my_df.iterrows():
        TECH_IDX = _used_len - idx - 1

        close_price      = row['close_price']
        high_price       = row['high_price']
        last_close_price = row['last']
        open_price       = row['open_price']
        vol              = row['total']
        pub_date         = row['pub_date']
        rate = (close_price - last_close_price) / last_close_price
        zt   = (close_price - open_price) / last_close_price
        if ref_vma50(TECH_IDX) > 0:
            vr = (vol / ref_vma50(TECH_IDX) - 1) * 100
        else:
            vr = 0

        # log_debug("--------------------%s-------------------", pub_date)

        if vol > v_max:
            v_max  = vol
            c_vmax = close_price

        if close_price > c_max:
            c_max = close_price
            i_max = idx

        if close_price < c_min:
            c_min = close_price
            i_min = idx

        # 寻找A点：阳柱+上涨
        if not got_A:
            # log_debug("searching A-point: %.2f", vr)
            if zt > 0 and rate > 0 and vr > VR1 \
                and close_price > ref_ma10(TECH_IDX) \
                and close_price > ref_ma20(TECH_IDX):
                # 最大量，最高点
                if vol > v_A: # price?
                    v_A = vol
                    p_A = close_price
                    i_A = idx
                    d_A = pub_date
                    rt_A= rate
                    vr_A= vr
                    log_info("放量new-A: %s: %.2f, %.2f, %d", pub_date, v_A, p_A, i_A)
                    log_info("vma10: %.2f, vma50: %.2f", ref_vma10(TECH_IDX), ref_vma50(TECH_IDX))
                    # 发现新的A时，同时更新B点
                    p_B = close_price
                    v_B = vol
                    i_B = idx
                    d_B = pub_date
        else:
            # log_debug("A-point got: [%s]", d_A)
            pass

        # 寻找B点
        B_updated = False
        if not got_B and v_A > 0:
            if close_price < p_B:
                p_B = close_price
                v_B = vol
                i_B = idx
                d_B = pub_date
                B_updated = True
                log_info("B-updated: %s: 收:%.2f", pub_date, p_B)

        # 确定A点, 根据回撤Y1幅度
        if not got_A and B_updated:
            # log_debug("尝试确定A点")
            if p_B > 0 and p_A > 0:
                y1 = (p_B / p_A - 1) * 100.00
                log_info("y1: %s: %.2f, %.2f, %.2f", pub_date, p_B, p_A, y1)
                if y1 < BACK1:
                    log_info("[%s]: A->B 深幅回撤y1: %.2f", pub_date, y1)
                    log_info("nice+++ %s A点确定: %s", _stock_id, d_A)
                    got_A = True
                    # 从此点开始，寻找B点
                    p_B = close_price
                    v_B = vol
                    i_B = idx
                    d_B = pub_date
                    rt_B= rate
                    vr_B= vr
                    log_info("B-born: %s: 收:%.2f", pub_date, p_B)
                else:
                    # log_info("回撤不够: %.2f", y1)
                    pass
        else:
            # log_debug("A点已定")
            pass

        if got_A and not got_B and i_max > i_A:
            u_A = (c_max / p_A - 1) * 100
            # log_debug("u_A: %.2f", u_A)
            if u_A > 5:
                log_info("error: DIV1 %s, %.2f", _stock_id, u_A)
                return -1

        # 寻找C点
        C_updated = False
        if not got_C and got_A:
            # log_debug("searching C-point")
            if zt > 0 and rate > 0:
                # 最大量，最高点
                if vol > v_C: # price?
                    v_C = vol
                    p_C = close_price
                    i_C = idx
                    d_C = pub_date
                    C_updated = True
                    rt_C= rate
                    vr_C= vr
                    log_info("放量new-C: %s: %.2f, %.2f", pub_date, v_C, p_C)
                    # 发现新的C时，同时更新D点
                    p_D = close_price
                    v_D = vol
                    i_D = idx
                    d_D = pub_date
        else:
            # log_debug("not start C frame")
            pass

        # 确定B点
        # by反弹Z1幅度
        if got_A and not got_B and C_updated:
            if p_C > 0 and p_B > 0:
                z1 = (p_C / p_B - 1) * 100.00
                log_info("z1: %s: %.2f, %.2f, %.2f", pub_date, p_B, p_C, z1)
                if z1 > RISE1:
                    log_info("[%s]: B->C 形成右壁: %.2f%%", pub_date, z1)
                    log_info("nice+++确定B点%s", d_B)
                    AB    = i_B - i_A
                    if AB > 25 or AB < 11:
                        log_info("sorry: AB exceeds! %s -- %d", _stock_id, AB)
                        return i_B
                    dv_AB = (p_B / p_A - 1) * 100
                    log_info("A->B %s division: %.3f",  _stock_id, dv_AB)
                    if dv_AB < BACK_AB:
                        log_info("sorry: A-B BAD! %s -- division: %.3f", _stock_id, dv_AB)
                        return -1
                    got_B = True
                else:
                    log_info("B->C反弹不够: %.2f", z1)
        else:
            pass

        # 寻找D点
        # D是第二低点
        # 目标是为了确定C点
        D_updated = False
        if not got_D and v_C > 0 and got_B:
            if p_D > close_price:
                p_D = close_price
                v_D = vol
                i_D = idx
                d_D = pub_date
                rt_D= rate
                vr_D= vr
                D_updated = True
                log_info("D: %s: 收:%.2f", pub_date, p_D)

        # 确定C点
        # 根据回撤Y2幅度
        if not got_C and got_B and D_updated:
            # log_debug("尝试确定C点")
            if p_D > 0 and p_C > 0:
                y2 = (p_D / p_C - 1) * 100.00
                CD = idx - i_C
                log_info("y2: %s: %.2f, %.2f, %.2f", pub_date, p_D, p_C, y2)
                if y2 < BACK2 :
                    log_info("[%s]: C->D 浅幅回撤y2: %.2f", pub_date, y2)
                    log_info("nice+++C点确定: %s", d_C)
                    got_C = True
                    BC = i_C - i_B
                    log_info("frame BC: %d", BC)
                    # if BC < 10 or BC > 25:
                    if BC < 10 or BC > 29:
                        log_info("sorry: BC BAD! %s -- BC: %d", _stock_id, BC)
                        return -1
                    dv_AC = p_C / p_A
                    log_info("A-C  %s -- division: %.3f", _stock_id, dv_AC)
                    if dv_AC < 0.88 or dv_AC > 1.08:
                        log_info("sorry: A-C BAD! %s -- division: %.3f", _stock_id, dv_AC)
                        return -1
                    if vr_C < 50:
                        log_info("sorry: C放量不足 %s -- %.3f", _stock_id, vr_C)
                        return -1
                    # 从此点开始，继续寻找D点
                    p_D = close_price
                    v_D = vol
                    i_D = idx
                    d_D = pub_date
                    log_info("D-born: %s: 收:%.2f", pub_date, p_D)
                else:
                    log_info("y2回撤不够: %.2f", y2)
        else:
            # log_debug("C点已定")
            pass

        # 寻找E点
        # 目标：确定D点
        E_updated = False
        if not got_E and got_C:
            # log_debug("searching E-point")
            if zt > 0 and rate > 0:
                # 最大量，最高点
                if vol > v_E: # price?
                    E_updated = True
                    v_E = vol
                    p_E = close_price
                    i_E = idx
                    d_E = pub_date
                    rt_E= rate
                    vr_E= vr
                    log_info("放量new-E: %s: %.2f, %.2f", pub_date, v_E, p_E)
        else:
            # log_debug("not start E frame")
            pass

        # 确定D点, 根据反弹Z2幅度
        if not got_D and got_C and E_updated:
            if p_D > 0 and p_E > 0:
                CD = i_D - i_C
                if CD > 7:
                    log_info("sorry: CD too long: %s, %d", _stock_id, CD)
                    return -1
                z2 = (p_E / p_D - 1) * 100.00
                log_info("z2: %s: %.2f, %.2f, %.2f, %.2f", pub_date, p_D, p_E, z2, vr)
                if z2 > RISE2 and vr > VR2 and high_price > p_D and CD > 2:
                    log_info("[%s]: 确定D点, D->E 形成突破: %.2f%%", pub_date, z2)
                    log_info("nice+++:确定D点%s", d_D)
                    log_info("vol: %.3f", ref_vol(TECH_IDX))
                    got_D = True
                    break
                else:
                    log_info("反弹不够: %.2f", z2)
        else:
            pass

        idx  = idx + 1

    if got_D:
        log_info("bingo: %s break at %s", _stock_id, d_E)
        log_info("A: %s", d_A)
        log_info("B: %s", d_B)
        log_info("C: %s", d_C)
        log_info("D: %s", d_D)
        log_debug("XXX: %s", _stock_id)
        log_debug("XXX: A->B: %.2f", dv_AB)
        log_debug("XXX: A->C: %.2f", dv_AC)
        log_debug("XXX: AB: %d", AB)
        log_debug("XXX: BC: %d", BC)
        log_debug("XXX: CD: %d", CD)
        log_debug("XXX: C放量: %.2f", vr_C)
        content1 += "突破: %s, 放量(+): %.2f%%\n"  % (d_E, vr_E)
        content1 += "A点: %s,  放量(+): %.2f%%\n"  % (d_A, vr_A)
        content1 += "B点: %s,  缩量(-): %.2f%%\n"  % (d_B, vr_B)
        content1 += "C点: %s,  放量(+): %.2f%%\n"  % (d_C, vr_C)
        content1 += "D点: %s,  缩量(-): %.2f%%\n"  % (d_D, vr_D)
        content1 += "+++++++++++++++++++++++++\n"
        info  = get_basic_info_all(_stock_id, _db)
        content1 += info

        if str(d_E) == str(_trade_date):
            to_mail = True
            log_info("MAIL: %s", d_E)
        else:
            log_info("obsolete: %s(%s) : %s(%s)", d_E, type(d_E), _trade_date, type(_trade_date))


    if to_mail:
        subject = "CwH0: %s -- %s" % (_stock_id, _trade_date)
        log_info(subject)
        log_info("mail:\n%s", content1)
        if sai_is_product_mode():
            mailed = 1
            saimail_dev(subject, content1)
    else:
        log_info("sorry1: %s, %s", _stock_id, _trade_date)

    return 0



def CwH_exec_algo(_max_date, _detail_df, _db):

    # 涨幅
    rate = (ref_close(0) - ref_close(1)) / ref_close(1) * 100
    # log_debug("涨幅: %.2f", rate)

    # 柱体
    zt = (ref_close(0) - ref_open(0)) / ref_close(1) * 100
    # log_debug("柱体: %.2f", zt) 

    # 成交量比1: vol/ref_vma5(3)
    vol_rate1 = ref_vol(0) / ref_vma5(3)
    # log_debug("当前量比1: %.3f", vol_rate1)

    # 成交量比2
    vol_rate2 = ref_vol(0) / ref_vma10(5)
    # log_debug("当前量比2: %.3f", vol_rate2)

    # ma60 bigger
    ma60_bigger = ref_ma60(0) >= ref_ma60(10) and ref_ma60(5) >= ref_ma60(15)

    # ma10 diviate
    ma10_divia =  (ref_open(0) - ref_ma10(0)) / ref_ma10(0) * 100

    # today
    this_close = ref_close(0)
    this_vol   = ref_vol(0)

    # 收盘价突破
    # log_debug("close: [%.2f]", this_close)
    days1 = get_CwH_max_price_days(_detail_df,  this_close)
    # log_debug("价格突破天数days1: %d", days1)

    # 收盘价突破 -- 容错
    days2 = get_CwH_almost_max_price_days(_detail_df,  this_close)
    # log_debug("价格突破天数days2: %d", days2)

    # 成交量突破
    # log_debug("volume: [%.2f]", this_vol)
    days3 = get_CwH_max_volume_days(_detail_df, this_vol)
    # log_debug("成交量突破天数days3: %d", days3)

    # 阳柱成交量大 sum(red) / sum(green) > 2.5
    n = 30
    sum1, sum2 = sum_CwH_detail(_detail_df, n, _db)
    # log_debug("red-sum: %.3f", sum1)
    # log_debug("gre-sum: %.3f", sum2)
    vol_rate3 = -1
    if sum1 > 0 and sum2 > 0:
        vol_rate3 = sum1 / sum2
        # log_debug("合计量比vol_rate3: %.3f", vol_rate3)

    return rate, zt, days1, days2, days3, vol_rate1, vol_rate2, vol_rate3, ma60_bigger, ma10_divia


def sum_CwH_detail(_detail_df, _days, _db):

    counter = 0
    sum1 = 0.0
    sum2 = 0.0
    for row_index, row in _detail_df.iterrows():
        close_price = row['close_price']
        open_price  = row['open_price']
        vol         = row['total']

        if close_price > open_price:
            # log_debug("<%s> red: %.3f", row_index, vol)
            sum1 += vol
        elif close_price < open_price:
            # log_debug("<%s> gre: %.3f", row_index, vol)
            sum2 += vol
        else:
            pass
        counter = counter + 1
        if counter >= _days:
            # log_debug("counter: reach: %d", _days)
            break

    return sum1, sum2

"""
价格突破前高
"""
def get_CwH_max_price_days(_detail_df, _max_price):
    counter = 0
    for row_index, row in _detail_df.iterrows():
        if counter == 0:
            counter = 1
            continue

        close_price = row['close_price']
        if close_price <= _max_price:
            counter += 1
            # log_debug("[%s][%.3f] < [%.3f]", row['pub_date'], close_price, _max_price)
        else:
            break
    return counter

"""
价格突破前高 -- 容错
"""
def get_CwH_almost_max_price_days(_detail_df, _max_price):
    counter = 0
    for row_index, row in _detail_df.iterrows():
        if counter == 0:
            counter = 1
            continue

        close_price = row['close_price']
        if close_price <= _max_price*1.01:
            counter += 1
            # log_debug("[%s][%.3f] < [%.3f]", row['pub_date'], close_price, _max_price)
        else:
            break
    return counter

"""
量突破前高
"""
def get_CwH_max_volume_days(_detail_df, _max_volume):
    counter = 0
    for row_index, row in _detail_df.iterrows():
        if counter == 0:
            counter = 1
            continue

        volume = row['total']
        if volume < _max_volume:
            counter += 1
            # log_debug("[%s][%.3f] < [%.3f]", row['pub_date'], close_price, _max_price)
        else:
            break
    return counter



def CwH_dynamic_calc_tech(_df):

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


def CwH_format_ref(_stock_id, _detail_df):

    # _detail MUST be sorted
    rv = ref_init4(_detail_df)
    if rv < 0:
        log_error("error: ref_init4")
        return -1

    _detail_df.sort_index(ascending=False, inplace=True)
    CwH_dynamic_calc_tech(_detail_df)
    _detail_df.sort_index(ascending=True,  inplace=True)

    ref_set_tech5()

    """
    log_debug("ref0:  [%.3f, %.3f] -- vol:[%.3f]", ref_open(0), ref_close(0), ref_vol(0))
    log_debug("ref1:  [%.3f, %.3f] -- vol:[%.3f]", ref_open(1), ref_close(1), ref_vol(1))
    log_debug("ref2:  [%.3f, %.3f] -- vol:[%.3f]", ref_open(2), ref_close(2), ref_vol(2))

    log_debug("ma5/10 [%.3f, %.3f] - vma[%.3f, %.3f]", ref_ma5(0), ref_ma10(0), ref_vma5(0), ref_vma10(0))
    log_debug("ma5/10 [%.3f, %.3f] - vma[%.3f, %.3f]", ref_ma5(1), ref_ma10(1), ref_vma5(1), ref_vma10(1))
    log_debug("ma5/10 [%.3f, %.3f] - vma[%.3f, %.3f]", ref_ma5(2), ref_ma10(2), ref_vma5(2), ref_vma10(2))

    log_debug("macd0: [%.3f] [%.3f], [%.3f]", ref_macd(0), ref_diff(0), ref_dea(0))
    log_debug("macd1: [%.3f] [%.3f], [%.3f]", ref_macd(1), ref_diff(1), ref_dea(1))
    log_debug("macd2: [%.3f] [%.3f], [%.3f]", ref_macd(2), ref_diff(2), ref_dea(2))
    """

    return 0


def get_CwH_detail(_stock_id, _pub_date, _n, _db):
    sql = "select stock_id, pub_date, open_price, close_price, \
deal_total_count total, last_close_price last, \
high_price, low_price \
from tbl_day a \
where a.stock_id  = '%s' and a.pub_date <= '%s' \
order by pub_date desc limit %d" % (_stock_id, _pub_date, _n)

    # log_debug("detail-sql:\n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        return df


def get_CwH_stock_list(_till, _db):
    sql = "select distinct stock_id from tbl_day \
where pub_date = \
(select max(pub_date) from tbl_day \
where pub_date <= '%s')" % (_till)

    # log_debug("stock list sql:\n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _till)
        return None
    else:
        df.set_index("stock_id", inplace=True)
        return df


def CwH_work_one_day_stock(_stock_id, _till,  _db):

    global g_detail_fetched 
    global g_detail_used

    log_debug("================================================")
    # 获取明细数据
    # 之前n1单位的交易数据
    n1 = g_detail_fetched
    detail_df = get_CwH_detail(_stock_id, _till, n1, _db);
    if detail_df is None:
        log_info("[%s, %s] detail is none", _stock_id, _till)
        return -1
    elif detail_df.empty:
        log_debug("detail_df is empty: [%d]", len(detail_df))
        return 1
    else:
        # log_debug("n1: len[%d]", len(detail_df))
        pass

    length = len(detail_df)
    if length < g_detail_used:
        log_info("data-not-enough: %s: %d", _stock_id, length)
        return 1

    # 格式化数据
    rv = CwH_format_ref(_stock_id, detail_df)
    if rv < 0:
        log_error("error: CwH_format_ref: %s", _stock_id)
        return -1

    used_len = g_detail_used
    my_df = detail_df.sort_index(ascending=False).tail(used_len)
    rv = CwH_analyzer(_stock_id, _till, my_df, used_len, _db)
    if rv < 0:
        log_error("error: CwH_analyzer1: %s", _stock_id)
        return -1
    elif rv > 0:
        # 2017-7-21
        left_len = used_len - (rv+1)
        if left_len <= 10:
            log_error("AGAIN: left too short: %d", left_len)
            return -1
        log_info("again: CwH_analyzer0: %s: %d: %d", _stock_id, rv, left_len)
        my_df = my_df.tail(left_len)
        rv = CwH_analyzer(_stock_id, _till, my_df, used_len, _db)
        if rv < 0:
            log_error("error: CwH_analyzer2: %s", _stock_id)
            return -1

    return 0


def CwH_work_one_day(_till_date, _db):

    log_info("date: %s", _till_date)

    list_df = get_CwH_stock_list(_till_date, _db)
    if list_df is None:
        log_error("error: get_CwH_stock_list failure")
        return -1
    else:
        # log_debug("list df:\n%s", list_df)
        pass

    for row_index, row in list_df.iterrows():

        stock_id = row_index

        log_debug("[%s]------------------", stock_id)

        CwH_work_one_day_stock(stock_id, _till_date, _db)


def regression(_db):

    # all
    max_date = "2017-06-26"
    days = 200


    # 600191 @ 2017-07-05
    max_date = "2017-07-05"
    days = 1

    # 000488  @ 2017-06-26
    max_date = "2017-06-26"
    days = 1

    # XXX
    max_date = "2017-07-20"
    days = 30

    log_info("regress")

    date_df = get_recent_pub_date(max_date, days, _db)
    if date_df is None:
        log_error("error: get_recent_pub_date failure")
        return -1
    else:
        date_df.set_index("pub_date", inplace=True)

    for row_index, row in date_df.iterrows():
        till_date = row_index
        log_debug("[%s]------------------", till_date)
        CwH_work_one_day(till_date, _db)

    return 0


def work():
    db = db_init()

    if sai_is_product_mode():
        till_date = get_date_by(0)
        till_date = get_newest_trade_date(db)
        # till_date = "2017-01-18"
        log_info("till_date: %s", till_date)
        CwH_work_one_day(till_date, db)

        """
        # 柳钢股份 case1 init
        till_date = "2016-11-18"
        stock_id  = "601003"
        CwH_work_one_day_stock(stock_id, till_date, db)


        # 海康威视 3
        till_date = "2017-01-18"
        stock_id  = "002415"
        CwH_work_one_day_stock(stock_id, till_date, db)

        # 晨鸣纸业 4
        till_date = "2017-06-28"
        stock_id  = "000488"
        CwH_work_one_day_stock(stock_id, till_date, db)

        # 盐田港 5: FAIL
        till_date = "2017-04-06"
        stock_id  = "000088"
        CwH_work_one_day_stock(stock_id, till_date, db)

        # 华资实业 6 done
        till_date = "2017-07-06"
        stock_id  = "600191"
        CwH_work_one_day_stock(stock_id, till_date, db)

        # 天茂集团 7 done
        till_date = "2017-07-05"
        stock_id  = "000627"
        CwH_work_one_day_stock(stock_id, till_date, db)

        # 珠海港 2 TODO
        till_date = "2017-04-10"
        stock_id  = "000507"
        CwH_work_one_day_stock(stock_id, till_date, db)

        # 东湖高新 8 TODO: high = vol*close_price
        till_date = "2017-07-05"
        stock_id  = "600133"
        CwH_work_one_day_stock(stock_id, till_date, db)

        # 沧州大化 9  TODO: fail: dynamic search
        till_date = "2017-07-10"
        stock_id  = "600230"
        CwH_work_one_day_stock(stock_id, till_date, db)

        # 敦煌种业10  TODO
        till_date = "2017-07-18"
        stock_id  = "600354"
        CwH_work_one_day_stock(stock_id, till_date, db)
        """

    else:
        regression(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("cwh.log")

    log_info("let's begin here!")

    if sai_is_product_mode():
        if today_is_weekend():
            log_info("today is weekend, exit")
            work()
        else:
            log_info("today is workday, come on")
            work()
    else:
        log_debug("test mode")
        work()

    log_info("main ends, bye!")

    return

#######################################################################

main()

#######################################################################

# CwH.py
