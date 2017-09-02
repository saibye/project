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


def flag_analyzer(_stock_id, _trade_date, _detail_df, _db):

    mailed = 0
    content1 = ""

    length = len(_detail_df)
    if length <= 90:
        log_info("data-not-enough: %s", _stock_id)
        return 1

    rate, zt, days1, days2, days3, \
        vol_rate1, vol_rate2, vol_rate3, \
        ma60_bigger, ma10_divia =  \
        flag_exec_algo(_trade_date, _detail_df, _db)

    log_info("涨幅: %.2f%%, 柱体: %.2f%%", rate, zt)
    log_info("突破天数: %d, %d, 成交量突破: %d", days1, days2, days3)
    log_info("当前量比: %.2f, %.2f, 合计量比: %.2f", vol_rate1, vol_rate2, vol_rate3)
    log_info("ma60企稳: %s, ma10偏离: %.2f", ma60_bigger, ma10_divia)

    # 涨幅
    rate0 = (ref_close(0) - ref_close(1)) / ref_close(1) * 100
    rate1 = (ref_close(1) - ref_close(2)) / ref_close(2) * 100
    rate2 = (ref_close(2) - ref_close(3)) / ref_close(3) * 100
    rate3 = (ref_close(3) - ref_close(4)) / ref_close(4) * 100
    rate4 = (ref_close(4) - ref_close(5)) / ref_close(5) * 100

    # 柱体
    zt0 = (ref_close(0) - ref_open(0)) / ref_close(1) * 100
    zt1 = (ref_close(1) - ref_open(1)) / ref_close(2) * 100
    zt2 = (ref_close(2) - ref_open(2)) / ref_close(3) * 100
    zt3 = (ref_close(3) - ref_open(3)) / ref_close(4) * 100
    zt4 = (ref_close(4) - ref_open(4)) / ref_close(5) * 100

    # 中点
    md0 = (ref_close(0) + ref_open(0)) / 2.0
    md1 = (ref_close(1) + ref_open(1)) / 2.0
    md2 = (ref_close(2) + ref_open(2)) / 2.0
    md3 = (ref_close(3) + ref_open(3)) / 2.0
    md4 = (ref_close(4) + ref_open(4)) / 2.0

    MD0 = (ref_high(0) + ref_low(0)) / 2.0
    MD1 = (ref_high(1) + ref_low(1)) / 2.0
    MD2 = (ref_high(2) + ref_low(2)) / 2.0

    log_debug("rate0: %.2f%%, zt0: %.2f%%, md0: %.2f", rate0, zt0, md0)
    log_debug("rate1: %.2f%%, zt1: %.2f%%, md1: %.2f", rate1, zt1, md1)
    log_debug("rate2: %.2f%%, zt2: %.2f%%, md2: %.2f", rate2, zt2, md2)
    log_debug("rate3: %.2f%%, zt3: %.2f%%, md3: %.2f", rate3, zt3, md3)
    log_debug("rate4: %.2f%%, zt4: %.2f%%, md4: %.2f", rate4, zt4, md4)


    # MACD
    macd    = ref_macd(0) > 0 and ref_diff(0) > 0 and ref_dea(0) > 0
    log_debug("macd(%s): %.3f, diff: %.3f, dea: %.3f", macd, ref_macd(0), ref_diff(0), ref_dea(0))

    macd2   = ref_macd(0) > 0 and ref_diff(0) > 0 and ref_dea(0) > -0.1
    log_debug("macd2(%s): %.3f, diff: %.3f, dea: %.3f", macd, ref_macd(0), ref_diff(0), ref_dea(0))

    # FASAN
    fasan3  = ref_ma5(0) > ref_ma10(0) and ref_ma10(0) > ref_ma20(0)
    fasan4  = fasan3 and ref_ma20(0) > ref_ma30(0)
    fasan5  = fasan4 and ref_ma30(0) > ref_ma60(0)

    if fasan5:
        log_info("5线发散")
    elif fasan4:
        log_info("4线发散")
    elif fasan3:
        log_info("3线发散")

    if rate1 > 9.8:
        this_price = ref_close(1)

        # 柱体、涨幅、中线
        zt_rule = abs(zt0) < 2.0
        rt_rule = abs(rate0) < 2.1
        md_rule = md0 > this_price
        log_debug("REF(1): zt: %s, md: %s, rt:%s", zt_rule, md_rule, rt_rule)

        # 对比均线量比
        vol_rate = ref_vol(0) / ref_vma10(5)
        log_debug("vol-rate: %.3f", vol_rate)

        # 累计涨幅1
        acc_rate = (this_price / ref_open(3) - 1) * 100
        log_debug("acc_rate: %.3f", acc_rate)

        # 累计涨幅2
        ACC_rate = (this_price / ref_open(6) - 1) * 100
        log_debug("ACC rate: %.3f", ACC_rate)

        # 累计涨幅3
        ACC_rate2= (this_price / ref_open(4) - 1) * 100
        log_debug("ACC rate: %.3f", ACC_rate2)

        ACC_max  = max(acc_rate, ACC_rate, ACC_rate2)
        log_debug("ACC max: %.3f", ACC_max)

        # 002161
        rule3 = zt_rule and md_rule and rt_rule \
            and vol_rate > 15 and ACC_rate > 30 \
            and macd

        # 600740
        rule4 = zt_rule and md_rule and rt_rule \
            and vol_rate > 5 and ACC_max > 15 \
            and macd2

        if rule3:
            content1 = "rule3: %s - %s" % (_stock_id, _trade_date)
            log_info("nice: rule3: %s", _stock_id)
        elif rule4:
            content1 = "rule4(weak): %s - %s" % (_stock_id, _trade_date)
            log_info("nice: rule4: %s", _stock_id)
    elif rate2 > 9.8:
        # 600740
        this_price = ref_close(2)

        # 柱体、涨幅、中线
        zt_rule = abs(zt1) < 2.5 and abs(zt0) < 2.5
        rt_rule = abs(rate0) < 2.5 and abs(rate1) < 2.5
        md_rule = MD0 > this_price and MD1 > this_price
        log_debug("REF(2): zt: %s, md: %s, rt:%s", zt_rule, md_rule, rt_rule)

        # 对比均线量比
        vol_rate = ref_vol(2) / ref_vma10(5)
        log_debug("vol-rate: %.3f", vol_rate)

        # 累计涨幅1
        acc_rate = ((1 + rate3/100) * (1 + rate2/100) - 1) * 100
        log_debug("acc_rate: %.3f", acc_rate)

        # 累计涨幅2
        ACC_rate = (this_price / ref_open(7) - 1) * 100
        log_debug("ACC rate: %.3f", ACC_rate)

        if zt_rule and md_rule and rt_rule \
            and vol_rate > 3 and ACC_rate > 15\
            and macd and ma60_bigger:
            content1 = "rule2: %s - %s" % (_stock_id, _trade_date)
            log_info("nice: rule2: %s", _stock_id)
    elif rate3 > 9.8:
        # 600516
        this_price = ref_close(3)

        # 柱体、中线、涨幅
        zt_rule = abs(zt2) < 2.5 and abs(zt1) < 2.5 and abs(zt0) < 2.5
        md_rule = md0 > this_price and md1 > this_price and md2 > this_price
        rt_rule = abs(rate0) < 2.5 and abs(rate1) < 2.5 and abs(rate2) < 2.5
        log_debug("REF(3): zt: %s, md: %s, rt:%s", zt_rule, md_rule, rt_rule)

        # 对比均线量比
        vol_rate = ref_vol(3) / ref_vma10(6)
        log_debug("vol-rate: %.3f", vol_rate)

        # 累计涨幅
        acc_rate = ((1 + rate4/100) * (1 + rate3/100) - 1) * 100
        log_debug("acc_rate: %.3f", acc_rate)

        if zt_rule and md_rule and rt_rule \
            and vol_rate > 2 and acc_rate > 16\
            and macd and ma60_bigger:
            content1 = "rule1: %s - %s" % (_stock_id, _trade_date)
            log_info("nice: rule1: %s", _stock_id)

    if len(content1) > 0:
        subject = "high-narrow-flag: %s - %s" % (_stock_id, _trade_date)
        info  = get_basic_info_all(_stock_id, _db)
        content1 += "\n%s" % (info)
        log_info(subject)
        log_info("mail:\n%s", content1)
        if sai_is_product_mode():
            mailed = 1
            saimail_dev(subject, content1)
    else:
        log_info("sorry1: %s, %s", _stock_id, _trade_date)

    return 0



def flag_exec_algo(_max_date, _detail_df, _db):

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
    days1 = get_flag_max_price_days(_detail_df,  this_close)
    # log_debug("价格突破天数days1: %d", days1)

    # 收盘价突破 -- 容错
    days2 = get_flag_almost_max_price_days(_detail_df,  this_close)
    # log_debug("价格突破天数days2: %d", days2)

    # 成交量突破
    # log_debug("volume: [%.2f]", this_vol)
    days3 = get_flag_max_volume_days(_detail_df, this_vol)
    # log_debug("成交量突破天数days3: %d", days3)

    # 阳柱成交量大 sum(red) / sum(green) > 2.5
    n = 30
    sum1, sum2 = sum_flag_detail(_detail_df, n, _db)
    # log_debug("red-sum: %.3f", sum1)
    # log_debug("gre-sum: %.3f", sum2)
    vol_rate3 = -1
    if sum1 > 0 and sum2 > 0:
        vol_rate3 = sum1 / sum2
        # log_debug("合计量比vol_rate3: %.3f", vol_rate3)

    return rate, zt, days1, days2, days3, vol_rate1, vol_rate2, vol_rate3, ma60_bigger, ma10_divia


def sum_flag_detail(_detail_df, _days, _db):

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
def get_flag_max_price_days(_detail_df, _max_price):
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
def get_flag_almost_max_price_days(_detail_df, _max_price):
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
def get_flag_max_volume_days(_detail_df, _max_volume):
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



def flag_dynamic_calc_tech(_df):

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

    return 0


def flag_format_ref(_stock_id, _detail_df):

    # _detail MUST be sorted
    rv = ref_init4(_detail_df)
    if rv < 0:
        log_error("error: ref_init4")
        return -1

    _detail_df.sort_index(ascending=False, inplace=True)
    flag_dynamic_calc_tech(_detail_df)
    _detail_df.sort_index(ascending=True,  inplace=True)

    ref_set_tech4()

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


def get_flag_detail(_stock_id, _pub_date, _n, _db):
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


def get_flag_stock_list(_till, _db):
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


def flag_work_one_day_stock(_stock_id, _till,  _db):

    # 获取明细数据
    # 之前n1单位的交易数据
    n1 = 100
    detail_df = get_flag_detail(_stock_id, _till, n1, _db);
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
    if length <= 90:
        log_info("data-not-enough: %s", _stock_id)
        return 1

    # 格式化数据
    rv = flag_format_ref(_stock_id, detail_df)
    if rv < 0:
        log_error("error: flag_format_ref: %s", _stock_id)
        return -1

    rv = flag_analyzer(_stock_id, _till, detail_df, _db)
    if rv < 0:
        log_error("error: flag_analyzer: %s", _stock_id)
        return -1

    return 0


def flag_work_one_day(_till_date, _db):

    log_info("date: %s", _till_date)

    list_df = get_flag_stock_list(_till_date, _db)
    if list_df is None:
        log_error("error: get_flag_stock_list failure")
        return -1
    else:
        # log_debug("list df:\n%s", list_df)
        pass

    for row_index, row in list_df.iterrows():

        stock_id = row_index

        log_debug("[%s]------------------", stock_id)

        flag_work_one_day_stock(stock_id, _till_date, _db)


def regression(_db):

    # all
    max_date = "2017-07-12"
    days = 20

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
        flag_work_one_day(till_date, _db)

    return 0


def work():
    db = db_init()

    if sai_is_product_mode():
        till_date = get_date_by(0)


        till_date = "2017-07-05"
        stock_id = "600808"

        till_date = "2017-07-07"
        stock_id = "002161"

        till_date = "2017-06-30"
        stock_id = "600740"

        till_date = "2017-06-29"
        stock_id = "600516"

        # flag_work_one_day_stock(stock_id, till_date, db)

        till_date = get_date_by(0)
        flag_work_one_day(till_date, db)

    else:
        regression(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("flag2.log")

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

# flag.py
