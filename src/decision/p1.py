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
# 策略：从跌停到涨停
#   振幅超过17，开盘跌停
#
#######################################################################

"""
1. 超长振幅: _max_amp
2. 开盘跌停
3. 最近N天
"""
def get_p1_list(_date, _max_amp, _db):
    recent = 30 # test
    recent = 1
    sql = "select stock_id, pub_date, \
round((close_price-open_price)/last_close_price*100,2) rate, \
round((high_price - low_price)/last_close_price*100,2) amp, \
round((open_price - low_price)/last_close_price*100,2) dis, \
round((close_price-last_close_price)/last_close_price*100,2) rate2, \
open_price open, close_price close, low_price low, high_price high, \
last_close_price last \
from tbl_day \
where pub_date in (select * from (select distinct pub_date from tbl_day where pub_date <= '%s' order by pub_date desc limit %d) x) \
and (high_price - low_price) / last_close_price * 100 >= %d \
and (open_price - low_price) / last_close_price * 100 < 0.5 \
order by pub_date"  % (_date, recent, _max_amp)

    log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        df.set_index("stock_id", inplace=True)
        return df


def xxx(_db):
    max_amp = 17

    if sai_is_product_mode():
        trade_date = get_today()
    else:
        trade_date = "2016-12-13"

    list_df = get_p1_list(trade_date, max_amp, _db)
    if list_df is None:
        log_error("error: get_p1_list failure")
        return -1
    else:
        log_debug("list df: \n%s", list_df)

    content  = "跌停开盘，但分时线上，不一定（甚至最好不）在跌停盘停留\n"
    content += "注意：\n1、小心复牌补跌\n2、新股破板不考虑\n"
    content += "优先：\n1、不在跌停板停留\n2、下降趋势\n3、前一日跌停，缩量\n"
    content += "\n"

    for row_index, row in list_df.iterrows():
        stock_id = row_index
        log_debug("[%s]------------------", stock_id)
        one = "%s, %s, 振幅:%s, 升幅:%s, 涨幅:%s\n" % (stock_id, row['pub_date'], row['amp'], row['rate'], row['rate2'])
        all_info = get_basic_info_all(stock_id, _db)
        one = one + all_info
        one = one + "++++++++++++++++++++++++++++++++++++++++\n"
        content = content + one
        log_debug("%s", one)

    subject = "###超级振幅: %s" % (trade_date)
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
    sailog_set("p1.log")

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


# p1.py
