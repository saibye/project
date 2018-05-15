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
from saitick import *


#######################################################################
# sao: 扫货
# 跌停板，密集成交
# 300155 @2017-06-01
#######################################################################


def sao_analyze_one(_stock_id, _trade_date, _db):
    one = ""
    rv  = 0
    name = get_name(_stock_id)

    log_info("%s %s @ %s", _stock_id, name, _trade_date)

    time_rate, sum_rate, sao_rate = sai_tick_bottom(_stock_id, _trade_date)
    if time_rate == -1:
        log_error("warn: stock %s, %s is None, next", _stock_id, _trade_date)
        return ""

    log_debug("time时间片占比: %.2f / 8 (%.3f)", time_rate * 8, time_rate)
    log_debug("sum 成交额占比: %.3f", 100 * sum_rate)
    log_debug("扫货力度:   %.3f", sao_rate)

    # 300155 @2017-06-01 deleted
    # 300216 @2018-05-03 
    rule1 = time_rate < 0.10 and sum_rate > 0.24 and sao_rate > 2.54
 
    # 300585 @2017-06-12
    rule2 = False and time_rate < 0.18 and sum_rate > 0.06 and sao_rate > 0.37

    rule_info = ""
    if rule1:
        log_info("nice: rule1: %s @ %s 扫货", _stock_id, _trade_date)
        rv = 1
        rule_info = "rule1\n"
    elif rule2:
        log_info("nice: rule2: %s @ %s 扫货", _stock_id, _trade_date)
        rv = 1
        rule_info = "rule2\n"

    if rv == 1:
        one = "%s - %s - %s 跌停\n" % (_stock_id, name, _trade_date)
        one += "%s" % (rule_info)
        one += "-时间片: %.2f / 8 (%.2f)\n" % (time_rate*8, time_rate)
        one += "+成交额: %.2f%%\n" % (100 * sum_rate)
        one += "+力度  : %.2f\n" % sao_rate
        one += get_basic_info_all(_stock_id, _db)
        one += "++++++++++++++++++++++++++++++++\n"
        log_info("%s\n", one)

    return one


def sao_get_check_list(_date, _db):

    sql = "select * from tbl_day where pub_date='%s' \
and (low_price - last_close_price) / last_close_price * 100 < -9.9 " % (_date)

    log_info("sql: %s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        log_info("got data: %d lines", len(df))

    return df


def xxx(_db):

    trade_date = "2017-04-24" # 002307
    trade_date = "2017-06-01" # 300155
    trade_date = "2017-06-12" # 300585
    trade_date = "2017-06-01" # 300155
    trade_date = "2017-06-13" # 600892
    trade_date = "2018-05-03" # 300216
    trade_date = get_today()
    trade_date = get_date_by(-1)
    trade_date = get_newest_trade_date(_db)

    basic = sao_get_check_list(trade_date, _db)
    if basic is None:
        log_debug("error: sao_get_check_list failure")
        return -1

    content = ""
    for row_index, row in basic.iterrows():
        stock_id = row['stock_id']
        trade_date = row['pub_date']

        # log_debug("%s", row)

        # stock_id = "300155"
        # stock_id = "002307"
        one = sao_analyze_one(stock_id, trade_date, _db)
        content += one
        log_debug("-----------------------------------------")

    if len(content) > 0:
        log_info("mail: \n%s", content)
        subject = "new跌停: %s" % (trade_date)
        if sai_is_product_mode():
            saimail_dev(subject, content)

    return 0


def work():
    db = db_init()

    xxx(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("sao.log")

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


# sao.py
