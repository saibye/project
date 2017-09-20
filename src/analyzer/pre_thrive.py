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

g_detail_fetched = 150
g_detail_used    = 100


def pre_thrive_analyzer(_stock_id, _a_date, _b_date, _c_date, _d_date, _e_date, _my_df, _used_len, _db):
    global g_detail_fetched 

    lowest   = 0
    mailed = 0
    content1 = "duck\n"
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
            rt_E2= (h_E / last_close_price - 1) * 100.00
            vr_E= vr
            zt_E= zt
            log_info("Data: %s-E: %s, high:%.2f, vol:%.2f, %d", _stock_id, pub_date, h_E, v_E, i_E)



        idx  = idx + 1
    # for

    if got_B and got_C and got_D and got_E:
        log_info("bingo: %s", _stock_id)

        log_info("data: %s: B点涨幅:  %.2f", _stock_id, rt_B)
        log_info("data: %s: B点柱体:  %.2f", _stock_id, zt_B)

        log_info("data: %s: C点涨幅:  %.2f", _stock_id, rt_C)
        log_info("data: %s: C点柱体:  %.2f", _stock_id, zt_C)

        log_info("data: %s: D点涨幅:  %.2f", _stock_id, rt_D)
        log_info("data: %s: D点柱体:  %.2f", _stock_id, zt_D)

        # BC幅度
        rate_BC = (h_C / l_B - 1) * 100.00
        log_info("data: %s: 三线跌幅: -%.2f%%",   _stock_id, rate_BC)

        # CD长度
        len_CD  = i_D - i_C
        log_info("data: %s: 高点CD距离: %d", _stock_id, len_CD)

        # DB幅度
        rate_DB = (h_D / l_B - 1) * 100.00
        log_info("data: %s: 高点跌幅: -%.2f%%",   _stock_id, rate_DB)

        # DE长度
        # DE幅度
        len_DE  = i_E - i_D
        rate_DE = (h_D / l_E - 1) * 100.00
        step_DE = rate_DE / len_DE
        log_info("data: %s: 升幅DE距离: %d",   _stock_id, len_DE)
        log_info("data: %s: 升幅DE幅度: %.2f%%", _stock_id, rate_DE)
        log_info("data: %s: 升幅DE步长: %.2f", _stock_id, step_DE)

        # 升降对比
        log_info("data: %s: 参考DB幅度: %.2f%%，对比%.2f", _stock_id, rate_DB, rate_DE/rate_DB)

        # D点rpv
        D1 = 8
        D_rpv_rt = pre_thrive_rpv(_my_df, _used_len, _d_date, D1, _db)
        log_info("data: %s: D点之前[%d]RPV比率: %.2f", _stock_id, D1, D_rpv_rt)

        # D点往前最低！
        D2 = 0
        D3 = 5
        min_low, low_close, low_date, low_idx, low_vol, low_rate = pre_thrive_preceding_low(_my_df, _used_len, _d_date, D2, D3, _db)
        rate_DX = (h_D / min_low - 1) * 100.00
        log_info("data: %s: D点之前[%02d]最低: %s: low: %.2f, rate: %.2f%%", _stock_id, D3, low_date, min_low, rate_DX)

        D2 = 0
        D3 = 10
        min_low, low_close, low_date, low_idx, low_vol, low_rate = pre_thrive_preceding_low(_my_df, _used_len, _d_date, D2, D3, _db)
        rate_DX = (h_D / min_low - 1) * 100.00
        log_info("data: %s: D点之前[%02d]最低: %s: low: %.2f, rate: %.2f%%", _stock_id, D3, low_date, min_low, rate_DX)

    else:
        log_info("error: not got all point")

    if to_mail:
        subject = "pre_thrive: %s -- %s" % (_stock_id, _e_date)
        log_info(subject)
        log_info("mail:\n%s", content1)
        mailed = 1
    else:
        log_info("--: %s, %s", _stock_id, _a_date)

    return 0

def pre_thrive_work_one_day_stock(_stock_id, _a_date, _b_date, _c_date, _d_date, _e_date, _db):

    global g_detail_fetched 
    global g_detail_used

    log_debug("=====[%s, %s]=====", _stock_id, _a_date)

    # 获取明细数据
    # 之前n1单位的交易数据
    n1 = g_detail_fetched
    detail_df = get_pre_thrive_detail(_stock_id, _a_date, n1, _db);
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

    """
    # 格式化数据
    rv = pre_thrive_format_ref(_stock_id, detail_df)
    if rv < 0:
        log_error("error: pre_thrive_format_ref: %s", _stock_id)
        return -1
    """

    used_len = g_detail_used
    my_df = detail_df.head(used_len)

    rv = pre_thrive_analyzer(_stock_id, _a_date, _b_date, _c_date, _d_date, _e_date, my_df, used_len, _db)
    if rv == 0:
        log_info("nice1: %s", _stock_id)
        return 0
    log_debug("-------------------------------------------------")

    log_debug("-------------------------------------------------")

    return 1



#
# X点往前n1单位起始，n2单位内的最低low价
#
def pre_thrive_preceding_low(_detail_df, _used_len, _date, _n1, _n2, _db):
    idx = 0
    days = 0
    low_date = ""
    to_start = False
    to_count = False
    min_low = 1000.0
    low_close = 0.0

    for row_index, row in _detail_df.iterrows():
        TECH_IDX = idx

        pub_date         = row['pub_date']
        close_price      = row['close_price']
        high_price       = row['high_price']
        low_price        = row['low_price']

        last_close_price = row['last']
        open_price       = row['open_price']
        vol              = row['total']


        # log_debug("pub_date: [%s]", pub_date)

        if to_start:
            days = days + 1
            if days >= _n1:
                # log_debug("to count: %s", pub_date)
                to_start = False
                to_count = True
                days = 0

        if to_count:
            days = days + 1
            if days > _n2:
                # log_debug("reach n2: %d", days)
                break
            else:
                # log_debug("[%d, %s]", days, pub_date)
                if low_price < min_low:
                    min_low = low_price
                    low_close= close_price
                    low_date = pub_date
                    low_idx  = idx
                    low_vol  = vol
                    # log_debug("low:[%s.2f, %s]", min_low, low_date)
                    low_rate = (close_price - last_close_price) / last_close_price * 100

        if str(_date) == str(pub_date):
            to_start = True

        idx  = idx + 1

    return min_low, low_close, low_date, low_idx, low_vol, low_rate

# X点往前
# RPV
# avg(+rate*vol)  / avg(-rate*vol)
def pre_thrive_rpv(_detail_df, _used_len, _till, _n, _db):
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


def pre_thrive_dynamic_calc_tech(_df):

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


def pre_thrive_format_ref(_stock_id, _detail_df):

    # _detail MUST be sorted
    rv = ref_init4(_detail_df)
    if rv < 0:
        log_error("error: ref_init4")
        return -1

    _detail_df.sort_index(ascending=False, inplace=True)
    pre_thrive_dynamic_calc_tech(_detail_df)
    _detail_df.sort_index(ascending=True,  inplace=True)

    ref_set_tech5()


    return 0



def get_pre_thrive_detail(_stock_id, _pub_date, _n, _db):
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


def get_pre_thrive_stock_list(_till, _db):
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


    # 中孚信息 +++
    stock_id  = "300659"
    A_date = "2017-08-31"
    B_date = "2017-08-30"
    C_date = "2017-08-28"
    D_date = "2017-08-25"
    E_date = "2017-08-21"
    pre_thrive_work_one_day_stock(stock_id, A_date, B_date, C_date, D_date, E_date, db)

    # 韩建河山
    stock_id  = "603616"
    A_date = "2017-04-25"
    B_date = "2017-04-24"
    C_date = "2017-04-20"
    D_date = "2017-04-18"
    E_date = "2017-04-06"
    pre_thrive_work_one_day_stock(stock_id, A_date, B_date, C_date, D_date, E_date, db)

    # 万科A
    stock_id  = "000002"
    A_date = "2016-08-12"
    B_date = "2016-08-11"
    C_date = "2016-08-09"
    D_date = "2016-08-08"
    E_date = "2016-08-01"
    pre_thrive_work_one_day_stock(stock_id, A_date, B_date, C_date, D_date, E_date, db)

    # 泸天化
    stock_id  = "000912"
    A_date = "2016-09-26"
    B_date = "2016-09-23"
    C_date = "2016-09-21"
    D_date = "2016-09-20"
    E_date = "2016-09-12"
    pre_thrive_work_one_day_stock(stock_id, A_date, B_date, C_date, D_date, E_date, db)


    # 西部建设
    stock_id  = "002302"
    A_date = "2017-01-17"
    B_date = "2017-01-16"
    C_date = "2017-01-12"
    D_date = "2017-01-12"
    E_date = "2017-01-04"
    pre_thrive_work_one_day_stock(stock_id, A_date, B_date, C_date, D_date, E_date, db)


    # 东方铁塔
    stock_id  = "002545"
    A_date = "2017-08-07"
    B_date = "2017-08-04"
    C_date = "2017-08-02"
    D_date = "2017-08-01"
    E_date = "2017-07-27"
    pre_thrive_work_one_day_stock(stock_id, A_date, B_date, C_date, D_date, E_date, db)


    # 青山纸业
    stock_id  = "600103"
    A_date = "2017-07-12"
    B_date = "2017-07-11"
    C_date = "2017-07-07"
    D_date = "2017-07-06"
    E_date = "2017-06-30"
    pre_thrive_work_one_day_stock(stock_id, A_date, B_date, C_date, D_date, E_date, db)

    # 达安股份 case3
    stock_id  = "300635"
    A_date = "2017-09-07"
    B_date = "2017-09-06"
    C_date = "2017-09-01"
    D_date = "2017-08-31"
    E_date = "2017-08-24"
    pre_thrive_work_one_day_stock(stock_id, A_date, B_date, C_date, D_date, E_date, db)

    # 达安股份 case3
    stock_id  = "300635"
    A_date = "2017-09-07"
    B_date = "2017-09-06"
    C_date = "2017-09-01"
    D_date = "2017-08-31"
    E_date = "2017-08-24"
    pre_thrive_work_one_day_stock(stock_id, A_date, B_date, C_date, D_date, E_date, db)


    # 2017-9-16
    # 科大国创
    stock_id  = "300520"
    A_date = "2017-09-12"
    B_date = "2017-09-11"
    C_date = "2017-09-07"
    D_date = "2017-09-06"
    E_date = "2017-08-30"
    pre_thrive_work_one_day_stock(stock_id, A_date, B_date, C_date, D_date, E_date, db)

    # 多氟多
    stock_id  = "002407"
    A_date = "2017-09-11"
    B_date = "2017-09-08"
    C_date = "2017-09-06"
    D_date = "2017-09-05"
    E_date = "2017-08-30"
    pre_thrive_work_one_day_stock(stock_id, A_date, B_date, C_date, D_date, E_date, db)

    # 先导智能
    stock_id  = "300450"
    A_date = "2017-09-11"
    B_date = "2017-09-08"
    C_date = "2017-09-06"
    D_date = "2017-09-05"
    E_date = "2017-08-30"
    pre_thrive_work_one_day_stock(stock_id, A_date, B_date, C_date, D_date, E_date, db)

    # 溢多利
    stock_id  = "300381"
    A_date = "2017-09-14"
    B_date = "2017-09-13"
    C_date = "2017-09-11"
    D_date = "2017-09-08"
    E_date = "2017-09-06"
    pre_thrive_work_one_day_stock(stock_id, A_date, B_date, C_date, D_date, E_date, db)

    # 盈方微
    stock_id  = "000670"
    A_date = "2017-09-12"
    B_date = "2017-09-11"
    C_date = "2017-09-07"
    D_date = "2017-09-06"
    E_date = "2017-08-30"
    pre_thrive_work_one_day_stock(stock_id, A_date, B_date, C_date, D_date, E_date, db)

    # 晨鸣纸业
    stock_id  = "000488"
    A_date = "2017-09-08"
    B_date = "2017-09-07"
    C_date = "2017-09-05"
    D_date = "2017-09-04"
    E_date = "2017-08-29"
    pre_thrive_work_one_day_stock(stock_id, A_date, B_date, C_date, D_date, E_date, db)


    db_end(db)


#######################################################################

def main():
    sailog_set("A_pre_thrive.log")

    log_info("let's begin here!")

    work()

    log_info("main ends, bye!")

    return

#######################################################################

main()

#######################################################################

# pre_thrive.py
