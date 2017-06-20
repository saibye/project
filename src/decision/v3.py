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
# 策略：
#######################################################################


def get_v3_list(_till, _db):
    # sql = "select distinct stock_id from tbl_30min where pub_date_time = (select max(pub_date_time) from tbl_30min)"
    sql = "select distinct stock_id from tbl_30min \
where pub_date_time = \
(select max(pub_date_time) from tbl_30min \
where pub_date_time <= '%s')" % (_till)

    log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        df.set_index("stock_id", inplace=True)
        return df


"""
最近n2天的最大vol，是最近n1天的最大vol
+阳线
"""
def get_v3_max_vol(_stock_id, _till, _n1, _n2, _db):
    sql = "select pub_date_time, deal_total_count, stock_id from tbl_30min where \
stock_id = '%s' \
and pub_date_time <= '%s' \
and pub_date_time >= \
( \
select min(pub_date_time) from  \
( \
    select pub_date_time, deal_total_count from tbl_30min \
    where pub_date_time <='%s' \
    and stock_id = '%s' \
    and close_price > open_price \
    order by pub_date_time desc \
    limit %d \
 ) t1 \
) \
and deal_total_count =  \
( \
select max(deal_total_count) from \
( \
select pub_date_time, deal_total_count from tbl_30min \
where pub_date_time <='%s' \
and stock_id = '%s' \
and close_price > open_price \
order by pub_date_time desc \
limit %d \
) t2 \
) \
and  \
( \
select max(deal_total_count) from \
( \
select pub_date_time, deal_total_count from tbl_30min \
where pub_date_time <='%s' \
and stock_id = '%s' \
and close_price > open_price \
order by pub_date_time desc \
limit %d \
) t3 \
) \
= \
( \
select max(deal_total_count) from \
( \
select pub_date_time, deal_total_count from tbl_30min \
where pub_date_time <='%s' \
and stock_id = '%s' \
and close_price > open_price \
order by pub_date_time desc \
limit %d \
) t4 \
) \
order by pub_date_time desc limit 1" % (_stock_id, _till, \
    _till, _stock_id, _n1, \
    _till, _stock_id, _n1, \
    _till, _stock_id, _n1, \
    _till, _stock_id, _n2)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        # df.set_index("pub_date_time", inplace=True)
        # log_debug("max df: \n%s", df)
        return df


"""
最近n2天的最大vol，是最近n1天的最大vol
"""
def get_v3_max_vol0(_stock_id, _till, _n1, _n2, _db):
    sql = "select pub_date_time, deal_total_count, stock_id from tbl_30min where \
stock_id = '%s' \
and pub_date_time <= '%s' \
and pub_date_time >= \
( \
select min(pub_date_time) from  \
( \
    select pub_date_time, deal_total_count from tbl_30min \
    where pub_date_time <='%s' \
    and stock_id = '%s' \
    order by pub_date_time desc \
    limit %d \
 ) t1 \
) \
and deal_total_count =  \
( \
select max(deal_total_count) from \
( \
select pub_date_time, deal_total_count from tbl_30min \
where pub_date_time <='%s' \
and stock_id = '%s' \
order by pub_date_time desc \
limit %d \
) t2 \
) \
and  \
( \
select max(deal_total_count) from \
( \
select pub_date_time, deal_total_count from tbl_30min \
where pub_date_time <='%s' \
and stock_id = '%s' \
order by pub_date_time desc \
limit %d \
) t3 \
) \
= \
( \
select max(deal_total_count) from \
( \
select pub_date_time, deal_total_count from tbl_30min \
where pub_date_time <='%s' \
and stock_id = '%s' \
order by pub_date_time desc \
limit %d \
) t4 \
) \
order by pub_date_time desc limit 1" % (_stock_id, _till, \
    _till, _stock_id, _n1, \
    _till, _stock_id, _n1, \
    _till, _stock_id, _n1, \
    _till, _stock_id, _n2)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        # df.set_index("pub_date_time", inplace=True)
        # log_debug("max df: \n%s", df)
        return df


"""
最大vol前的成交日数据
"""
def get_v3_detail(_stock_id, _pub_date_time, _n3, _db):
    sql = "select stock_id, pub_date_time, open_price, close_price, \
deal_total_count total, last_close_price last, \
high_price, low_price \
from tbl_30min a where a.stock_id  = '%s' and   a.pub_date_time <= '%s' \
order by pub_date_time desc limit %d" % (_stock_id, _pub_date_time, _n3)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        # df.set_index("pub_date_time", inplace=True)
        # log_debug("detail df: \n%s", df)
        return df



"""
突破前高
"""
def check_v3_max_price(_stock_id, _till, _n3, _db):
    sql = "select pub_date_time, deal_total_count from tbl_30min where \
stock_id = '%s' \
and pub_date_time = '%s' \
and close_price= \
( \
select max(close_price) close_price from \
( \
select pub_date_time, close_price from tbl_30min \
where pub_date_time <='%s' \
and stock_id = '%s' \
order by pub_date_time desc \
limit %d \
) t1 \
) \
order by pub_date_time desc limit 1" % (_stock_id, _till, \
    _till, _stock_id, _n3)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db)
    if df is None:
        log_info("not match1", _n3)
        return 0
    elif df.empty:
        log_debug("not match2: [%d]", len(df))
        return 0
    else:
        log_debug("is [%d] highest price", _n3)
        return 1



def sum_v3_detail(_detail_df, _days, _db):

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


def v3_dynamic_calc_tech(_df):

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


def v3_format_ref(_stock_id, _date_df, _detail_df):

    rv = ref_init2(_date_df, _detail_df)
    if rv < 0:
        log_error("error: ref_init2")
        return -1

    # format
    ref_set3(_stock_id)

    _detail_df.sort_index(ascending=False, inplace=True)
    v3_dynamic_calc_tech(_detail_df)
    _detail_df.sort_index(ascending=True,  inplace=True)

    # log_debug("after tech: \n%s", _detail_df)

    ref_set_tech(_stock_id)

    log_debug("ref0[%.3f] -- [%.3f]", ref_close(0), ref_amount(0))
    log_debug("ref1[%.3f] -- [%.3f]", ref_close(1), ref_amount(1))
    log_debug("ref2[%.3f] -- [%.3f]", ref_close(2), ref_amount(2))

    log_debug("tech0[%.3f] - [%.3f] - [%.3f] - [%.3f]", ref_ma5(0), ref_ma10(0), ref_vma5(0), ref_vma10(0))
    log_debug("tech1[%.3f] - [%.3f] - [%.3f] - [%.3f]", ref_ma5(1), ref_ma10(1), ref_vma5(1), ref_vma10(1))
    log_debug("tech2[%.3f] - [%.3f] - [%.3f] - [%.3f]", ref_ma5(2), ref_ma10(2), ref_vma5(2), ref_vma10(2))

    return 0


#########################
# 算法检查
#########################
def v3_exec_algo_check(_db):

    # 放量大涨 rate >= 2.5
    rate = (ref_close(0) - ref_close(1)) / ref_close(1) * 100
    log_info("rate: %.2f", rate)

    # 阳柱体 zt >= 2.5
    zt = (ref_close(0) - ref_open(0)) / ref_close(1) * 100
    log_info("zt: %.2f", zt)

    # 阳柱到顶: close @= high
    rate2 = ref_close(0) / ref_high(0) * 100
    log_debug("rate2: %.3f", rate2)

    # 成交量 : ref_vma5(3) >= 6
    vol_rate2 = ref_vol(0) / ref_vma5(3)
    log_debug("vol-rate2: %.3f", vol_rate2)

    # 均线发散
    log_debug("tech0: ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma10(0), ref_ma20(0), ref_ma30(0), ref_ma60(0))
    log_debug("tech1: ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma10(1), ref_ma20(1), ref_ma30(1), ref_ma60(1))
    log_debug("tech2: ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma10(2), ref_ma20(2), ref_ma30(2), ref_ma60(2))

    # 002458
    # 20, 30, 60  
    fasan_sub1 = ref_ma20(0) > ref_ma30(0) and  ref_ma30(0) > ref_ma60(0)
    fasan_sub2 = ref_ma20(1) > ref_ma30(1) and  ref_ma30(1) > ref_ma60(1)
    fasan_sub3 = ref_ma20(2) > ref_ma30(2) and  ref_ma30(2) > ref_ma60(2)
    fasan_rule1 = fasan_sub1 and fasan_sub2 and fasan_sub3

    # 000025
    # 10, 20, 30  
    fasan_sub1 = ref_ma10(0) > ref_ma20(0) and  ref_ma20(0) > ref_ma30(0)
    fasan_sub2 = ref_ma10(1) > ref_ma20(1) and  ref_ma20(1) > ref_ma30(1)
    fasan_sub3 = ref_ma10(2) > ref_ma20(2) and  ref_ma20(2) > ref_ma30(2)
    fasan_rule2 = fasan_sub1 and fasan_sub2 and fasan_sub3

    fasan_ma20 = ref_ma20(0) > ref_ma20(1) and  ref_ma20(1) > ref_ma20(2)

    rule1 = fasan_ma20 and fasan_rule1
    rule2 = fasan_ma20 and fasan_rule2

    # 贴近ma20
    ma20_rate = ref_close(3) / ref_ma20(3) * 100
    ma20_dis = abs(ma20_rate - 100)


    # 002302
    # cross 5
    cross5_sub1 = ref_close(1) > ref_ma5(1) and  ref_close(1) > ref_ma10(1) and ref_close(1) > ref_ma20(1) and ref_close(1) > ref_ma30(1) and ref_close(1) > ref_ma60(1) and \
                  ref_open(1) < ref_ma5(1) and  ref_open(1) < ref_ma10(1) and ref_open(1) < ref_ma20(1) and ref_open(1) < ref_ma30(1) and ref_open(1) < ref_ma60(1)
    cross5_sub2 = ref_close(2) > ref_ma5(2) and  ref_close(2) > ref_ma10(2) and ref_close(2) > ref_ma20(2) and ref_close(2) > ref_ma30(2) and ref_close(2) > ref_ma60(2) and \
                  ref_open(2) < ref_ma5(2) and  ref_open(2) < ref_ma10(2) and ref_open(2) < ref_ma20(2) and ref_open(2) < ref_ma30(2) and ref_open(2) < ref_ma60(2)
    cross5_sub3 = ref_close(3) > ref_ma5(3) and  ref_close(3) > ref_ma10(3) and ref_close(3) > ref_ma20(3) and ref_close(3) > ref_ma30(3) and ref_close(3) > ref_ma60(3) and \
                  ref_open(3) < ref_ma5(3) and  ref_open(3) < ref_ma10(3) and ref_open(3) < ref_ma20(3) and ref_open(3) < ref_ma30(3) and ref_open(3) < ref_ma60(3)
    cross5_sub4 = ref_close(4) > ref_ma5(4) and  ref_close(4) > ref_ma10(4) and ref_close(4) > ref_ma20(4) and ref_close(4) > ref_ma30(4) and ref_close(4) > ref_ma60(4) and \
                  ref_open(4) < ref_ma5(4) and  ref_open(4) < ref_ma10(4) and ref_open(4) < ref_ma20(4) and ref_open(4) < ref_ma30(4) and ref_open(4) < ref_ma60(4)
    log_info("[%.3f, %.3f]", ref_open(4), ref_close(4) )
    log_info("[%.3f, %.3f, %.3f, %.3f, %.3f]", ref_ma5(4), ref_ma10(4), ref_ma20(4), ref_ma30(4), ref_ma60(4))
    cross5_rule1 = cross5_sub1 or cross5_sub2 or cross5_sub3 or cross5_sub4

    # 002302
    # cross4
    cross4_sub1 = ref_close(1) > ref_ma5(1) and  ref_close(1) > ref_ma10(1) and ref_close(1) > ref_ma20(1) and ref_close(1) > ref_ma30(1) and ref_close(1) > ref_ma60(1) and \
                  ref_open(1) < ref_ma5(1) and  ref_open(1) < ref_ma10(1) and ref_open(1) < ref_ma20(1) and ref_open(1) < ref_ma30(1)
    cross4_sub2 = ref_close(2) > ref_ma5(2) and  ref_close(2) > ref_ma10(2) and ref_close(2) > ref_ma20(2) and ref_close(2) > ref_ma30(2) and ref_close(2) > ref_ma60(2) and \
                  ref_open(2) < ref_ma5(2) and  ref_open(2) < ref_ma10(2) and ref_open(2) < ref_ma20(2) and ref_open(2) < ref_ma30(2)
    cross4_sub3 = ref_close(3) > ref_ma5(3) and  ref_close(3) > ref_ma10(3) and ref_close(3) > ref_ma20(3) and ref_close(3) > ref_ma30(3) and ref_close(3) > ref_ma60(3) and \
                  ref_open(3) < ref_ma5(3) and  ref_open(3) < ref_ma10(3) and ref_open(3) < ref_ma20(3) and ref_open(3) < ref_ma30(3)
    cross4_rule1 = cross4_sub1 or cross4_sub2 or cross4_sub3

    return rate, zt, rate2, vol_rate2, rule1, rule2, ma20_dis, cross5_rule1, cross4_rule1



def work_one(_stock_id, _till,  _db):

    good = 0
    zt   = 0
    content = ""

    begin = get_micro_second()

    # 最近n1天的最大vol，是最近n2天的最大vol
    # n3 最近n3价格最高
    # n4 最近n4天的数据
    # n5 最近n5天的红绿成交量加总
    if sai_is_product_mode():
        n1 = 8
        n2 = 200
        n3 = 75
        n4 = 300
        n5 = 30
    else:
        n1 = 8
        n2 = 200
        n3 = 75
        n4 = 300
        n5 = 30

    max_date_time = ""
    max_volume = ""

    content += "%s @ %s\n" % (_stock_id, _till)

    # PRE check1
    # max(volume), pub_date_time
    date_df = get_v3_max_vol(_stock_id, _till, n1, n2, _db)
    if date_df is None:
        log_info("n1(%d), n2(%d) not match!", n1, n2)
        return -1
    elif date_df.empty:
        log_debug("date_df is empty: [%d]", len(date_df))
        return 1
    else:
        # log_debug("max: len[%d]\n%s", len(date_df), date_df)
        max_date_time = date_df.iloc[0, 0]
        max_volume    = date_df.iloc[0, 1]
        date_df = date_df.set_index("stock_id")
        date_df["1"] = "1"
        log_debug("max_date_time: [%s]", max_date_time)
        log_debug("max_volume:    [%s]", max_volume)

    # PRE check2
    # 
    high = check_v3_max_price(_stock_id, max_date_time, n3, _db)
    if high:
        log_info("+1 价格突破前高: %s", max_date_time)
    else:
        log_info("sorry: price: 价格未突破")
        return 1

    # 获取明细数据
    # 之前n4单位的交易数据
    detail_df = get_v3_detail(_stock_id, max_date_time, n4, _db);
    if detail_df is None:
        log_info("[%s, %s, %s] detail is none", _stock_id, max_date_time, max_volume)
        return -1
    elif detail_df.empty:
        log_debug("detail_df is empty: [%d]", len(detail_df))
        return 1
    else:
        log_debug("max: len[%d]", len(detail_df))

    length = len(detail_df)
    log_debug("detail: %d", length)

    if length <= 8:
        log_info("data-not-enough: %s", _stock_id)
        return 1

    # 阳柱成交量大 sum(red) / sum(green) > 2.5
    sum1, sum2 = sum_v3_detail(detail_df, n5, _db)
    log_info("red-sum: %.3f", sum1)
    log_info("gre-sum: %.3f", sum2)
    vol_rate = -1
    if sum1 > 0 and sum2 > 0:
        vol_rate = sum1 / sum2
        log_info("%s: vol-rate: %.3f", _stock_id, vol_rate)


    # 格式化数据
    rv = v3_format_ref(_stock_id, date_df, detail_df)
    if rv < 0:
        log_error("error: v3_format_ref")
        return -1

    # 涨幅，柱体，收盘/最高，量比，发散1，发散2，距离ma20
    rate, zt, rate2, vol_rate2, fasan_rule1, fasan_rule2, ma20_dis, cross5_rule, cross4_rule = v3_exec_algo_check(_db)
    log_info("%.3f, %.3f, %.3f, %.3f, %s, %s, %.3f, %s, %s",
            rate, zt, rate2, vol_rate2, fasan_rule1, fasan_rule2, ma20_dis, cross5_rule, cross4_rule)


    # 002458
    rule1 = rate >= 2.5 and zt >= 2.5 and rate2 >= 98.8 \
               and vol_rate2 >= 6 and fasan_rule1 \
               and ref_close(0) > ref_ma20(0) and ref_open(3) < ref_ma20(3) \
               and vol_rate >= 2.48

    # 000025, 2017-06-08 10:00:00
    rule2 = rate >= 8.0 and zt >= 8.0 and rate2 >= 98.8 \
               and vol_rate2 >= 15 and fasan_rule2 \
               and ref_close(0) > ref_ma20(0) and ma20_dis <= 2 \
               and vol_rate >= 2.48

    # 002302, 2017-06-14 11:00:00
    rule3 = rate >= 4.7 and zt >= 4.7 and rate2 >= 98.0 \
               and vol_rate2 >= 15  \
               and ref_close(0) > ref_ma20(0) \
               and vol_rate >= 1.8 \
               and cross5_rule

    # 000877, 2017-06-14 11:00:00
    rule4 = rate >= 4.7 and zt >= 4.7 and rate2 >= 98.0 \
               and vol_rate2 >= 15  \
               and ref_close(0) > ref_ma20(0) \
               and vol_rate >= 1.8 \
               and cross5_rule

    # 002591, 2017-06-15 13:30:00
    rule5 = rate >= 7 and zt >= 7 and rate2 >= 98.0 \
               and vol_rate2 >= 18 \
               and ref_close(0) > ref_ma20(0) \
               and vol_rate >= 3 \
               and cross5_rule

    #
    if rule1:
        log_info("rule1: %s", _stock_id)
    elif rule2:
        log_info("rule2: %s", _stock_id)
    elif rule3:
        log_info("rule3: %s", _stock_id)
    elif rule4:
        log_info("rule4: %s", _stock_id)
    elif rule5:
        log_info("rule5: %s", _stock_id)
    else:
        log_info("sorry: not match")
        return 1

    log_info("nice+++ %s, %s", _stock_id, max_date_time)

    content += "+合计量比: %.2f\n"  % (vol_rate)
    content += "+当前量比: %.2f\n"  % (vol_rate2)
    content += "+涨幅、柱体: %.2f%%, %.2f%%\n"  % (rate, zt)

    content += get_basic_info_all(_stock_id, _db)

    subject = "30min: %s @%s" % (_stock_id, _till)
    log_info("mail: %s, \n%s", subject, content)
    saimail(subject,  content)

    log_info("it costs %d us", get_micro_second() - begin)

    return 0


def xxx(_db):


    if sai_is_product_mode():
        till = get_date_by(-1) + " 15:00:00"
    else:

        # 002458, n3=100
        till = "2017-06-09 15:00:00"

        # 000025, n3=75
        till = "2017-06-08 15:00:00"

        # till = "2017-06-16 15:00:00"

        # 002302
        till = "2017-06-14 15:00:00"

        # 002591
        till = "2017-06-15 15:00:00"

    log_info("till: %s", till)

    list_df = get_v3_list(till, _db)
    if list_df is None:
        log_error("error: get_v3_list failure")
        return -1
    else:
        log_debug("list df: \n%s", list_df)

    for row_index, row in list_df.iterrows():

        stock_id = row_index

        # stock_id = "002458"

        log_debug("[%s]------------------", stock_id)

        work_one(stock_id, till, _db)

        # break

    return 0




def work():
    db = db_init()

    xxx(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("v3.log")

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


# v3.py
