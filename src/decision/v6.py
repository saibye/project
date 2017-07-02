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
# 策略：日线，最大量，最大价，伴随穿越5线
#######################################################################


def get_v6_list(_till, _db):
    sql = "select distinct stock_id from tbl_day \
where pub_date = \
(select max(pub_date) from tbl_day \
where pub_date <= '%s')" % (_till)

    log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        df.set_index("stock_id", inplace=True)
        return df


def get_v6_n1_max(_stock_id, _till, _n1, _db):
    sql = "select pub_date, deal_total_count, close_price, stock_id from  \
( select pub_date, deal_total_count, close_price, open_price, stock_id from tbl_day where \
 stock_id = '%s' \
 and pub_date <= '%s' \
 order by pub_date desc  \
 limit %d ) t1 \
where close_price > open_price \
order by deal_total_count desc limit 1" % (_stock_id, _till, _n1)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        return df


def get_v6_n2_max(_stock_id, _till2, _n2, _db):
    sql = "select pub_date, deal_total_count from  \
( select pub_date, deal_total_count from tbl_day where \
 stock_id = '%s' \
 and pub_date <= '%s' \
 order by pub_date desc  \
 limit %d ) t1 \
order by deal_total_count desc limit 1" % (_stock_id, _till2, _n2)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        return df


"""
最大vol前的成交日数据
"""
def get_v6_detail(_stock_id, _pub_date, _n3, _db):
    sql = "select stock_id, pub_date, open_price, close_price, \
deal_total_count total, last_close_price last, \
high_price, low_price \
from tbl_day a where a.stock_id  = '%s' and   a.pub_date <= '%s' \
order by pub_date desc limit %d" % (_stock_id, _pub_date, _n3)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        # df.set_index("pub_date", inplace=True)
        # log_debug("detail df: \n%s", df)
        return df

"""
价格突破前高
"""
def get_v6_max_price_days(_detail_df, _max_price):
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
def get_v6_almost_max_price_days(_detail_df, _max_price):
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
def get_v6_max_volume_days(_detail_df, _max_volume):
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



def sum_v6_detail(_detail_df, _days, _db):

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


def v6_dynamic_calc_tech(_df):

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

    return 0


def v6_format_ref(_stock_id, _date_df, _detail_df):

    rv = ref_init2(_date_df, _detail_df)
    if rv < 0:
        log_error("error: ref_init2")
        return -1

    # format
    ref_set(_stock_id)

    _detail_df.sort_index(ascending=False, inplace=True)
    v6_dynamic_calc_tech(_detail_df)
    _detail_df.sort_index(ascending=True,  inplace=True)

    # log_debug("after tech: \n%s", _detail_df)

    ref_set_tech(_stock_id)

    if ref_amount(0) <= 0 or ref_close(0) <= 0:
        log_error("error: invalid data: %s: %.2f, %.2f", _stock_id, ref_close(0), ref_amount(0))
        return -1

    return 0


#########################
# 算法检查
#########################
def v6_exec_algo_check(_db):

    # 放量大涨 rate >= 2.5
    rate = (ref_close(0) - ref_close(1)) / ref_close(1) * 100
    log_info("涨幅: %.2f", rate)

    # 阳柱体 zt >= 2.5
    zt = (ref_close(0) - ref_open(0)) / ref_close(1) * 100
    log_info("阳柱: %.2f", zt)

    if ref_vma5(3) == 0:
        return -1, -1, -1, -1, False, False, False

    # 成交量比 : vol/ref_vma5(3)
    vol_rate2 = ref_vol(0) / ref_vma5(3)
    log_debug("当前量比: %.3f", vol_rate2)


    # ma60 bigger
    big_sub1 = ref_ma60(0) >= ref_ma60(5) and ref_ma60(1) >= ref_ma60(6) and ref_ma60(2) >= ref_ma60(7)
    big_sub2 = ref_ma60(6) >= ref_ma60(11) and ref_ma60(7) >= ref_ma60(12) and ref_ma60(8) >= ref_ma60(13)
    ma60_bigger = big_sub1 and big_sub2

    # ma10 diviate
    ma10_divia =  (ref_open(0) - ref_ma10(0)) / ref_ma10(0) * 100

    return rate, zt, vol_rate2, ma60_bigger, ma10_divia



def work_one_stock(_stock_id, _till,  _db):

    good = 0
    zt   = 0
    content = ""

    begin = get_micro_second()

    # 最近n1天的最大vol，是最近n2天的最大vol
    # n3: 最近n3价格最高
    # n4: 最近n4天的数据
    # n5: 最近n5天的红绿成交量加总
    if sai_is_product_mode():
        n1 = 1
        n2 = 100
        n3 = 100
        n4 = 300
        n5 = 30
    else:
        n1 = 1
        n2 = 100
        n3 = 100
        n4 = 300
        n5 = 30

    max_date_time = ""
    max_volume = ""


    # 2017-6-21
    n1_df = get_v6_n1_max(_stock_id, _till, n1, _db)
    if n1_df is None:
        log_info("n1(%d) not match!", n1)
        return -1
    elif n1_df.empty:
        log_debug("n1_df is empty: [%d]", len(n1_df))
        return 1
    else:
        n1_max_date_time = n1_df.iloc[0, 0]
        n1_max_volume    = n1_df.iloc[0, 1]
        n1_max_close     = n1_df.iloc[0, 2]
        log_debug("n1_date [%s]", n1_max_date_time);
        log_debug("n1_vol  [%s]", n1_max_volume);
        log_debug("n1_close[%.3f]", n1_max_close);
        n1_df = n1_df.set_index("stock_id")
        n1_df["1"] = "1"

    # 2017-6-21
    n2_df = get_v6_n2_max(_stock_id, n1_max_date_time, n2, _db)
    if n2_df is None:
        log_info("n2(%d) not match!", n2)
        return -1
    elif n2_df.empty:
        log_debug("n2_df is empty: [%d]", len(n2_df))
        return 1
    else:
        n2_max_date_time = n2_df.iloc[0, 0]
        n2_max_volume    = n2_df.iloc[0, 1]
        log_debug("n2_date[%s], n2_vol[%.2f]", n2_max_date_time, n2_max_volume);

    # check max-vol(n1) == max-vol(n2)
    if n2_max_date_time != n1_max_date_time:
        log_info("time: [%s] != [%s]", n1_max_date_time, n2_max_date_time)
        return 1
    else:
        log_info("match the same time: [%s]", n1_max_date_time)

    if n2_max_volume != n1_max_volume:
        log_info("not the same volume: [%s] != [%s]", n1_max_volume, n2_max_volume)
        return 1
    else:
        log_info("match the same volume: [%s]", n1_max_volume)


    # 获取明细数据
    # 之前n4单位的交易数据
    detail_df = get_v6_detail(_stock_id, n1_max_date_time, n4, _db);
    if detail_df is None:
        log_info("[%s, %s] detail is none", _stock_id, n1_max_date_time)
        return -1
    elif detail_df.empty:
        log_debug("detail_df is empty: [%d]", len(detail_df))
        return 1
    else:
        log_debug("n4: len[%d]", len(detail_df))

    max_date_time = n1_max_date_time
    max_volume    = n1_max_volume
    log_debug("%s: max_date_time: [%s]", _stock_id, max_date_time)
    log_debug("%s: max_volume:    [%s]", _stock_id, max_volume)

    content += "%s @ %s\n" % (_stock_id, max_date_time)

    log_debug("max-close: [%.3f]", n1_max_close)

    # 收盘价突破
    days1 = get_v6_max_price_days(detail_df,  n1_max_close)
    log_info("价格突破天数days1: %d", days1)

    # 收盘价突破 -- 容错
    days2 = get_v6_almost_max_price_days(detail_df,  n1_max_close)
    log_info("价格突破天数days2: %d", days2)

    # TODO
    if days1 >= 100 or days2 >= 100:
        log_info("价格突破前高: %d > %d", days1, n3)
    else:
        log_info("sorry: price: 价格未突破[%d < %d]", days1, n3)
        return 1

    # 成交量突破
    log_debug("max-volume: [%.2f]", n1_max_volume)
    days3 = get_v6_max_volume_days(detail_df,  n1_max_volume)
    log_info("成交量突破天数days3: %d", days3)

    length = len(detail_df)
    log_debug("detail: %d", length)

    if length <= 90:
        log_info("data-not-enough: %s", _stock_id)
        return 1

    # 阳柱成交量大 sum(red) / sum(green) > 2.5
    sum1, sum2 = sum_v6_detail(detail_df, n5, _db)
    log_info("red-sum: %.3f", sum1)
    log_info("gre-sum: %.3f", sum2)
    vol_rate = -1
    if sum1 > 0 and sum2 > 0:
        vol_rate = sum1 / sum2
        log_info("合计量比vol_rate: %.3f", vol_rate)


    # 格式化数据
    rv = v6_format_ref(_stock_id, n1_df, detail_df)
    if rv < 0:
        log_error("error: v6_format_ref: %s", _stock_id)
        return -1

    log_debug("ref0[%.3f, %.3f] -- [%.3f, %.3f]", ref_open(0), ref_close(0), ref_amount(0), ref_vma5(0))
    log_debug("ref1[%.3f, %.3f] -- [%.3f, %.3f]", ref_open(1), ref_close(1), ref_amount(1), ref_vma5(1))
    log_debug("ref2[%.3f, %.3f] -- [%.3f, %.3f]", ref_open(2), ref_close(2), ref_amount(2), ref_vma5(2))

    log_debug("tech0[%.3f = %.3f - %.3f] - [%.3f, %.3f]", ref_macd(0), ref_diff(0), ref_dea(0), ref_vma5(0), ref_vma10(0))
    log_debug("tech1[%.3f = %.3f - %.3f] - [%.3f, %.3f]", ref_macd(1), ref_diff(1), ref_dea(1), ref_vma5(1), ref_vma10(1))
    log_debug("tech2[%.3f = %.3f - %.3f] - [%.3f, %.3f]", ref_macd(2), ref_diff(2), ref_dea(0), ref_vma5(2), ref_vma10(2))

    # 均线发散
    log_debug("tech0: ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma10(0), ref_ma20(0), ref_ma30(0), ref_ma60(0))
    log_debug("tech1: ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma10(1), ref_ma20(1), ref_ma30(1), ref_ma60(1))
    log_debug("tech2: ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma10(2), ref_ma20(2), ref_ma30(2), ref_ma60(2))
    log_debug("tech3: ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma10(3), ref_ma20(3), ref_ma30(3), ref_ma60(3))
    log_debug("tech4: ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma10(4), ref_ma20(4), ref_ma30(4), ref_ma60(4))
    log_debug("tech5: ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma10(5), ref_ma20(5), ref_ma30(5), ref_ma60(5))


    # 涨幅，柱体
    rate, zt, vol_rate2, ma60_bigger, ma10_divia = v6_exec_algo_check(_db)
    log_info("%.3f, %.3f, %.3f, %s, %.3f", rate, zt, vol_rate2, ma60_bigger, ma10_divia)

    macd = ref_macd(0)
    diff = ref_diff(0)
    dea  = ref_dea(0)
    log_info("macd: %.3f = %.3f - %.3f", macd, diff, dea)

    # 600050 @ 2016-10-11
    rule1 = rate >= 10 and zt >= 10 \
               and vol_rate >= 1.4 \
               and vol_rate2 >= 8 \
               and days1 >= 150 \
               and days3 >= 150 \
               and macd > 0 and diff > 0 and dea > -0.02 \
               and ma60_bigger \
               and abs(ma10_divia)  < 3

    # ...
    rule2 = False and rate >= 9 and zt >= 6 \
               and vol_rate >= 2.0 \
               and vol_rate2 >= 15 \
               and days1 >= 200 \
               and days3 >= 200 \
               and macd > 0 and diff > 0 and dea > -0.04

    #
    if rule1:
        log_info("rule1: %s", _stock_id)
        content += "rule1\n"
    elif rule2:
        log_info("rule2: %s", _stock_id)
        content += "rule2\n"
    else:
        log_info("sorry: not match")
        return 1

    log_info("nice+++ %s, %s", _stock_id, max_date_time)

    content += "涨幅: %.2f%%\n" % (get_chg_rate(_stock_id))

    content += "+合计量比: %.2f\n"  % (vol_rate)
    content += "+当前量比: %.2f\n"  % (vol_rate2)
    content += "+收盘价突破: %d(unit)\n"    % (days1)
    content += "+成交量突破: %d(unit)\n"  % (days3)
    content += "+涨幅、柱体: %.2f%%, %.2f%%\n"  % (rate, zt)

    content += get_basic_info_all(_stock_id, _db)

    subject = "big volume+macd: %s @%s" % (_stock_id, max_date_time)
    log_info("mail: \n%s\n%s", subject, content)
    saimail(subject,  content)

    log_info("it costs %d us", get_micro_second() - begin)

    return 0



def regression_one(_db):

    till = get_date_by(-1)


    # 
    till = "2017-01-11"
    stock_id = "002302"

    # 600050 (done)
    till = "2016-10-11"
    stock_id = "600050"


    log_debug("[%s]------------------", stock_id)

    work_one_stock(stock_id, till, _db)

    return 0

def regression(_db):
    max_date = "2017-01-11"
    days = 2

    max_date = "2016-10-11"
    days = 2

    max_date = "2017-06-29"
    days = 100

    log_info("regress-all")

    date_df = get_recent_pub_date(max_date, days, _db)
    if date_df is None:
        log_error("error: get_recent_pub_date failure")
        return -1
    else:
        date_df.set_index("pub_date", inplace=True)

    for row_index, row in date_df.iterrows():
        trade_date = row_index
        log_debug("[%s]------------------", trade_date)
        work_one(trade_date, _db)


def work_one(_date, _db):
    list_df = get_v6_list(_date, _db)
    if list_df is None:
        log_error("error: get_v6_list failure")
        return -1
    else:
        log_debug("list df: \n%s", list_df)

    for row_index, row in list_df.iterrows():

        stock_id = row_index

        log_debug("====[%s][%s]====", _date, stock_id)

        work_one_stock(stock_id, _date, _db)


def xxx(_db):

    if sai_is_product_mode():
        till = get_date_by(-1)
    else:
        regression_one(_db)
        return

    # test only
    regression(_db)
    return
    # delete me
        
    log_info("till: %s", till)

    work_one(till)

    return 0




def work():
    db = db_init()

    xxx(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("v6.log")

    log_info("let's begin here!")

    if sai_is_product_mode():
        # check holiday
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
exit()

#######################################################################


# v6.py
