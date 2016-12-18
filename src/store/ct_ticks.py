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
from saitick import *
from saitu   import *


"""
buy策略：
"""
#######################################################################

g_has_noticed  = {}
g_basic_info   = None

def ct_ticks_analyze(_stock_id, _trade_date, _df, _db):

    # log_debug("\n%s", _df)

    base_list = [1, 200, 400, 800, 1000, 2000, 3000]

    rank = 0.0

    open_price  = _df['price'][0]
    close_price = _df['price'][-1]

    if close_price <= 2.0:
        log_error("warn: stock %s is too cheap, next", _stock_id)
        return -4, None, None, None

    if close_price <= open_price*1.01:
        kk = 9
    else:
        kk = 0


    # with price
    factor = close_price / 10.0

    buy_list  = []
    sell_list = []
    net_list  = []

    counter5 = 0
    counter10 = 0
    counter20 = 0
    counter30 = 0
    counter40 = 0
    counter50 = 0
    # 60,70,80不考虑加权 2016/9/2
    counter60 = 0
    counter70 = 0
    counter80 = 0
    counter_bad = 0
    content = "%s: %s: [%s, %s]\n" % (_stock_id, _trade_date, open_price, close_price)
    min_rate = 10
    for base in base_list :
        rank = 0
        rate = 0.0
        net  = 0.0
        buy, sell = get_buy_sell_sum(_df, base)

        # rate
        if base < 200:
            rate = 2.0
        elif   buy > 0  and sell == 0:
            rate = 3.0
        elif buy == 0 and sell == 0:
            rate = 1.0
        elif buy == 0 and sell > 0:
            rate = -1.0
        elif buy > 0  and sell > 0:
            rate = 1.0 * buy / sell
        else:
            rate = 0.0

        if rate < min_rate:
            min_rate = rate


        diff  = buy - sell
        diff2 = diff * factor
        content += "%04d B: %.2f, S: %.2f, N: %.2f, %.2f\n" % \
                    (base, buy/10000.00, sell/10000.00, diff/10000.00, diff2/10000.00)

        buy_list.append(buy/1000.00)
        sell_list.append(sell/1000.00)
        net_list.append(diff/1000.00)

        # 原始净值 2016/9/2
        if diff >= 1200000:
            counter80 += 1
        if diff >= 1000000:
            counter70 += 1
        if diff >= 600000:
            counter60 += 1

        # 加权净值2016/9/2
        if diff2 >= 500000 or diff >= 500000:
            counter50 += 1
        if diff2 >= 400000:
            counter40 += 1
        if diff2 >= 300000:
            counter30 += 1
        if diff2 >= 200000:
            counter20 += 1
        if diff2 >= 100000:
            counter10 += 1
        if diff2 >= 30000:
            counter5 += 1
        if diff2 < 0:
            counter_bad += 1

    if counter80 >= 6:
        rank = 800
    elif counter70 >= 6:
        rank = 700
    elif counter60 >= 6:
        rank = 600
    elif counter50 >= 6:
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

    # save to db
    dt = get_today()
    tm = get_time()
    sql = "insert into tbl_net_rank \
(pub_date, stock_id, stock_loc,  watcher, \
open_price, close_price, \
net1, net200, net400, net800, net1000, net2000, net3000, \
rank, \
buy1, buy200, buy400, buy800, buy1000, buy2000, buy3000, \
sell1, sell200, sell400, sell800, sell1000, sell2000, sell3000, \
inst_date, inst_time) \
values ('%s', '%s', '%s', '%s',  \
'%.2f', '%.2f', \
'%.2f', '%.2f', '%.2f', '%.2f', '%.2f', '%.2f', '%.2f', \
'%d', \
'%.2f', '%.2f', '%.2f', '%.2f', '%.2f', '%.2f', '%.2f', \
'%.2f', '%.2f', '%.2f', '%.2f', '%.2f', '%.2f', '%.2f', \
'%s', '%s')" % \
    (_trade_date, _stock_id, 'cn', 'sai',
     open_price, close_price,
     net_list[0], net_list[1], net_list[2], net_list[3], net_list[4], net_list[5], net_list[6],
     rank, 
     buy_list[0], buy_list[1], buy_list[2], buy_list[3], buy_list[4], buy_list[5], buy_list[6],
     sell_list[0], sell_list[1], sell_list[2], sell_list[3], sell_list[4], sell_list[5], sell_list[6],
     dt, tm)
    # log_info("%s", sql)

    return  rank, content, sql, min_rate


def ct_ticks(_stocks, _trade_date, _db):
    global g_has_noticed

    tick_set_sina_mode()

    tdall = get_stock_quotation()
    if tdall is None:
        log_error("error: get_stock_quotation")
        return -1

    chged = tdall['changepercent']

    body = ""
    for row_index, row in _stocks.iterrows():
        stock_id = row_index

        tdchg = chged.get(stock_id)
        if tdchg is None:
           tdchg = 0.0
        log_debug("stock %s today changed: %.2f%%", stock_id, tdchg)

        df = get_tick(stock_id, _trade_date)
        if df is None :
            log_error("warn: stock %s, %s is None, next", stock_id, _trade_date)
            continue

        rank, content, sql, rate = ct_ticks_analyze(stock_id, _trade_date, df, _db)
        # if rank >= 500 or (rank >= 109 and rank % 100 == 9):
        # if rank >= 100 or (rank >= 109 and rank % 100 == 9):
        # if rank >= 109 or (rank >= 100 and tdchg > 9.5) or (rank >= 59 and rate >= 2.0):
        if rank >= 100 or (rank >= 50 and tdchg > 9.8) or (rank >= 50 and rate >= 2.0):
            # very good

            if tdchg > 9.8 and rate >= 2.0:
                subject1 = "rank: %d | %s 涨停+高比 %s" % (rank, stock_id, _trade_date)
            elif tdchg > 9.8:
                subject1 = "rank: %d | %s 涨停 %s" % (rank, stock_id, _trade_date)
            elif rate >= 2.0:
                subject1 = "rank: %d | %s 高比 %s" % (rank, stock_id, _trade_date)
            else:
                subject1 = "rank: %d | %s 吸筹 %s" % (rank, stock_id, _trade_date)

            if g_has_noticed.has_key(stock_id):
                pass
            else:
                g_has_noticed[stock_id] = 1

                # 2016/10/16
                basic_info = get_basic_info(stock_id)
                content = content + basic_info

                # 2016/10/16
                xsg_info = get_xsg_info(stock_id, _db)
                content = content + xsg_info

                saimail(subject1, content)
                log_info("%s\n%s", subject1, content)
        else:
            if rank >= 50:
                log_info("nice: %s, rank: %d\n%s", stock_id, rank, content)
                body += content + "\n"
            else:
                if rate is None:
                    log_debug("None");
                else:
                    log_debug("%s, %d, %.2f", stock_id, rank, rate)

        # to db 2016/9/11
        if rank >= 50:
           sql_to_db_nolog(sql, _db)


    # 一次性mail:  TODO
    if len(body) > 0:
        log_info("mail out: %s", body)

    return


def ct_ticks_range(_stock_id, _date_list, _db):

    tick_set_feng_mode()

    body = ""
    for item in _date_list:
        trade_date = str(item).split()[0]
        # log_debug("trade_date: %s", trade_date)

        df = get_tick(_stock_id, trade_date)
        if df is None :
            log_error("warn: stock %s, %s is None, next", _stock_id, trade_date)
            continue

        rank, content, sql, rate = ct_ticks_analyze(_stock_id, trade_date, df, _db)
        if content is not None:
            body += "%d, %.2f, %s\n" % (rank, rate, content)
            log_debug("%s, rank: %.2f\n%s", _stock_id, rank, content)

    return body



def work_one_day(_trade_date, _db):

    # step1: get from web
    begin = get_micro_second()

    stocks = get_stock_list_df_tu()

    log_debug("get_today_all costs: %d", get_micro_second()-begin)

    if stocks is None or stocks.empty:
        return -1
    else:
        # stocks = stocks.head(10)
        log_debug("stock_list :\n%s", stocks)


    # step2: loop the list
    ct_ticks(stocks, _trade_date, _db)

    return


def work_one_stock(_stock_id, _start_date, _days, _db):

    body = ""

    date_list  = pd.date_range(_start_date, periods=int(_days))

    log_debug("trade day: %s", date_list)
    body = ct_ticks_range(_stock_id, date_list, _db)

    # mail
    if len(body) > 0:
        # 2016/10/16
        basic_info = get_basic_info(_stock_id)
        body = body + basic_info

        # 2016/10/16
        xsg_info = get_xsg_info(_stock_id, _db)
        body = body + xsg_info

        subject = "%s, start: %s, days: %s" % (_stock_id, _start_date, _days)
        saimail(subject, body)

    return

"""
usage: 
python ct_ticks.py 
python ct_ticks.py some-day
python ct_ticks.py some-day days stockid
"""
def work(_args):

    # get all stocks info
    global g_basic_info
    g_basic_info = get_stock_list_df_tu()
    if g_basic_info is None:
        log_error("error: get_stock_list_df_tu")
        return 
    else:
        log_info("nice, got stock basics")

    db = db_init()

    argc = len(_args)

    if argc == 0:
        # default mode
        start_date = "2016-08-01"

        # 2016/8/23 good case: 廊坊发展
        stock_id   = "600149"
        start_date = "2016-07-20"
        days       = 35

        start_date = "2016-10-14"
        days       = 1

        stock_id   = "300331"
        stock_id   = "000961"
        log_debug("default::: %s, %s, %s", start_date, days, stock_id)
        work_one_stock(stock_id, start_date, days, db)
    elif argc == 1:

        # mode1: check all stocks
        trade_date = "2016-08-10"
        trade_date = "2016-08-09"

        trade_date = _args[0]

        log_debug("trade_date2: %s", trade_date)

        # check holiday 2016/9/3 && 2016/11/27
        if today_is_weekend():
            log_info("today is weekend, exit")
        else:
            log_info("today is workday, come on")
            work_one_day(trade_date, db)
        # work_one_day(trade_date, db)
    elif argc == 3:
        # mode2: check one stock during several days
        start_date = _args[0]
        days       = _args[1]
        stock_id   = _args[2]

        log_debug("input3: %s, %s, %s", start_date, days, stock_id)

        work_one_stock(stock_id, start_date, days, db)


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

if __name__ == "__main__":
    main()
    exit()

#######################################################################

# ct_ticks.py
