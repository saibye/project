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
# 策略：复牌，跌停
#######################################################################


def get_d1_list(_db):
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
def get_d1_detail(_stock_id, _max_date, _n, _db):
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

"""
检查今天的成交量是最近n1日的最小成交量
"""
def check_d1_min(_stock_id, _pub_date, _n1, _db):
    sql = "select stock_id, pub_date, deal_total_count from tbl_day a \
where stock_id = '%s' \
and   pub_date = '%s' \
and \
    (select min(deal_total_count) from tbl_day b  \
     where b.stock_id  = a.stock_id \
     and   b.pub_date <= a.pub_date \
     and   b.pub_date >=  \
     (select min(pub_date) from (select pub_date from tbl_day where stock_id = '%s' and pub_date <= '%s' order by pub_date desc limit %d) t1)) \
    = \
    (select min(deal_total_count) from tbl_day c \
     where c.stock_id  = a.stock_id \
     and   c.pub_date  = a.pub_date)" % (_stock_id, _pub_date, _stock_id, _pub_date, _n1)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("[%s, %s, %d] check dl is none", _stock_id, _max_date, n1)
        return 0
    elif df.empty:
        log_debug("df is empty: [%d]", len(df))
        return 0
    else:
        pass
        log_debug("nice: d1 min: len[%d]\n%s", len(df), df)
        return 1


"""
2016-12-25
insert into tbl_fupai ( 
stock_id, stock_loc, fupai_date, tingpai_date, days, 
inst_date, inst_time) 
values ('000757', 'cn', '2016-09-27', '2016-03-27', 180, '2016-12-25', '09:41:00'); 
"""
def record_to_db(_stock_id, _fupai_date, _tingpai_date, _days, _db):
    dt = get_today()
    tm = get_time()
    sql = "insert into tbl_fupai (  \
stock_id, stock_loc, fupai_date, tingpai_date, days,  \
inst_date, inst_time)  \
values ('%s', 'cn', '%s', '%s', %d, '%s', '%s')" % (_stock_id, _fupai_date, _tingpai_date, _days, dt, tm)

    log_debug("sql: \n%s", sql)

    rv = sql_to_db_nolog(sql, _db)
    if rv != 0:
        log_error("error: record fupai: %s", sql)

    return rv


def work_one(_stock_id, _max_date, _db):

    log_info("work_one [%s, %s] begin", _stock_id, _max_date)

    begin = get_micro_second()

    # 最近n天的数据
    n1 = 3

    # 停牌天数
    n2 = 120

    # 最近n天最小成交量
    n3 = 60

    # 之前n天的交易数据
    detail_df = get_d1_detail(_stock_id, _max_date, n1, _db);
    if detail_df is None:
        log_info("[%s, %s, %d] detail is none", _stock_id, _max_date, n1)
        return None
    elif detail_df.empty:
        # log_info("detail_df is empty: [%d]", len(detail_df))
        return None
    else:
        pass
        # log_debug("recent: len[%d]\n%s", len(detail_df), detail_df)

    length = len(detail_df)

    diff     = 0
    row_num  = 0
    item     = ""
    rate     = 0.0
    last_rate= 0.0
    last_one = _max_date
    for row_index, row in detail_df.iterrows():
        row_num = row_num + 1
        trade_date = row['pub_date']
        rate       = (row['close_price'] - row['last_close_price']) / row['last_close_price'] * 100
        # log_debug("[%s][%s]------------------", trade_date, type(trade_date))
        this_one = trade_date
        # last_one: "2016-09-27"
        # this_one: "2016-03-27"
        if row_num > 1:
            diff = (last_one - this_one).days
            # log_debug("diff: [%s] - [%s] = [%s]", this_one, last_one, diff)

        if diff > n2:
            log_debug("nice: %s waits a long time: %d", _stock_id, diff)
            item += "%s: %4d 天 (%s, %s]" % (_stock_id, diff, this_one, last_one)
            if check_d1_min(_stock_id, last_one, n3, _db) == 1:
                item += "\n## excited with diliang ##"
                item += "\n## 涨幅 %.2f [跌停优先] ##" % last_rate
            item += "\n%s" % (get_basic_info_all(_stock_id, _db))
            item += "---------------------------------------------------------------\n"
            log_debug("\n%s", item)

        # 2016-12-25
        if diff > 30:
            record_to_db(_stock_id, last_one, this_one, diff, _db)

        last_one = this_one
        last_rate= rate

    # log_debug("it costs %d us", get_micro_second() - begin)

    return item


def xxx(_db):

    if sai_is_product_mode():
        max_date = get_today()
    else:
        max_date = "2016-09-28"
        max_date = "2016-12-17"

    list_df = get_d1_list(_db)
    if list_df is None:
        log_error("error: get_d1_list failure")
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

    if len(content) > 0:
        subject = "fupai: %s" % (max_date)
        log_debug("mail: %s", subject)
        log_debug("\n%s", content)
        if sai_is_product_mode():
            saimail(subject, content)
        else:
            pass
            # saimail(subject, content)


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
