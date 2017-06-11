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
# 策略：低开高走长上影
#  002584 -- 2017-3-3
#  低开7.62
#  最高4.68
#  阳线
#  放量15+
#  前一日跌停
#  WARN: 之后连续两天阳线很重要，并且收盘价要高于第一日收盘价
#######################################################################

"""
1. 开盘 < -7
2. 收盘 > 4
3. 前一天跌停，缩量
4. 量比15+
"""
def get_p3_list(_date, _db):
    recent = 10 # test
    recent = 1
    sql = "select stock_id, pub_date, \
round((close_price-last_close_price)/last_close_price*100,2) rate, \
round((high_price - low_price)/last_close_price*100,2) amp, \
round((open_price - low_price)/last_close_price*100,2) dis, \
open_price open, close_price close, low_price low, high_price high, \
last_close_price last, deal_total_count vol \
from tbl_day \
where pub_date in (select * from (select distinct pub_date from tbl_day where pub_date <= '%s' order by pub_date desc limit %d) x) \
and (high_price - last_close_price) / last_close_price * 100 >= 4 \
and (low_price  - last_close_price) / last_close_price * 100 <= -7 \
and (open_price - low_price) / last_close_price * 100 < 0.5 \
order by pub_date desc" % (_date, recent)

    log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        df.set_index("stock_id", inplace=True)
        return df


def xxx(_db):

    if sai_is_product_mode():
        trade_date = get_today()
    else:
        trade_date = "2016-12-13"
        trade_date = "2017-05-19"

    list_df = get_p3_list(trade_date, _db)
    if list_df is None:
        log_error("error: get_p3_list failure")
        return -1
    else:
        log_debug("list df: \n%s", list_df)

    content  = ""
    content += "非常重要:\n"
    content += "1. 之后两天需要收阳线，且收盘价高于第一天收盘价\n"
    content += "2. 前一日最好跌停，若是无量更好\n"
    content += "\n"

    for row_index, row in list_df.iterrows():
        stock_id = row_index
        # 今日量比 >= 4
        log_debug("[%s]------------------", stock_id)
        one = ""
        rt = tech_get_vol_rate(stock_id, row['pub_date'], _db)
        log_debug("量比: %.2f", rt)
        one = one + "%s, %s, 涨幅:%s,\n振幅:%s, 量比:%.2f\n" % (stock_id, row['pub_date'], row['rate'], row['amp'], rt)
        all_info = get_basic_info_all(stock_id, _db)
        one = one + all_info
        one = one + "++++++++++++++++++++++++++++++++++++++++\n"
        content = content + one
        log_debug("%s", one)

    subject = "超级振幅3: %s" % (trade_date)
    if len(list_df) > 0:
        log_debug("mail: %s", subject)
        log_debug("\n%s", content)
        if sai_is_product_mode():
            saimail(subject, content)
        else:
            pass
            # saimail(subject, content)
    else:
        log_debug("no data: %s", subject)

    return 0


def work():
    db = db_init()

    xxx(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("p3.log")

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


# p3.py
