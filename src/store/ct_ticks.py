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
from sairank import *


"""
buy策略：
"""
#######################################################################

g_good_list    = []
g_good_list2   = []
g_good_list3   = []

g_has_noticed  = {}
g_has_noticed2 = {}
g_has_noticed3 = {}

g_has_noticed_rank = {}


g_stock_date  = ""
g_check_count = 0  # 检查是否全天无数据



def ct_ticks_analyze(_stock_id, _trade_date, _db):

    # sina base
    base_vol = 200

    df = None

    try:
        # df = ts.get_sina_dd(_stock_id, date=_trade_date, vol=base_vol)
        df = ts.get_tick_data(_stock_id, date = _trade_date)
    except Exception:
        log_error("warn: %s get ticks exception!", _stock_id)
        time.sleep(5)
        return -4, None

    if df is None :
        # log_error("warn: stock %s is None, next", _stock_id)
        return -1, None

    if df.empty:
        log_error("warn: stock %s is empty, next", _stock_id)
        return -2, None

    if len(df) <= 5:
        log_error("warn: stock %s is empty: %d, next", _stock_id, len(df))
        return -3, None

    """
    #  sina data: convert to 手
    df['volume'] = df['volume'] / 100
    """

    df = df.set_index('time').sort_index()
    # log_debug("\n%s", df)

    base_list = [1, 200, 400, 800, 1000, 2000, 3000]

    rank = 0.0

    open_price  = df['price'][0]
    close_price = df['price'][-1]

    if close_price <= 6.0:
        log_error("warn: stock %s is too cheap, next", _stock_id)
        return -4, None

    if close_price <= open_price:
        kk = 9
    else:
        kk = 0

    factor = close_price / 10.0

    counter5 = 0
    counter10 = 0
    counter20 = 0
    counter30 = 0
    counter40 = 0
    counter50 = 0
    counter_bad = 0
    content = "%s: %s: [%s, %s]\n" % (_stock_id, _trade_date, open_price, close_price)
    for base in base_list :
        rank = 0
        rate = 0.0
        net  = 0.0
        buy, sell = get_buy_sell_sum(df, base)

        # rate
        if buy > 0 and sell > 0:
            rate = 1.0 * buy / sell


        diff = buy - sell
        diff2 = diff * factor
        content += "base(%d):\tbuy: %d, sell: %d, rate: %.2f, net: %d, %.0f\n" % (base, buy, sell, rate, diff, diff2)

        # TODO: with price and total-flow 2016/8/26

        diff = diff2
        if diff >= 500000:
            counter50 += 1
        elif diff >= 400000:
            counter40 += 1
        elif diff >= 300000:
            counter30 += 1
        elif diff >= 200000:
            counter20 += 1
        elif diff >= 100000:
            counter10 += 1
        elif diff >= 30000:
            counter5 += 1
        elif diff < 0:
            counter_bad += 1

    if counter50 >= 6:
        rank = 500
    elif counter40 >= 6:
        rank = 400
    elif counter30 >= 6:
        rank = 300
    elif counter20 >= 6:
        rank = 200
    elif counter10 >= 6:
        rank = 100
    elif counter5 >= 6:
        rank = 50

    if counter_bad > 0:
        rank -= 10
    # log_info("\n%s", content)

    if rank > 0:
        rank += kk

    return  rank, content


def ct_ticks(_stocks, _trade_date, _db):
    global g_has_noticed
    global g_has_noticed2
    global g_has_noticed3

    for row_index, row in _stocks.iterrows():
        """
        name     = row['name']
        stock_id = row['code']
        chg      = row['changepercent']
        op       = row['open']
        high     = row['high']
        low      = row['low']
        """
        stock_id = row_index

        """
        stock_id = '000002'
        """

        """
        if chg > 12:
            log_debug("%s: new stock, ingore it", stock_id)
        elif op == high and high == low :
            log_debug("%s: one one one, ignore too", stock_id)
        else:
            ct_ticks_analyze(stock_id, _trade_date, _db)
        """

        rank, content = ct_ticks_analyze(stock_id, _trade_date, _db)
        if rank >= 300:
            log_info("nice1: %s, rank: %d\n%s", stock_id, rank, content)
            # TODO send mail
        elif rank >= 100:
            log_info("nice2: %s, rank: %d\n%s", stock_id, rank, content)
            # TODO send mail
        elif rank >= 50:
            log_info("nice3: %s, rank: %d\n%s", stock_id, rank, content)
            # TODO send mail
        else:
            log_debug("rank: %s, %d", stock_id, rank)

        """
        break
        """

    return


def ct_ticks_range(_stock_id, _date_list, _db):

    for item in _date_list:
        trade_date = str(item).split()[0]
        # log_debug("trade_date: %s", trade_date)
        # TODO: check is weekend
        rank, content = ct_ticks_analyze(_stock_id, trade_date, _db)
        log_debug("%s, rate: %.2f\n%s", _stock_id, rank, content)


    return

"""
从9点半开始
"""

def rt_timer(_stocks, _trade_date, _db):
    global g_good_list
    global g_good_list2
    global g_good_list3

    end_time  = '15:30:00'
    lun_time1 = '11:35:00'
    lun_time2 = '12:00:00'


    log_debug("trade day: %s", _trade_date)

    counter  = 0
    while 1:
        g_good_list  = []
        g_good_list2 = []
        g_good_list3 = []
        counter = counter + 1

        curr = get_time()

        # 中午休息
        if curr >= lun_time1 and curr <= lun_time2:
            log_info("'%s' means noon time", curr)
            time.sleep(300)
            continue

        log_info(">>>>>let's run here")

        # 遍历股票列表
        ct_ticks(_stocks, _trade_date, _db)

        # 测试模式
        break
        """
        """

        # 当日结束
        curr = get_time()
        if curr >= end_time:
            log_info("'%s' means end today", curr)
            break

        # 降低频率
        time.sleep(300)

    return


def work_one_day(_trade_date, _db):

    # step1: get from web
    begin = get_micro_second()

    stocks = get_stock_list_df_tu()
    # stocks = ts.get_today_all()

    log_debug("get_today_all costs: %d", get_micro_second()-begin)

    if stocks is None or stocks.empty:
        return -1
    else:
        # stocks = stocks.head(10)
        log_debug("stock_list :\n%s", stocks)


    # step2: loop the list
    rt_timer(stocks, _trade_date, _db)

    return


def work_one_stock(_stock_id, _start_date, _days, _db):

    date_list  = pd.date_range(_start_date, periods=int(_days))

    log_debug("trade day: %s", date_list)
    ct_ticks_range(_stock_id, date_list, _db)

    # TODO: mail

    return

"""
usage: 
python ct_ticks.py 
python ct_ticks.py some-day
python ct_ticks.py some-day days stockid
"""
def work(_args):
    db = db_init()

    argc = len(_args)

    if argc == 0:
        # default mode
        start_date = "2016-08-01"

        stock_id   = "000885"
        stock_id   = "000002"

        stock_id   = "600838"
        start_date = "2016-08-01"
        days       = 22

        stock_id   = "002208"
        start_date = "2016-03-01"
        days       = 30
        start_date = "2016-08-01"
        days       = 22

        stock_id   = "000981"
        start_date = "2016-08-15"
        days       = 10

        stock_id   = "600766"
        start_date = "2016-08-01"
        days       = 22

        # 2016/8/23 good case: 廊坊发展
        stock_id   = "600149"
        start_date = "2016-07-20"
        days       = 35

        # 2016/8/23
        stock_id   = "000002"
        start_date = "2016-07-06"
        days       = 40

        stock_id   = "002695"
        start_date = "2016-08-01"
        days       = 40

        stock_id   = "002417"
        start_date = "2016-08-01"
        days       = 24

        stock_id   = "300331"
        stock_id   = "002036"
        stock_id   = "000620"
        stock_id   = "300470"
        stock_id   = "603778"
        stock_id   = "300088"
        stock_id   = "000811"
        stock_id   = "600178"
        stock_id   = "600738"
        stock_id   = "300020"
        stock_id   = "000687"
        stock_id   = "002329"
        log_debug("default::: %s, %s, %s", start_date, days, stock_id)
        work_one_stock(stock_id, start_date, days, db)
    elif argc == 1:

        # mode1: check all stocks
        trade_date = "2016-08-10"
        trade_date = "2016-08-17"
        trade_date = "2016-08-22"
        trade_date = "2016-08-09"

        trade_date = _args[0]

        log_debug("trade_date2: %s", trade_date)

        work_one_day(trade_date, db)
    elif argc == 3:
        # mode2: check one stock during several days
        start_date = _args[0]
        days       = _args[1]
        stock_id   = _args[2]

        log_debug("input3: %s, %s, %s", start_date, days, stock_id)


        work_one_stock(stock_id, start_date, days, db)

    """
    """


    db_end(db)


#######################################################################

def main():
    sailog_set("ct_ticks.log")

    log_info("main begins")

    saimail_init()

    args = get_args()

    work(args)

    log_info("main ends, bye!")
    return

main()
exit()

#######################################################################

# ct_ticks.py
