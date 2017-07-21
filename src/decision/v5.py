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


def v5_analyzer1(_stock_id, _min_date, _min_vol, _detail_df, _db):

    zt1   = 0.0
    vr1   = 0.0
    rate1 = 0.0

    zt2   = 0.0
    vr2   = 0.0
    rate2 = 0.0

    warn  = ""

    length = len(_detail_df)

    if length == 1:
        log_error("fatal: invalid length")
        return -1

    # 当日
    vol0   = _detail_df['deal_total_count'][0]
    date0  = _detail_df['pub_date'][0]
    open0  = _detail_df['open_price'][0]
    close0 = _detail_df['close_price'][0]
    last0  = _detail_df['last_close_price'][0]
    log_debug("volume0: [%.3f]", vol0)

    # 无量跌停，不考虑
    rate0  = (close0 - last0) / last0 * 100
    if rate0 > 9.9:
        log_info("sorry: [%s] 无量涨停", _stock_id)
        return -1

    # 无量跌停，不考虑
    if rate0 < -9.8:
        log_info("sorry: [%s] 无量跌停", _stock_id)
        return -1

    if length >= 2:
        vol1   = _detail_df['deal_total_count'][1]
        date1  = _detail_df['pub_date'][1]
        open1  = _detail_df['open_price'][1]
        close1 = _detail_df['close_price'][1]
        rate1  = (close1 - close0) / close0 * 100
        zt1    = (close1 - open1)  / close0 * 100
        vr1    = vol1 / vol0
        one    = "[%s]涨幅1: [%.2f], 量比1: [%.2f]" % (date1, rate1, vr1)
        log_debug("one: %s", one)

    if length >= 3:
        vol2   = _detail_df['deal_total_count'][2]
        date2  = _detail_df['pub_date'][2]
        open2  = _detail_df['open_price'][2]
        close2 = _detail_df['close_price'][2]
        rate2  = (close2 - close1) / close1 * 100
        zt2    = (close2 - open2)  / close1 * 100
        vr2    = vol2 / vol0
        two    = "[%s]涨幅2: [%.2f], 量比2: [%.2f]" % (date2, rate2, vr2)
        log_debug("two: %s", two)

    # 次日跌停不考虑 2016/12/11 for 300353
    if rate1 < -9.8 or rate2 < -9.8:
        log_info("sorry: 地量后，有跌停")
        return -1

    # 要求连续上涨 2017/5/29
    if rate1 < 0 or rate2 < 0:
        log_info("sorry: 之后两日不能下跌: %.2f, %.2f", rate1, rate2)
        return -1

    # 要求连续阳柱 2017/5/29
    if zt1 < 0 or zt2 < 0:
        log_info("sorry: 之后两日不能阴柱: %.2f, %.2f", zt1, zt2)
        return -1


    # 检查量比
    if ((rate1 > 0 or zt1 > 0) and vr1 >= 10) or ((rate2 > 0 or zt2 > 0) and vr2 >= 10):
        log_info("nice, a chance: [%s], since: [%s]", _stock_id, min_date)

        warn += "+++务必：穿越3线，收复MA20,60\n"
        warn += "+++最好：地量横盘2-3天\n"
        warn += "+++加分：双底+多个锤子线+多个上影线\n"
        log_info("%s", warn)

        if vr2 > vr1:
            warn += "++++增量放量\n"
            log_info("%.2f > %.2f", vr2, vr1)
            log_info("%s", warn)

        if rate2 > rate1:
            warn += "+++++增量涨幅\n"
            log_info("%.2f > %.2f", rate2, rate1)
            log_info("%s", warn)

        item  = "%s 地量: [%.3f]@[%s]" % (_stock_id, vol0, min_date)

        info  = get_basic_info_all(_stock_id, _db)
        item += "\n%s\n%s\n%s\n%s" % (warn, one, two, info)

        if vr1 >= 50 or vr2 >= 50:
            subject  = "###diliang: %s" % (min_date)
        elif vr1 >= 30 or vr2 >= 30:
            subject  = "##diliang: %s" % (min_date)
        elif vr1 >= 20 or vr2 >= 20:
            subject  = "#diliang: %s" % (min_date)
        else:
            subject  = "diliang: %s" % (min_date)

        # content += item
        log_info("subject: \n%s", subject)
        log_info("content: \n%s", item)
        saimail_dev(subject, item)
        sai_save_good(_stock_id, date0, "diliang", min_vol, vr1, vr2, min_date, _db)
    else :
        log_info("sorry... [%s]", _stock_id)

    return 0


def get_v5_detail_full(_stock_id, _pub_date, _n, _db):
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

def get_v5_list(_till, _db):
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

# 最近3天最小成交量
def get_v5_n1_min(_stock_id, _till, _n1, _db):
    sql = "select pub_date, deal_total_count, close_price, stock_id from  \
( select pub_date, deal_total_count, close_price, open_price, stock_id from tbl_day where \
 stock_id = '%s' \
 and pub_date <= '%s' \
 order by pub_date desc  \
 limit %d ) t1 \
order by deal_total_count limit 1" % (_stock_id, _till, _n1)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        return df


# 最近60天最小成交量
def get_v5_n2_min(_stock_id, _till2, _n2, _db):
    sql = "select pub_date, deal_total_count from  \
( select pub_date, deal_total_count from tbl_day where \
 stock_id = '%s' \
 and pub_date <= '%s' \
 order by pub_date desc  \
 limit %d ) t1 \
order by deal_total_count limit 1" % (_stock_id, _till2, _n2)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        return df

"""
最小vol后的成交日数据
"""
def get_v5_detail1(_stock_id, _pub_date, _n3, _db):
    sql = "select stock_id, pub_date, open_price, close_price, \
deal_total_count total, last_close_price last, \
high_price, low_price \
from tbl_day a where a.stock_id  = '%s' and   a.pub_date >= '%s' \
order by pub_date limit %d" % (_stock_id, _pub_date, _n3)

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
最小vol前的成交日数据
"""
def get_v5_detail2(_stock_id, _pub_date, _n3, _db):
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


def v5_dynamic_calc_tech(_df):

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


#########################
# 算法检查
#########################


def work_one(_stock_id, _till,  _db):

    good = 0
    zt   = 0
    content = ""

    begin = get_micro_second()

    # 最近n1天的最小vol，是最近n2天的最小vol
    # n3: 最近n3价格最高
    # n4: 最近n4天的数据
    # n5: 最近n5天的红绿成交量加总
    if sai_is_product_mode():
        n1 = 3
        n2 = 30
        n3 = 200
        n4 = 300
        n5 = 30
    else:
        n1 = 3
        n2 = 30
        n3 = 200
        n4 = 300
        n5 = 30

    min_date = ""
    min_volume = ""


    # 2017-6-21
    n1_df = get_v5_n1_min(_stock_id, _till, n1, _db)
    if n1_df is None:
        log_info("n1(%d) not match!", n1)
        return -1
    elif n1_df.empty:
        log_debug("n1_df is empty: [%d]", len(n1_df))
        return 1
    else:
        n1_min_date = n1_df.iloc[0, 0]
        n1_min_volume    = n1_df.iloc[0, 1]
        n1_min_close     = n1_df.iloc[0, 2]
        log_debug("n1_date [%s]", n1_min_date);
        log_debug("n1_vol  [%s]", n1_min_volume);
        log_debug("n1_close[%.3f]", n1_min_close);
        n1_df = n1_df.set_index("stock_id")
        n1_df["1"] = "1"

    # 2017-6-21
    n2_df = get_v5_n2_min(_stock_id, n1_min_date, n2, _db)
    if n2_df is None:
        log_info("n2(%d) not match!", n2)
        return -1
    elif n2_df.empty:
        log_debug("n2_df is empty: [%d]", len(n2_df))
        return 1
    else:
        n2_min_date = n2_df.iloc[0, 0]
        n2_min_volume    = n2_df.iloc[0, 1]
        log_debug("n2_date[%s], n2_vol[%.2f]", n2_min_date, n2_min_volume);

    # check min-vol(n1) == min-vol(n2)
    if n2_min_date != n1_min_date:
        log_info("time: [%s] != [%s]", n1_min_date, n2_min_date)
        return 1
    else:
        log_info("match the same time: [%s]", n1_min_date)

    if n2_min_volume != n1_min_volume:
        log_info("not the same volume: [%s] != [%s]", n1_min_volume, n2_min_volume)
        return 1
    else:
        log_info("match the same volume: [%s]", n1_min_volume)

    # 获取明细数据1
    # 地量之后n3单位的交易数据
    after_df = get_v5_detail1(_stock_id, n1_min_date, n3, _db);
    if after_df is None:
        log_info("[%s, %s] detail is none", _stock_id, n1_min_date)
        return -1
    elif after_df.empty:
        log_debug("after_df is empty: [%d]", len(after_df))
        return 1
    else:
        log_debug("n4: len[%d]", len(after_df))

    # TODO
    # 检查量比

    # 获取明细数据2
    # 地量之前n4单位的交易数据
    before_df = get_v5_detail2(_stock_id, n1_min_date, n4, _db);
    if before_df is None:
        log_info("[%s, %s] detail is none", _stock_id, n1_min_date)
        return -1
    elif before_df.empty:
        log_debug("before_df is empty: [%d]", len(before_df))
        return 1
    else:
        log_debug("n4: len[%d]", len(before_df))

    # TODO
    # 检查收盘价相近

    min_date   = n1_min_date
    min_volume = n1_min_volume
    log_debug("%s: min_date:   [%s]", _stock_id, min_date)
    log_debug("%s: min_volume: [%s]", _stock_id, min_volume)

    content += "%s @ %s\n" % (_stock_id, min_date)

    log_debug("min-close: [%.3f]", n1_min_close)


    # 格式化数据
    rv = v5_format_ref(_stock_id, before_df)
    if rv < 0:
        log_error("error: v5_format_ref: %s", _stock_id)
        return -1


    log_info("nice+++ %s, %s", _stock_id, min_date)

    content += "涨幅: %.2f%%\n" % (get_chg_rate(_stock_id))

    content += "+合计量比: %.2f\n"  % (vol_rate)
    content += "+当前量比: %.2f\n"  % (vol_rate2)
    content += "+收盘价突破: %d(unit)\n"    % (days1)
    content += "+成交量突破: %d(unit)\n"  % (days2)
    content += "+涨幅、柱体: %.2f%%, %.2f%%\n"  % (rate, zt)

    content += get_basic_info_all(_stock_id, _db)

    subject = "+++day: %s @%s" % (_stock_id, min_date)
    log_info("mail: \n%s\n%s", subject, content)
    # saimail(subject,  content)

    log_info("it costs %d us", get_micro_second() - begin)

    return 0



def regression(_db):

    till = get_date_by(-1)

    # 002822
    till = "2017-04-26"
    stock_id = "002822"

    # 002423
    till = "2017-06-15"
    stock_id = "002423"

    log_debug("[%s]------------------", stock_id)

    work_one(stock_id, till, _db)

    return 0


def xxx(_db):


    if sai_is_product_mode():
        till = get_date_by(-1)
        till = get_newest_trade_date(_db)
    else:
        regression(_db)

        return
        

    log_info("till: %s", till)

    list_df = get_v5_list(till, _db)
    if list_df is None:
        log_error("error: get_v5_list failure")
        return -1
    else:
        log_debug("list df: \n%s", list_df)

    for row_index, row in list_df.iterrows():

        stock_id = row_index

        log_debug("[%s]------------------", stock_id)

        work_one(stock_id, till, _db)

    return 0




def work():
    db = db_init()

    xxx(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("v5.log")

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


# v5.py
