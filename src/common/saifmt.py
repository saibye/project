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
from sairef  import *
import saiobj

#######################################################################




def sai_fmt_calc_tech(_df):

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

    # sma50
    se = calc_sma(sc, 50)
    _df['ma50'] = se;

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


def sai_fmt_ref_init(_mode, _detail_df):

    if _mode == 0:
        log_info('nothing to do')
        return 0

    # _detail MUST be sorted
    rv = ref_init4(_detail_df)
    if rv < 0:
        log_error("error: ref_init4")
        return -1

    if _mode == 1:
        log_info('basic ref(x) already done')
        return 0

    _detail_df.sort_index(ascending=False, inplace=True)
    sai_fmt_calc_tech(_detail_df)
    _detail_df.sort_index(ascending=True,  inplace=True)

    ref_set_tech5()


    return 0



def sai_fmt_get_detail(_stock_id, _pub_date, _n, _db):
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


# _mode: 0. 原始数据, 1.ref_close等, 2.ref_ma200等
def sai_fmt_set(_stock_id, _till_date, _mode, _n, _db):

    # log_debug("=====[%s, %s]=====", _stock_id, _till_date)

    # step1
    # 获取明细数据
    # 之前_n单位的交易数据
    detail_df = sai_fmt_get_detail(_stock_id, _till_date, _n, _db);
    if detail_df is None:
        log_info("[%s, %s] detail is none", _stock_id, _a_date)
        return None
    elif detail_df.empty:
        log_debug("detail_df is empty: [%d]", len(detail_df))
        return None
    else:
        # log_debug("len[%d]", len(detail_df))
        pass

    length = len(detail_df)
    if length < 10:
        log_info("data-not-enough: %s: %d", _stock_id, length)
        return None

    # step2
    # 格式化数据
    rv = sai_fmt_ref_init(_mode, detail_df)
    if rv < 0:
        log_error("error: sai_fmt_ref_init")
        return None

    # log_debug("=====[%s, formated]=====", _stock_id)

    return detail_df


def sai_fmt_simple(_stock_id, _till_date, _db):

    n   = saiobj.g_fetched_len
    # log_debug("%d", n)
    mode= saiobj.g_fmt_mode
    saiobj.g_subject_prefix = ''
    return sai_fmt_set(_stock_id, _till_date, mode, n, _db)

def sai_fmt_set_fetch_len(_n):
    saiobj.g_fetched_len = _n 



#######################################################################
if __name__=="__main__":
    sailog_set("saifmt.log")

    log_info("main begin here!")

    sai_fmt_set_fetch_len(30)

    db = db_init()


    stock_id  = '000002'
    till_date = '2018-04-22'
    df = sai_fmt_simple(stock_id, till_date, db)
    log_debug('%s', df)
    log_debug('ref_close(0) -- %s', ref_close(0))
    log_debug('ref_close(1) -- %s', ref_close(1))
    log_debug('ref_ma10(0) -- %s', ref_ma10(0))
    log_debug('ref_ma10(1) -- %s', ref_ma10(1))

    db_end(db)
    log_info("main ends  bye!")

#######################################################################

# saifmt.py
