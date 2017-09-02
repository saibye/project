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
# 策略：macd dead or ma dead
#######################################################################


def get_index_list(_till, _db):
    sql = "select distinct stock_id from tbl_index_day \
where pub_date = \
(select max(pub_date) from tbl_index_day \
where pub_date <= '%s')" % (_till)

    log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        df.set_index("stock_id", inplace=True)
        return df


def get_index_detail(_stock_id, _pub_date, _n3, _db):
    sql = "select stock_id, pub_date, open_price, close_price, \
deal_total_count total, last_close_price last, \
high_price, low_price \
from tbl_index_day a where a.stock_id  = '%s' and   a.pub_date <= '%s' \
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


def index_dynamic_calc_tech(_df):

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


def index_format_ref(_stock_id, _detail_df):

    # _detail MUST be sorted
    rv = ref_init4(_detail_df)
    if rv < 0:
        log_error("error: ref_init4")
        return -1

    _detail_df.sort_index(ascending=False, inplace=True)
    index_dynamic_calc_tech(_detail_df)
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


def work_one_stock(_stock_id, _till,  _db):

    to_mail = False

    content = ""

    if _stock_id == "000001":
        content += "上证指数#%s" % (_till)
    elif _stock_id == "399006":
        content += "创业板#%s" % (_till)
    else:
        pass

    subject = "CAUTION: %s" % (content)

    content += "\n(注意MACD柱线的背离！)\n\n"

    begin = get_micro_second()

    n3 = 200

    # 获取明细数据
    # 之前n4单位的交易数据
    detail_df = get_index_detail(_stock_id, _till, n3, _db);
    if detail_df is None:
        log_info("[%s, %s] detail is none", _stock_id, n1_max_date_time)
        return -1
    elif detail_df.empty:
        log_debug("detail_df is empty: [%d]", len(detail_df))
        return 1
    else:
        log_debug("n3: len[%d]", len(detail_df))


    # 格式化数据
    rv = index_format_ref(_stock_id, detail_df)
    if rv < 0:
        log_error("error: index_format_ref: %s", _stock_id)
        return -1

    log_debug("ref0: [%.3f, %.3f, %.3f, %.3f]", ref_open(0), ref_close(0), ref_low(0), ref_high(0))
    log_debug("ref1: [%.3f, %.3f, %.3f, %.3f]", ref_open(1), ref_close(1), ref_low(1), ref_high(1))
    log_debug("ref2: [%.3f, %.3f, %.3f, %.3f]", ref_open(2), ref_close(2), ref_low(2), ref_high(2))

    log_debug("macd0:[%.3f = %.3f - %.3f]", ref_macd(0), ref_diff(0), ref_dea(0))
    log_debug("macd1:[%.3f = %.3f - %.3f]", ref_macd(1), ref_diff(1), ref_dea(1))
    log_debug("macd2:[%.3f = %.3f - %.3f]", ref_macd(2), ref_diff(2), ref_dea(0))

    # 均线发散
    log_debug("tech0: ma5[%.3f], ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma5(0), ref_ma10(0), ref_ma20(0), ref_ma30(0), ref_ma60(0))
    log_debug("tech1: ma5[%.3f], ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma5(1), ref_ma10(1), ref_ma20(1), ref_ma30(1), ref_ma60(1))
    log_debug("tech2: ma5[%.3f], ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma5(2), ref_ma10(2), ref_ma20(2), ref_ma30(2), ref_ma60(2))
    log_debug("tech3: ma5[%.3f], ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma5(3), ref_ma10(3), ref_ma20(3), ref_ma30(3), ref_ma60(3))
    log_debug("tech4: ma5[%.3f], ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma5(4), ref_ma10(4), ref_ma20(4), ref_ma30(4), ref_ma60(4))
    log_debug("tech5: ma5[%.3f], ma10[%.3f], ma20[%.3f], ma30[%.3f], ma60: [%.3f]", ref_ma5(5), ref_ma10(5), ref_ma20(5), ref_ma30(5), ref_ma60(5))

    macd = ref_macd(0)
    diff = ref_diff(0)
    dea  = ref_dea(0)
    log_info("macd: %.3f = %.3f - %.3f", macd, diff, dea)


    cp   = ref_close(0)
    ma5  = ref_ma5(0)
    ma10 = ref_ma10(0)
    ma20 = ref_ma20(0)

    if macd < 0 and ma5 < ma10:
        to_mail = True
        content += "双死叉，建议清仓！！！\n\n"

    if macd < 0:
        to_mail = True
        content += "MACD死叉！\n==> macd[%.2f], diff[%.2f], dea[%.2f]\n\n" % (macd, diff, dea)

    if ma5 < ma10:
        to_mail = True
        content += "均线死叉！(%.2f)\n==> ma5[%.2f] < ma10[%.2f]\n\n" % (ma5-ma10, ma5, ma10)

    if cp < ma10:
        content += "收盘低于ma10！(%.2f)\n==> close[%.2f] < ma10[%.2f]\n\n" % (cp-ma10, cp, ma10)

    if cp < ma20:
        to_mail = True
        content += "收盘低于ma20！(%.2f)\n==> close[%.2f] < ma20[%.2f]\n\n" % (cp-ma20, cp, ma20)

    content += "@不建议逆势而为@"

    if to_mail:
        log_info("mail: \n%s\n%s", subject, content)
        saimail_dev(subject,  content)
    else:
        log_info("no need to send MaiL")
        log_info("content:\n%s", content)

    log_info("it costs %d us", get_micro_second() - begin)

    return 0



def regression_one(_db):

    till = get_date_by(0)

    # 
    till = "2017-08-10"
    stock_id = "000001"

    log_debug("[%s]------------------", stock_id)

    work_one_stock(stock_id, till, _db)

    return 0

def regression(_db):

    max_date = "2017-08-11"

    log_info("regress-all")

    work_one(max_date, _db)


def work_one(_date, _db):
    index_list = ['000001', '399006']

    stock_id = ""
    for stock_id in index_list:

        log_debug("====[%s][%s]====", _date, stock_id)

        work_one_stock(stock_id, _date, _db)


def xxx(_db):

    if sai_is_product_mode():
        till = get_date_by(0)
        till = "2017-08-10"
        till = get_newest_index_trade_date(_db)
    else:
        regression_one(_db)
        return

    log_info("till: %s", till)

    work_one(till, _db)

    return 0




def work():
    db = db_init()

    xxx(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("report_index.log")

    log_info("let's begin here!")

    if sai_is_product_mode():
        # check holiday
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
exit()

#######################################################################


# index.py
