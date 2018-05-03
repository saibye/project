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
# 策略：量比变化比较大
#       第三日 量比5+
#       第二日 量比1/5-
#       第二日 跌停（非一字跌停更优先）
#######################################################################


def get_v2_list(_db):
    sql = "select distinct stock_id from tbl_day order by 1"

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        df.set_index("stock_id", inplace=True)
        return df


"""
N天前的成交日数据
"""
def get_v2_detail(_stock_id, _pub_date, _n1, _db):
    sql = "select pub_date, stock_id, \
open_price, high_price, close_price, low_price, \
last_close_price, deal_total_count, \
round((close_price - last_close_price)/last_close_price*100, 2) rt, \
round((high_price - low_price)/last_close_price*100, 2) am \
from tbl_day \
where stock_id = '%s' \
and pub_date <= '%s' \
order by pub_date desc limit %d" % (_stock_id, _pub_date, _n1)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        # df.set_index("pub_date", inplace=True)
        # log_debug("detail df: \n%s", df)
        return df


def work_one(_stock_id, _max_date, _db):

    begin = get_micro_second()

    # 最近n天的数据
    n1 = 100
    n1 = 30
    n1 = 3

    #
    detail_df = get_v2_detail(_stock_id, _max_date, n1, _db);
    if detail_df is None:
        log_info("[%s, %s] detail is none", _stock_id, _max_date)
        return -1
    elif detail_df.empty:
        log_debug("detail_df is empty: [%d]", len(detail_df))
        return 1
    else:
        # log_debug("detail len[%d]\n%s", len(detail_df), detail_df)
        # log_debug("detail len[%d]", len(detail_df))
        pass

    rt1 = 0    # 当日涨幅
    rt2 = 0    # 第二日涨幅
    rt3 = 0    # 第三日涨幅

    am1 = 0    # 当日振幅
    am2 = 0    # 第二日振幅
    am3 = 0    # 第三日振幅

    vr2 = 0    # 第二日量比
    vr3 = 0    # 第三日量比

    r1 = None  # 当日
    r2 = None  # 第二日
    r3 = None  # 第三日

    one = ""

    for row_index, row in detail_df.iterrows():
        r3 = r2
        r2 = r1
        r1 = row
        if r3 is not None:
            if r1['deal_total_count'] <= 0 or r2['deal_total_count'] <= 0: 
                continue

            # log_debug("--[%s, %s, %s]--", r1['pub_date'], r2['pub_date'], r3['pub_date'])
            vr2 = r2['deal_total_count'] / r1['deal_total_count']
            vr3 = r3['deal_total_count'] / r2['deal_total_count']

            # 涨幅
            rt1 = r1['rt']
            rt2 = r2['rt']
            rt3 = r3['rt']

            # 振幅
            am1 = r1['am']
            am2 = r2['am']
            am3 = r3['am']

            # if vr3 >= 6 and vr2 < 0.15 and rt2 < -9.8 and rt1 > 5 and rt3 > 5:
            if vr3 >= 5 and vr2 <= 0.2 and rt2 < -9.8  and r3['close_price'] > r3['open_price']:
                log_info("-- rt: [%s, %s, %s] --", rt1, rt2, rt3)
                log_info("-- am: [%s, %s, %s] --", am1, am2, am3)
                log_info("-- vr: [%.3f, %.3f] --", vr2, vr3)
                log_info("---- good: [%s, %s]----", _stock_id, r3['pub_date'])
                one  = "%s, %s, 涨幅:%.2f, 振幅: %.2f\n" % (_stock_id, r3['pub_date'], rt3, am3)
                one += "量比: 第二日:%.2f, 第三日:%.2f\n" % (vr2, vr3)
                one += get_basic_info_all(_stock_id, _db)
                one += "++++++++++++++++++++++++++++++++++++++++\n"
        else:
            # log_debug("数据不足")
            pass

    log_debug("it costs %d us", get_micro_second() - begin)

    return one


def xxx(_db):

    counter  = 0
    max_date = "2017-02-11"
    max_date = get_date_by(0)
    log_info("date: [%s]", max_date)

    list_df = get_v2_list(_db)
    if list_df is None:
        log_error("error: get_v2_list failure")
        return -1
    else:
        log_debug("list df: \n%s", list_df)

    subject  = "### 超级量比: %s" % (max_date)
    content  = "第二日非一字跌停优先！\n"
    content += "第三日收阳柱优先\n"
    content += "小心复牌补跌\n\n"

    for row_index, row in list_df.iterrows():
        stock_id = row_index
        log_debug("---- [%s] begin -----", stock_id)
        item = work_one(stock_id, max_date, _db)
        if len(item) > 0:
            counter += 1
            content += item

    if counter > 1:
        log_debug("mail: %s", subject)
        log_debug("\n%s", content)
        if sai_is_product_mode():
            saimail(subject, content)
        else:
            saimail(subject, content)
            pass
    else:
        log_debug("no data: %s", subject)

    return 0




def work():
    db = db_init()

    xxx(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("v2.log")

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


# v2.py
