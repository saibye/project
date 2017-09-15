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

g_detail_fetched = 400
g_detail_used    = 350


def malaw_analyzer(_stock_id, _a_date, _b_date, _c_date, _d_date, _my_df, _used_len, _db):
    global g_detail_fetched 

    lowest   = 0
    mailed = 0
    content1 = "malaw\n"
    to_mail = False

    idx    = 0
    TECH_IDX = 0

    v_max = 0
    c_max = 0
    c_min = 1000

    got_A = False
    got_B = False
    got_C = False
    got_D = False
    got_E = False

    AB = 0 # A到B天数
    BC = 0 # B到C天数
    CD = 0 # C到D天数

    for row_index, row in _my_df.iterrows():
        TECH_IDX = idx

        close_price      = row['close_price']
        high_price       = row['high_price']
        low_price        = row['low_price']
        last_close_price = row['last']
        open_price       = row['open_price']
        vol              = row['total']
        pub_date         = row['pub_date']
        rate = (close_price - last_close_price) / last_close_price * 100
        zt   = (close_price - open_price) / last_close_price * 100
        vr   = 0

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
            zt_A= zt
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
            zt_B= zt
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
            zt_C= zt
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
            zt_D= zt
            log_info("Data: %s-D: %s, low:%.2f, vol:%.2f, %d", _stock_id, pub_date, l_D, v_D, i_D)

        idx  = idx + 1
    # for


    if got_A and got_B and got_C and got_D:
        log_info("bingo: %s", _stock_id)

        log_info("data: %s: A点涨幅:  %.2f", _stock_id, rt_A)
        log_info("data: %s: A点柱体:  %.2f", _stock_id, zt_A)

        log_info("data: %s: B点涨幅:  %.2f", _stock_id, rt_B)
        log_info("data: %s: B点柱体:  %.2f", _stock_id, zt_B)

        # A点量比

        # BC幅度
        len_BC = i_C - i_B
        log_info("data: %s: BC长度: %d",   _stock_id, len_BC)
        region_days, upper_days, cross_days, std1, std2 = malaw_region(_my_df, _used_len, _b_date, _c_date, _db)

        B_rpv_rt = malaw_rpv(_my_df, _used_len, _b_date, len_BC, _db)
        log_info("data: %s: B点之前[%d]RPV比率: %.2f", _stock_id, len_BC, B_rpv_rt)

        # CD长度
        len_CD  = i_D - i_C
        log_info("data: %s: CD距离: %d", _stock_id, len_CD)

        # D点rpv
        D1 = 8
        D_rpv_rt = malaw_rpv(_my_df, _used_len, _d_date, D1, _db)
        log_info("data: %s: D点之前[%d]RPV比率: %.2f", _stock_id, D1, D_rpv_rt)


    else:
        log_info("error: not got all point")

    if to_mail:
        subject = "malaw: %s -- %s" % (_stock_id, _a_date)
        log_info(subject)
        log_info("mail:\n%s", content1)
        mailed = 1
    else:
        log_info("--: %s, %s", _stock_id, _a_date)

    return 0

def malaw_work_one_day_stock(_stock_id, _a_date, _b_date, _c_date, _d_date, _db):

    global g_detail_fetched 
    global g_detail_used

    log_debug("=====[%s, %s]=====", _stock_id, _a_date)

    # 获取明细数据
    # 之前n1单位的交易数据
    n1 = g_detail_fetched
    detail_df = get_malaw_detail(_stock_id, _a_date, n1, _db);
    if detail_df is None:
        log_info("[%s, %s] detail is none", _stock_id, _a_date)
        return -1
    elif detail_df.empty:
        log_debug("detail_df is empty: [%d]", len(detail_df))
        return 1
    else:
        # log_debug("n1: len[%d]", len(detail_df))
        pass

    length = len(detail_df)
    # if length < g_detail_used:
    if length < 8:
        log_info("data-not-enough: %s: %d", _stock_id, length)
        return 1

    # 格式化数据
    rv = malaw_format_ref(_stock_id, detail_df)
    if rv < 0:
        log_error("error: malaw_format_ref: %s", _stock_id)
        return -1

    used_len = g_detail_used
    my_df = detail_df.head(used_len)

    rv = malaw_analyzer(_stock_id, _a_date, _b_date, _c_date, _d_date, my_df, used_len, _db)
    if rv == 0:
        log_info("nice1: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    log_debug("-------------------------------------------------")

    return 1




# X点往前
# RPV
# avg(+rate*vol)  / avg(-rate*vol)
def malaw_rpv(_detail_df, _used_len, _till, _n, _db):
    U_sum = 0.0 # up
    U_days = 0
    D_sum = 0.0 # down
    D_days = 0

    U_rpv = 1.0
    D_rpv = 1.0

    TECH_IDX = 0
    to_start = False

    idx = 0
    max_vol = 0.0
    rel_vr  = 0.0
    rel_rt  = 0.0
    days    = 0
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx
        close_price      = row['close_price']
        vol              = row['total']
        pub_date         = row['pub_date']
        last_close_price = row['last']
        rate = (close_price - last_close_price) / last_close_price * 100

        if not to_start and str(_till) == str(pub_date):
            to_start = True

        if to_start:
            days = days + 1
            if days > _n:
                # log_debug("finished: %d > %d", days, _n)
                break
            else:
                if rate > 0.0:
                    U_sum  += rate * vol
                    U_days += 1
                    # log_debug("U: %s: %.2f * %.2f += %.2f, U(%d)", pub_date, rate, vol, U_sum, U_days)
                else:
                    D_sum += rate * vol
                    D_days+= 1
                    # log_debug("D: %s: %.2f * %.2f += %.2f, D(%d)", pub_date, rate, vol, D_sum, D_days)
        else:
            # log_debug("%s not ready", pub_date)
            pass

        idx  = idx + 1

    if U_days <= 0:
        rpv_rt = -11.11
    elif D_days <= 0:
        rpv_rt = 9.99
        # log_debug("D_days: %d", D_days)
    elif abs(D_sum) <= 1:
        rpv_rt = 9.99
        # log_debug("D_sum: %d",  D_sum)
    else:
        # log_info("[%.2f, %d], [%.2f, %d]", U_sum, U_days, D_sum, D_days)
        U_rpv = U_sum / U_days
        D_rpv = D_sum / D_days
        rpv_rt = U_rpv / D_rpv
    # log_info("URPV[%.2f], DRPV[%.2f], RT[%.2f]", U_rpv, D_rpv, rpv_rt)

    return abs(rpv_rt)


# BC区间
# 
# 
def malaw_region(_detail_df, _used_len, _from, _till, _db):
    TECH_IDX = 0
    to_start = False

    sum1 = 0.0
    sum2 = 0.0

    idx = 0
    region_days= 0
    cross_days = 0
    upper_days = 0
    devia_days  = 0
    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx
        close_price      = row['close_price']
        open_price       = row['open_price']
        low_price        = row['low_price']
        high_price       = row['high_price']
        vol              = row['total']
        pub_date         = row['pub_date']
        last_close_price = row['last']
        rate = (close_price - last_close_price) / last_close_price * 100

        ma200 = ref_ma200(TECH_IDX)

        if not to_start and str(_from) == str(pub_date):
            to_start = True

        if to_start:
            region_days = region_days + 1
            sum1 += (close_price - ma200) * (close_price - ma200)

            # log_debug("IN-region: %s -- ma:%.2f, sum: %.2f", pub_date, ma200, sum1)

            if close_price >= ma200:
                upper_days += 1
                # log_debug("%s -- cross", pub_date)

            if high_price >= ma200 and low_price <= ma200:
                cross_days += 1
                # log_debug("%s -- cross", pub_date)
            else:
                devia_days += 1
                if low_price > ma200:
                    sum2 += (low_price-ma200) * (low_price-ma200)
                elif high_price < ma200:
                    sum2 += (high_price-ma200) * (high_price-ma200)

            
        else:
            # log_debug("%s not ready", pub_date)
            pass

        if str(_till) == str(pub_date):
            log_debug("to-end: %s", _till)
            break

        idx  = idx + 1

    log_debug("region-days:%d", region_days)
    log_debug("upper-days: %d", upper_days)
    log_debug("cross-days: %d", cross_days)
    log_debug("devia-days: %d", devia_days)

    if region_days > 0:
        std1 = sum1 / region_days
        log_debug("malaw-std: %.3f, sum: %.3f", std1, sum1)

    if devia_days > 0:
        std2 = sum2 / devia_days
        log_debug("malaw-dva: %.3f, sum: %.3f", std2, sum2)

    return  region_days, upper_days, cross_days, std1, std2


def malaw_dynamic_calc_tech(_df):

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


def malaw_format_ref(_stock_id, _detail_df):

    # _detail MUST be sorted
    rv = ref_init4(_detail_df)
    if rv < 0:
        log_error("error: ref_init4")
        return -1

    _detail_df.sort_index(ascending=False, inplace=True)
    malaw_dynamic_calc_tech(_detail_df)
    _detail_df.sort_index(ascending=True,  inplace=True)

    ref_set_tech5()


    return 0



def get_malaw_detail(_stock_id, _pub_date, _n, _db):
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


def get_malaw_stock_list(_till, _db):
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


def regression(_db):

    return 0


def work():
    db = db_init()


    # case1
    # 洛阳钼业
    stock_id  = "603993"
    A_date = "2017-06-13"
    B_date = "2017-06-12"
    C_date = "2017-04-24"
    D_date = "2017-01-23"
    malaw_work_one_day_stock(stock_id, A_date, B_date, C_date, D_date, db)

    db_end(db)


#######################################################################

def main():
    sailog_set("A_malaw.log")

    log_info("let's begin here!")

    work()

    log_info("main ends, bye!")

    return

#######################################################################

main()

#######################################################################

# malaw.py
