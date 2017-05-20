#!/usr/bin/env python
# -*- encoding: utf8 -*-

import heapq

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
# 策略：横盘突破，涨停为界
#  600698 -- 2017-1-3   rate1: 19.87, rate2: 14.65, cnt: 57
#  000912 -- 2016-9-26  rate1: 20.89, rate2: 16.61, cnt: 41
#
# 涨停突破前高
# 横盘天数够长
# 箱体盘整
# 分时线有人为的痕迹
# --有很多长上影线
# --涨停后成交量放大
#######################################################################

"""
"""
def get_one_list(_stock_id, _trade_date, _db):
    recent = 100
    sql = "select pub_date, open_price, close_price, low_price, high_price, \
last_close_price, deal_total_count vol, \
round((close_price-open_price)/last_close_price*100, 2) rate, \
round((high_price - low_price)/last_close_price*100, 2) amp, \
round((open_price - low_price)/last_close_price*100, 2) dis \
from tbl_day \
where stock_id = '%s' \
and pub_date <= '%s' \
order by pub_date desc limit %d " % (_stock_id, _trade_date, recent)

    # log_debug("sql: \n%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        df.set_index("pub_date", inplace=True)
        return df


def work_one_stock(_stock_id, _max_date, _db):
    rv = 0

    detail_df = get_one_list(_stock_id, _max_date, _db)
    if detail_df is None:
        log_error("error: get_one_list failure")
        return -1
    else:
        # log_debug("list df: \n%s", detail_df)
        pass

    high_list = []
    low_list  = []

    times = 0
    close0 = 0  # 最新涨停价
    last_low = -1
    this_high = -1
    good_to_end = 0
    up_gap = 0
    for row_index, row in detail_df.iterrows():
        trade_date  = row_index
        close_price = row['close_price']
        open_price  = row['open_price']
        low_price   = row['low_price']
        high_price  = row['high_price']
        last_close_price = row['last_close_price']

        rate = (close_price / last_close_price -1) * 100
        # log_debug("[%s] ==> %-3.2f%%", trade_date, rate)

        if good_to_end:
            log_info("Good_to_end: let's end")
            if last_low > high_price:
                log_info("[%s]向上跳空", trade_date)
                up_gap = 1
                break
            else:
                # log_debug("[%s]没有跳空", trade_date)
                pass
        else:
            if rate >= 9.8:
                times += 1
                if times == 1:
                    close0 = close_price
                    log_debug("[%s]本次涨停，开始往前", trade_date)
                else:
                    log_debug("[%s]上次涨停，结束遍历", trade_date)
                    good_to_end = 1
            else:
                high_list.append(high_price)
                low_list.append(low_price)

        last_low = low_price
        # end of for

    days = len(high_list)

    if good_to_end:
        log_info("匹配双涨停")

        if days < 30:
            log_info("天数太短: %d", days)
            return 1
        else:
            log_info("天数够长: %d", days)

        high_desc = heapq.nlargest(5, high_list)
        low_asc   = heapq.nsmallest(5, low_list)
        log_info("high_list: [%s]", high_desc)
        log_info("low_list:  [%s]", low_asc)
        rate1 = (high_desc[0] / low_asc[0] - 1) * 100  # 最大/最小
        rate2 = (high_desc[3] / low_asc[3] - 1) * 100  # 排除前三
        log_info("rate1: [%.2f]", rate1)
        log_info("rate2: [%.2f]", rate2)

        if rate1 <= 21 and rate2 <= 17 and close0 > high_desc[0]:
            log_info("nice2: [%s][%s] matched", _stock_id, _max_date)
            subject = "#break %s %s" % (_stock_id, _max_date)
            content = "%s 横盘%d(days)突破\n" % (_stock_id, days)
            if up_gap:
                content += "## 向上跳空[%s] ##\n" % (trade_date)
            content+= "#. 需要多次踩上MA60\n"
            content+= "#. 需要有很多上影线\n"
            content+= "#. 需要均线发散\n"
            content+= "振幅-全部: %.2f%%\n" % (rate1)
            content+= "振幅-主要: %.2f%%\n" % (rate2)
            content+= get_basic_info_all(_stock_id, _db)
            saimail(subject,  content)
            log_info("mail\n[%s]", content)
            rv = 1
        else:
            log_info("not match: [%s]", _stock_id)
            rv = 0
    else:
        log_info("未匹配双涨停")
        rv = 0

    log_info("-------------------------------------------------------------")

    return 0


"""
获取指定日期股票列表 2017-4-9
"""
def get_stock_list_by_date(_date, _db):
    sql = "select distinct stock_id from tbl_day \
where pub_date='%s' \
and (close_price - last_close_price) / last_close_price * 100 >= 9.8 \
order by 1" % (_date)

    df = pd.read_sql_query(sql, _db);

    if df is None:
        return None

    return df.set_index('stock_id')


def work_one_date(_max_date, _db):
    log_info("max_date: %s", _max_date)
    list_df = get_stock_list_by_date(_max_date, _db)
    if list_df is None:
        log_error("error: get_one_list failure")
        return -1
    else:
        log_debug("list df: \n%s", list_df)
        pass

    for row_index, row in list_df.iterrows():
        stock_id = row_index
        work_one_stock(stock_id, _max_date, _db)

    return 0


def xxx(_db):

    if sai_is_product_mode():
        start_date = get_today()
    else:
        start_date = "2017-01-03"

    start_date = "2017-01-03"
    after = 100

    start_date = get_date_by(-1)
    after = 1

    start_date = "2017-04-11"
    after = 1

    start_date = "2017-01-03"
    after = 1

    start_date = get_newest_trade_date(_db)
    after = 1

    log_info("start_date: [%s]", start_date)

    sql = "select distinct pub_date from tbl_day \
where pub_date >= '%s' order by pub_date limit %d" % (start_date, after)

    log_debug("sql: \n%s", sql)

    date_df = pd.read_sql_query(sql, _db);
    if date_df is None:
        log_info("'%s' not found in db", _stock_id)
        return None
    else:
        date_df.set_index("pub_date", inplace=True)
        log_info("date list: [%s]", date_df)
        pass

    for row_index, row in date_df.iterrows():
        max_date = row_index
        work_one_date(max_date, _db)
        # break

    return 0


def work():
    db = db_init()

    xxx(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("break.log")

    log_info("let's begin here!")

    if sai_is_product_mode():
        # check holiday
        if today_is_weekend():
            log_info("today is weekend, exit")
            work()
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


# break.py
