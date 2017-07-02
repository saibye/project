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


def t1_exec_algo_check(_max_date, _detail_df, _db):

    # 涨幅
    rate = (ref_close(0) - ref_close(1)) / ref_close(1) * 100
    log_info("涨幅: %.2f", rate)

    # 柱体
    zt = (ref_close(0) - ref_open(0)) / ref_close(1) * 100
    log_info("柱体: %.2f", zt) 

    # 成交量比1: vol/ref_vma5(3)
    vol_rate1 = ref_vol(0) / ref_vma5(3)
    log_debug("当前量比1: %.3f", vol_rate1)

    # 成交量比2
    vol_rate2 = ref_vol(0) / ref_vma10(5)
    log_debug("当前量比2: %.3f", vol_rate2)


    # ma60 bigger
    ma60_bigger = ref_ma60(0) >= ref_ma60(10) and ref_ma60(5) >= ref_ma60(15)

    # ma10 diviate
    ma10_divia =  (ref_open(0) - ref_ma10(0)) / ref_ma10(0) * 100

    # today
    this_close = ref_close(0)
    this_vol   = ref_vol(0)

    # 收盘价突破
    # log_debug("close: [%.2f]", this_close)
    days1 = get_t1_max_price_days(_detail_df,  this_close)
    log_info("价格突破天数days1: %d", days1)

    # 收盘价突破 -- 容错
    days2 = get_t1_almost_max_price_days(_detail_df,  this_close)
    log_info("价格突破天数days2: %d", days2)

    # 成交量突破
    # log_debug("volume: [%.2f]", this_vol)
    days3 = get_t1_max_volume_days(_detail_df, this_vol)
    log_info("成交量突破天数days3: %d", days3)

    # 阳柱成交量大 sum(red) / sum(green) > 2.5
    n = 30
    sum1, sum2 = sum_t1_detail(_detail_df, n, _db)
    log_info("red-sum: %.3f", sum1)
    log_info("gre-sum: %.3f", sum2)
    vol_rate3 = -1
    if sum1 > 0 and sum2 > 0:
        vol_rate3 = sum1 / sum2
        log_info("合计量比vol_rate3: %.3f", vol_rate3)

    log_debug("vol0[%.3f, %.3f, %.3f]", ref_amount(0), ref_vma5(0), ref_vma10(0))
    log_debug("vol1[%.3f, %.3f, %.3f]", ref_amount(1), ref_vma5(1), ref_vma10(1))
    log_debug("vol2[%.3f, %.3f, %.3f]", ref_amount(2), ref_vma5(2), ref_vma10(2))

    log_debug("macd0[%.3f = %.3f - %.3f]", ref_macd(0), ref_diff(0), ref_dea(0))
    log_debug("macd1[%.3f = %.3f - %.3f]", ref_macd(1), ref_diff(1), ref_dea(1))
    log_debug("macd2[%.3f = %.3f - %.3f]", ref_macd(2), ref_diff(2), ref_dea(0))

    log_debug("tech0: ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma10(0), ref_ma20(0), ref_ma30(0), ref_ma60(0))
    log_debug("tech1: ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma10(1), ref_ma20(1), ref_ma30(1), ref_ma60(1))
    log_debug("tech2: ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma10(2), ref_ma20(2), ref_ma30(2), ref_ma60(2))
    log_debug("tech3: ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma10(3), ref_ma20(3), ref_ma30(3), ref_ma60(3))
    log_debug("tech4: ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma10(4), ref_ma20(4), ref_ma30(4), ref_ma60(4))
    log_debug("tech5: ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma10(5), ref_ma20(5), ref_ma30(5), ref_ma60(5))

    return rate, zt, days1, days2, days3, vol_rate1, vol_rate2, vol_rate3, ma60_bigger, ma10_divia


def sum_t1_detail(_detail_df, _days, _db):

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
            log_info("counter: reach: %d", _days)
            break

    return sum1, sum2

"""
价格突破前高
"""
def get_t1_max_price_days(_detail_df, _max_price):
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
def get_t1_almost_max_price_days(_detail_df, _max_price):
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
def get_t1_max_volume_days(_detail_df, _max_volume):
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


def get_t1_detail(_stock_id, _pub_date, _n, _db):
    sql = "select stock_id, pub_date, open_price, close_price, \
deal_total_count total, last_close_price last, \
high_price, low_price \
from tbl_day a where a.stock_id  = '%s' and   a.pub_date <= '%s' \
order by pub_date desc limit %d" % (_stock_id, _pub_date, _n)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        return df


def work_one_day(_trade_date, _db):

    log_info("date: %s", _trade_date)
    ref_set_date(_trade_date)

    rv = ref_init(_db)
    if rv != 0:
        log_error("error: ref_init")
        return rv

    begin = get_micro_second()

    stocks = ref_get_list()
    rownum = 0
    content1 = "" #
    for s_index, s_val in stocks.iteritems():
        rownum = rownum + 1
        stock_id = s_index
        log_info("%s -- %s", _trade_date, stock_id)
        rv = ref_set_with_tech(stock_id)
        if rv < 0:
            log_error("error: ref_set_with_tech: %s", stock_id)
            return rv
        elif rv < 90:
            log_error("warn: %s small %d", stock_id, rv)
            continue

        # 获取明细数据
        # 之前n单位的交易数据
        n = 300
        detail_df = get_t1_detail(stock_id, _trade_date, n, _db);
        if detail_df is None:
            log_info("[%s, %s] detail is none", stock_id, _trade_date)
            return -1
        elif detail_df.empty:
            log_debug("detail_df is empty: [%d]", len(detail_df))
            return 1
        else:
            length = len(detail_df)
            log_debug("detail: %d", length)

        if length <= 90:
            log_info("data-not-enough: %s", stock_id)
            return 1

        rate, zt, days1, days2, days3, vol_rate1, vol_rate2, vol_rate3, \
            ma60_bigger, ma10_divia =  t1_exec_algo_check(_trade_date, detail_df, _db)

        log_info("%.2f, %.2f; %d, %d, %d; %.2f, %.2f, %.2f; %s, %.2f",
                rate, zt, days1, days2, days3, vol_rate1, vol_rate2, vol_rate3, ma60_bigger, ma10_divia)


    log_info("%d costs %d us", rownum, get_micro_second() - begin)

    mailed = 0

    if len(content1) > 0:
        subject = "t1: %s" % (_trade_date)
        log_info(subject)
        log_info("mail:\n%s", content1)
        if sai_is_product_mode():
            mailed = 1
            saimail(subject, content1)
    else:
        log_info("sorry1: %s", _trade_date)


    return


def regression(_db):

    # all
    max_date = "2017-06-26"
    days = 200

    # 000885
    max_date = "2017-01-18"
    days = 1

    # 603603
    max_date = "2017-05-10"
    days = 1

    log_info("regress")

    date_df = get_recent_pub_date(max_date, days, _db)
    if date_df is None:
        log_error("error: get_recent_pub_date failure")
        return -1
    else:
        date_df.set_index("pub_date", inplace=True)

    for row_index, row in date_df.iterrows():
        trade_date = row_index
        log_debug("[%s]------------------", trade_date)
        work_one_day(trade_date, _db)

    return 0


def work():
    db = db_init()

    if sai_is_product_mode():
        # regression(db)
        trade_date = get_date_by(0)
        trade_date = "2017-06-16"
        work_one_day(trade_date, db)
    else:
        regression(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("t1.log")

    log_info("let's begin here!")

    if sai_is_product_mode():
        if today_is_weekend():
            log_info("today is weekend, exit")
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


# t1.py
