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
#######################################################################


def get_p1_list(_db):
    sql = "select distinct stock_id from tbl_day where pub_date = (select max(pub_date) from tbl_day)"

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        df.set_index("stock_id", inplace=True)
        return df


"""
最近_n天的数据
"""
def get_p1_detail(_stock_id, _max_date, _n, _db):
    sql = "select pub_date, close_price, open_price, low_price, high_price, last_close_price, deal_total_count \
from tbl_day \
where stock_id='%s' \
and pub_date <= '%s' \
order by pub_date desc \
limit %d" % (_stock_id, _max_date, _n)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        # df.set_index("pub_date", inplace=True)
        # log_debug("min df: \n%s", df)
        return df




def work_one(_stock_id, _max_date, _db):

    log_info("work_one [%s, %s] begin", _stock_id, _max_date)

    begin = get_micro_second()

    log_debug("it costs %d us", get_micro_second() - begin)

    return item


def xxx(_db):

    if sai_is_product_mode():
        max_date = get_today()
    else:
        max_date = "2016-09-28"
        max_date = "2016-12-17"

    list_df = get_p1_list(_db)
    if list_df is None:
        log_error("error: get_p1_list failure")
        return -1
    else:
        log_debug("list df: \n%s", list_df)

    content = ""
    for row_index, row in list_df.iterrows():
        stock_id = row_index
        # stock_id = "000757"
        log_debug("[%s]------------------", stock_id)
        one = work_one(stock_id, max_date, _db)
        if one is not None:
            content += one

    """
    if len(content) > 0:
        subject = "fupai: %s" % (max_date)
        log_debug("mail: %s", subject)
        log_debug("\n%s", content)
        if sai_is_product_mode():
            saimail(subject, content)
        else:
            pass
            # saimail(subject, content)
    """

    return 0


def work():
    db = db_init()

    xxx(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("d1.log")

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


# d1.py
