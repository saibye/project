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


def cwha_analyzer(_stock_id, _k_date, _a_date, _b_date, _c_date, _d_date, _e_date, _my_df, _used_len, _db):
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
        low_price        = row['low_price']
        last_close_price = row['last']
        open_price       = row['open_price']
        vol              = row['total']
        pub_date         = row['pub_date']
        rate = (close_price - last_close_price) / last_close_price * 100
        zt   = (close_price - open_price) / last_close_price * 100

        if ref_vma50(TECH_IDX) > 0:
            vr = (vol / ref_vma50(TECH_IDX) - 1) * 100
        else:
            vr = 0
        log_debug("--------------------%s-------------------", pub_date)


        if vol > v_max:
            v_max  = vol
            c_vmax = close_price

        if close_price > c_max:
            c_max = close_price
            i_max = idx

        if close_price < c_min:
            c_min = close_price
            i_min = idx

        # K点
        if str(_k_date) == str(pub_date):
            log_debug("nice: K-point: %s", pub_date)
            got_K = True
            v_K = vol
            p_K = close_price
            h_K = high_price
            l_K = low_price
            i_K = idx
            d_K = pub_date
            rt_K= rate
            vr_K= vr
            log_info("Data: %s-K: %s, low:%.2f, vol:%.2f, %d", _stock_id, pub_date, l_K, v_K, i_K)

        # A点
        if str(_a_date) == str(pub_date):
            log_debug("nice: A-point: %s", pub_date)
            got_A = True
            v_A = vol
            p_A = close_price
            h_A = high_price
            l_A = low_price
            i_A = idx
            d_A = pub_date
            rt_A= rate
            vr_A= vr
            log_info("Data: %s-A: %s, high:%.2f, vol:%.2f, %d", _stock_id, pub_date, h_A, v_A, i_A)

        # B点
        if str(_b_date) == str(pub_date):
            log_debug("nice: B-point: %s", pub_date)
            got_B = True
            v_B = vol
            p_B = close_price
            h_B = high_price
            l_B = low_price
            i_B = idx
            d_B = pub_date
            rt_B= rate
            vr_B= vr
            log_info("Data: %s-B: %s, low:%.2f, vol:%.2f, %d", _stock_id, pub_date, l_B, v_B, i_B)

        # C点
        if str(_c_date) == str(pub_date):
            log_debug("nice: C-point: %s", pub_date)
            got_C = True
            v_C = vol
            p_C = close_price
            h_C = high_price
            l_C = low_price
            i_C = idx
            d_C = pub_date
            rt_C= rate
            vr_C= vr
            log_info("Data: %s-C: %s, high:%.2f, vol:%.2f, %d", _stock_id, pub_date, h_C, v_C, i_C)

        # D点
        if str(_d_date) == str(pub_date):
            log_debug("nice: D-point: %s", pub_date)
            got_D = True
            v_D = vol
            p_D = close_price
            h_D = high_price
            l_D = low_price
            i_D = idx
            d_D = pub_date
            rt_D= rate
            vr_D= vr
            log_info("Data: %s-D: %s, low:%.2f, vol:%.2f, %d", _stock_id, pub_date, l_D, v_D, i_D)

        # E点
        if str(_e_date) == str(pub_date):
            log_debug("nice: E-point: %s", pub_date)
            got_E = True
            v_E = vol
            p_E = close_price
            h_E = high_price
            l_E = low_price
            i_E = idx
            d_E = pub_date
            rt_E= rate
            vr_E= vr
            log_info("Data: %s-E: %s, high:%.2f, vol:%.2f, %d", _stock_id, pub_date, h_E, v_E, i_E)



        idx  = idx + 1
    # for

    if got_A and got_B and got_C and got_D and got_E and got_K:
        log_info("bingo: %s", _stock_id)
        rate_DE = h_E / l_D * 100.00
        len_DE  = i_E - i_D
        rate_CE = h_E / h_E * 100.00
        len_CD  = i_D - i_C
        rate_AE = h_E / h_A * 100.00
        len_AB  = i_B - i_A
        len_BC  = i_C - i_B
        len_AC  = i_C - i_A
        rate_AB = h_A / l_B * 100.00
        rate_BC = h_C / l_B * 100.00
        len_KA  = i_A - i_K
        rate_KA = h_A / l_K * 100.00

        log_info("data: %s: KA长度: %d", _stock_id, len_KA)
        log_info("data: %s: AB长度: %d", _stock_id, len_AB)
        log_info("data: %s: BC长度: %d", _stock_id, len_BC)
        log_info("data: %s: AC长度: %d", _stock_id, len_AC)
        log_info("data: %s: CD长度: %d", _stock_id, len_CD)
        log_info("data: %s: DE长度: %d", _stock_id, len_DE)
        log_info("data: %s: AK比率: %.2f",   _stock_id, rate_KA)
        log_info("data: %s: AB比率: %.2f",   _stock_id, rate_AB)
        log_info("data: %s: CB比率: %.2f",   _stock_id, rate_BC)
        log_info("data: %s: AE比率: %.2f",   _stock_id, rate_AE)
        log_info("data: %s: DE比率: %.2f",   _stock_id, rate_DE)
        log_info("data: %s: CE比率: %.2f",   _stock_id, rate_CE)
        log_info("data: %s: A点量比: +%.2f", _stock_id, vr_A) # TODO
        log_info("data: %s: C点量比: +%.2f", _stock_id, vr_C) # TODO
        log_info("data: %s: E点量比: +%.2f", _stock_id, vr_E) # TODO

        # A点附近最大成交量
        A1 = 4
        A_vol_max, A_rel_vr, A_rel_rt = cwha_max_vol(_my_df, _used_len, _a_date, A1, _db)
        log_info("data: %s: A点附近[%d]最大成交量: %.2f, +%.2f%%, %.2f%%",
                _stock_id, A1, A_vol_max, A_rel_vr, A_rel_rt)

        # D点之前rpv
        D2 = 4
        D2 = 20
        D_rpv_rt = cwha_rpv(_my_df, _used_len, _d_date, D2, _db)
        log_info("data: %s: D点之前[%d]RPV比率: %.2f",
                _stock_id, D2, D_rpv_rt)

        # D点之前rpv
        B3 = 12
        B4 = 10
        B_mean, B_std, B_rel_date, B_rel_idx = cwha_devia(_my_df, _used_len, _b_date, B3, B4, _db)
        log_info("data: %s: B点附近[%d]长度[%d]平均值: %.2f, 标准差: %.2f [%s]",
                _stock_id, B3, B4, B_mean, B_std, B_rel_date)

        rate_BS = B_mean / l_B * 100.00
        log_info("data: %s: BS比率: %.2f",   _stock_id, rate_BS)

    else:
        log_info("error: not got all point")

    if to_mail:
        subject = "cwha: %s -- %s" % (_stock_id, _e_date)
        log_info(subject)
        log_info("mail:\n%s", content1)
        mailed = 1
        saimail_dev(subject, content1)
    else:
        log_info("--: %s, %s", _stock_id, _e_date)

    return 0



# A点附近的最大成交量
#
def cwha_max_vol(_detail_df, _used_len, _date, _n, _db):

    idx = 0
    TECH_IDX = 0
    for row_index, row in _detail_df.iterrows():
        pub_date         = row['pub_date']

        if str(_date) == str(pub_date):
            break

        idx  = idx + 1

    # log_info("date[%s] => idx[%d]", _date, idx)
    start_idx = idx - _n
    end_idx   = idx + _n
    # log_info("start:[%d] => end[%d]", start_idx, end_idx)

    if start_idx < 0 or end_idx > len(_detail_df):
        log_error("error: exceeds: %d, %d", start_idx, end_idx)
        return -1, -1, -1

    idx = 0
    max_vol = 0.0
    rel_vr  = 0.0
    rel_rt  = 0.0
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = _used_len - idx - 1
        close_price      = row['close_price']
        vol              = row['total']
        pub_date         = row['pub_date']
        last_close_price = row['last']
        rate = (close_price - last_close_price) / last_close_price * 100

        if idx >= start_idx and idx < end_idx:
            # log_debug("[%s]: [%d, %d]: [%.2f, %.2f]", pub_date, idx, TECH_IDX, vol, ref_vma50(TECH_IDX))
            if ref_vma50(TECH_IDX) > 0:
                vr = (vol / ref_vma50(TECH_IDX) - 1) * 100
            else:
                vr = 0.0

            if vol > max_vol:
                max_vol = vol
                rel_vr  = vr
                rel_rt  = rate
        else:
            pass

        idx  = idx + 1

    # log_info("max vol: %.2f, v-rate: +%.2f%%, p-rate: %.2f%%", max_vol, rel_vr, rel_rt)

    return max_vol, rel_vr, rel_rt

# RPV
# avg(+rate*vol)  / avg(-rate*vol)
def cwha_rpv(_detail_df, _used_len, _till, _n, _db):
    U_sum = 0.0 # up
    U_days = 0
    D_sum = 0.0 # down
    D_days = 0

    U_rpv = 1.0
    D_rpv = 1.0

    idx = 0
    TECH_IDX = 0
    for row_index, row in _detail_df.iterrows():
        pub_date         = row['pub_date']

        if str(_till) == str(pub_date):
            break

        idx  = idx + 1

    # log_info("date[%s] => idx[%d]", _till, idx)
    start_idx = idx - _n
    end_idx   = idx
    # log_info("start:[%d] => end[%d]", start_idx, end_idx)

    if start_idx < 0:
        log_error("error: exceeds: %d, %d", start_idx, end_idx)
        return -19.99

    idx = 0
    max_vol = 0.0
    rel_vr  = 0.0
    rel_rt  = 0.0
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = _used_len - idx - 1
        close_price      = row['close_price']
        vol              = row['total']
        pub_date         = row['pub_date']
        last_close_price = row['last']
        rate = (close_price - last_close_price) / last_close_price * 100

        if idx >= start_idx and idx <= end_idx:
            if rate > 0.0:
                U_sum  += rate * vol
                U_days += 1
                # log_debug("U: %s: %.2f * %.2f += %.2f, U(%d)", pub_date, rate, vol, U_sum, U_days)
            else:
                D_sum += rate * vol
                D_days+= 1
                # log_debug("D: %s: %.2f * %.2f += %.2f, D(%d)", pub_date, rate, vol, D_sum, D_days)
        else:
            pass

        idx  = idx + 1

    if U_days <= 0:
        rpv_rt = -11.11
    elif D_days <= 0:
        rpv_rt = 9.99
    else:
        # log_info("[%.2f, %d], [%.2f, %d]", U_sum, U_days, D_sum, D_days)
        U_rpv = U_sum / U_days
        D_rpv = D_sum / D_days
        rpv_rt = U_rpv / D_rpv
    # log_info("URPV[%.2f], DRPV[%.2f], RT[%.2f]", U_rpv, D_rpv, rpv_rt)

    return abs(rpv_rt)


# 方差最小时的平均值
# B-frame
def cwha_devia(_detail_df, _used_len, _date, _n1, _n2, _db):

    idx = 0
    TECH_IDX = 0
    min_std  = 1000.0
    min_mean = 0.0
    min_date = ""
    min_idx  = -1

    for row_index, row in _detail_df.iterrows():
        pub_date         = row['pub_date']

        if str(_date) == str(pub_date):
            break

        idx  = idx + 1

    # log_info("date[%s] => idx[%d]", _date, idx)
    start_idx = idx - _n1
    end_idx   = idx + _n1
    # log_info("start:[%d] => end[%d]", start_idx, end_idx)

    if start_idx < 0 or end_idx > len(_detail_df):
        log_error("error: exceeds: %d, %d", start_idx, end_idx)
        return -1, -1, -1, -1

    s1 = _detail_df['low_price']
    # log_debug("series: %s", s1)

    idx = 0
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = _used_len - idx - 1
        close_price      = row['close_price']
        vol              = row['total']
        pub_date         = row['pub_date']
        last_close_price = row['last']
        rate = (close_price - last_close_price) / last_close_price * 100

        if idx >= start_idx and idx < end_idx:
            s2 = s1[idx: idx+_n2]
            # log_debug("[%s]:\n%s", pub_date, s2)
            std = s2.std()
            # log_debug("[%s]: std: %.2f, mean: %.2f", pub_date, std, s2.mean())
            if std < min_std:
                min_std  = std
                min_mean = s2.mean()
                min_date = pub_date
                min_idx  = idx
        else:
            pass

        idx  = idx + 1
    # for

    # log_debug("[%s]: %.2f, %.2f, %d", min_date, min_std, min_mean, min_idx)

    return min_mean, min_std, min_date, min_idx


def cwha_exec_algo(_max_date, _detail_df, _db):

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
    days1 = get_cwha_max_price_days(_detail_df,  this_close)
    # log_debug("价格突破天数days1: %d", days1)

    # 收盘价突破 -- 容错
    days2 = get_cwha_almost_max_price_days(_detail_df,  this_close)
    # log_debug("价格突破天数days2: %d", days2)

    # 成交量突破
    # log_debug("volume: [%.2f]", this_vol)
    days3 = get_cwha_max_volume_days(_detail_df, this_vol)
    # log_debug("成交量突破天数days3: %d", days3)

    # 阳柱成交量大 sum(red) / sum(green) > 2.5
    n = 30
    sum1, sum2 = sum_cwha_detail(_detail_df, n, _db)
    # log_debug("red-sum: %.3f", sum1)
    # log_debug("gre-sum: %.3f", sum2)
    vol_rate3 = -1
    if sum1 > 0 and sum2 > 0:
        vol_rate3 = sum1 / sum2
        # log_debug("合计量比vol_rate3: %.3f", vol_rate3)

    return rate, zt, days1, days2, days3, vol_rate1, vol_rate2, vol_rate3, ma60_bigger, ma10_divia


def sum_cwha_detail(_detail_df, _days, _db):

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
def get_cwha_max_price_days(_detail_df, _max_price):
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
def get_cwha_almost_max_price_days(_detail_df, _max_price):
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
def get_cwha_max_volume_days(_detail_df, _max_volume):
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



def cwha_dynamic_calc_tech(_df):

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


def cwha_format_ref(_stock_id, _detail_df):

    # _detail MUST be sorted
    rv = ref_init4(_detail_df)
    if rv < 0:
        log_error("error: ref_init4")
        return -1

    _detail_df.sort_index(ascending=False, inplace=True)
    cwha_dynamic_calc_tech(_detail_df)
    _detail_df.sort_index(ascending=True,  inplace=True)

    ref_set_tech5()

    log_debug("ref0:  [%.3f, %.3f] -- vol:[%.3f]", ref_open(0), ref_close(0), ref_vol(0))
    log_debug("ref1:  [%.3f, %.3f] -- vol:[%.3f]", ref_open(1), ref_close(1), ref_vol(1))
    log_debug("ref2:  [%.3f, %.3f] -- vol:[%.3f]", ref_open(2), ref_close(2), ref_vol(2))

    log_debug("ma5/10 [%.3f, %.3f] - vma[%.3f, %.3f]", ref_ma5(0), ref_ma10(0), ref_vma5(0), ref_vma10(0))
    log_debug("ma5/10 [%.3f, %.3f] - vma[%.3f, %.3f]", ref_ma5(1), ref_ma10(1), ref_vma5(1), ref_vma10(1))
    log_debug("ma5/10 [%.3f, %.3f] - vma[%.3f, %.3f]", ref_ma5(2), ref_ma10(2), ref_vma5(2), ref_vma10(2))

    log_debug("macd0: [%.3f] [%.3f], [%.3f]", ref_macd(0), ref_diff(0), ref_dea(0))
    log_debug("macd1: [%.3f] [%.3f], [%.3f]", ref_macd(1), ref_diff(1), ref_dea(1))
    log_debug("macd2: [%.3f] [%.3f], [%.3f]", ref_macd(2), ref_diff(2), ref_dea(2))

    return 0


def get_cwha_detail(_stock_id, _pub_date, _n, _db):
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


def get_cwha_stock_list(_till, _db):
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


def cwha_work_one_day_stock(_stock_id, _k_date, _a_date, _b_date, _c_date, _d_date, _e_date, _db):

    global g_detail_fetched 
    global g_detail_used

    log_debug("================================================")
    # 获取明细数据
    # 之前n1单位的交易数据
    n1 = g_detail_fetched
    detail_df = get_cwha_detail(_stock_id, _e_date, n1, _db);
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
        log_info("df-not-enough: %s: %d", _stock_id, length)
        return 1

    # 格式化数据
    rv = cwha_format_ref(_stock_id, detail_df)
    if rv < 0:
        log_error("error: cwha_format_ref: %s", _stock_id)
        return -1

    used_len = g_detail_used
    my_df = detail_df.sort_index(ascending=False).tail(used_len)
    rv = cwha_analyzer(_stock_id, _k_date, _a_date, _b_date, _c_date, _d_date, _e_date, my_df, used_len, _db)
    if rv < 0:
        log_error("error: cwha_analyzer: %s", _stock_id)
        return -1

    return 0




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

    """
    # 柳钢股份 case1 init
    till_date = "2016-11-18"
    stock_id  = "601003"
    cwha_work_one_day_stock(stock_id, till_date, db)


    # 海康威视 3
    till_date = "2017-01-18"
    stock_id  = "002415"
    cwha_work_one_day_stock(stock_id, till_date, db)

    # 晨鸣纸业 4
    till_date = "2017-06-28"
    stock_id  = "000488"
    cwha_work_one_day_stock(stock_id, till_date, db)

    # 盐田港 5: FAIL
    till_date = "2017-04-06"
    stock_id  = "000088"
    cwha_work_one_day_stock(stock_id, till_date, db)

    # 华资实业 6 done
    till_date = "2017-07-06"
    stock_id  = "600191"
    cwha_work_one_day_stock(stock_id, till_date, db)

    # 天茂集团 7 done
    till_date = "2017-07-05"
    stock_id  = "000627"
    cwha_work_one_day_stock(stock_id, till_date, db)

    # 珠海港 2 TODO
    till_date = "2017-04-10"
    stock_id  = "000507"
    cwha_work_one_day_stock(stock_id, till_date, db)

    # 东湖高新 8 TODO: high = vol*close_price
    till_date = "2017-07-05"
    stock_id  = "600133"
    cwha_work_one_day_stock(stock_id, till_date, db)

    # 沧州大化 9  TODO: fail: dynamic search
    till_date = "2017-07-10"
    stock_id  = "600230"
    cwha_work_one_day_stock(stock_id, till_date, db)

    # 敦煌种业10  TODO
    till_date = "2017-07-18"
    stock_id  = "600354"
    cwha_work_one_day_stock(stock_id, till_date, db)
    """


    return 0


def work():
    db = db_init()

    if sai_is_product_mode():
        K_date = "2017-04-17"
        A_date = "2017-04-26"
        B_date = "2017-06-02"
        C_date = "2017-06-30"
        D_date = "2017-07-05"
        E_date = "2017-07-10"

        # 沧州大化
        stock_id  = "600230"
        cwha_work_one_day_stock(stock_id, K_date, A_date, B_date, C_date, D_date, E_date, db)

    else:
        regression(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("cwha3.log")

    log_info("let's begin here!")

    work()

    log_info("main ends, bye!")

    return

#######################################################################

main()

#######################################################################

# cwha.py
