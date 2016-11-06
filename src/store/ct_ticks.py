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

g_has_noticed  = {}
g_basic_info   = None

def ct_ticks_analyze(_stock_id, _trade_date, _db):

    # sina base
    base_vol = 200

    df = None

    try:
        # df = ts.get_sina_dd(_stock_id, date=_trade_date, vol=base_vol)
        df = ts.get_tick_data(_stock_id, date = _trade_date, retry_count=5, pause=1)
    except Exception:
        log_error("warn: %s get ticks exception!", _stock_id)
        time.sleep(5)
        return -4, None, None

    if df is None :
        log_error("warn: stock %s, %s is None, next", _stock_id, _trade_date)
        return -1, None, None

    if df.empty:
        log_error("warn: stock %s, %s is empty, next", _stock_id, _trade_date)
        return -2, None, None

    if len(df) <= 5:
        log_error("warn: stock %s, %s is short %d, next", _stock_id, _trade_date, len(df))
        return -3, None, None

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

    if close_price <= 2.0:
        log_error("warn: stock %s is too cheap, next", _stock_id)
        return -4, None, None

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
    for base in base_list :
        rank = 0
        rate = 0.0
        net  = 0.0
        buy, sell = get_buy_sell_sum(df, base)

        # rate
        if buy > 0 and sell > 0:
            rate = 1.0 * buy / sell


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

    return  rank, content, sql

def get_basic_info(_stock_id, _db):
    global g_basic_info
    # TODO: check whether df contains this stock
    row = g_basic_info.loc[_stock_id, :]

    # 名称, 行业, 地区
    # 市盈率, 流通股本, 总股本, 上市日期
    info  = "%s-%s-%s\n" % (row['name'], row['industry'], row['area'])
    info += "市盈率 : %s\n" % row['pe']
    v1 = float(row['outstanding']) / 10000.00
    info += "流通股 : %.2f亿股\n" % v1
    v2 = float(row['totals']) / 10000.00
    info += "总股本 : %.2f亿股\n" % v2
    info += "上市   : %s\n" % row['timeToMarket']

    log_debug("info:\n%s", info)

    return info


def get_xsg_info(_stock_id, _db):
    info = ""

    xsg = get_xsg_df(_stock_id, _db)

    if xsg is None:
        return info

    if len(xsg) > 0:
        info = "解禁   :\n"

    for row_index, row in xsg.iterrows():
        info += "%s - %5s%% - %s 万\n" % (row['free_date'], row['ratio'], row['free_count'])

    log_debug("info:\n%s", info)
    return info


def ct_ticks(_stocks, _trade_date, _db):
    global g_has_noticed

    body = ""
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

        rank, content, sql = ct_ticks_analyze(stock_id, _trade_date, _db)
        # if rank >= 500 or (rank >= 109 and rank % 100 == 9):
        # if rank >= 100 or (rank >= 109 and rank % 100 == 9):
        if rank >= 59:
            # very good
            subject1 = "###rank: %d | %s 吸筹 %s" % (rank, stock_id, _trade_date)
            if g_has_noticed.has_key(stock_id):
                pass
            else:
                g_has_noticed[stock_id] = 1

                # 2016/10/16
                basic_info = get_basic_info(stock_id, _db)
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
                log_debug("%s, %d", stock_id, rank)

        # to db 2016/9/11
        if rank >= 50:
           sql_to_db_nolog(sql, _db)


    # 一次性mail:  TODO
    if len(body) > 0:
        log_info("mail out: %s", body)

    return


def ct_ticks_range(_stock_id, _date_list, _db):

    body = ""
    for item in _date_list:
        trade_date = str(item).split()[0]
        # log_debug("trade_date: %s", trade_date)
        # TODO: check is weekend
        rank, content, sql = ct_ticks_analyze(_stock_id, trade_date, _db)
        if content is not None:
            body += "%d, %s\n" % (rank, content)
            log_debug("%s, rank: %.2f\n%s", _stock_id, rank, content)

    return body



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
    ct_ticks(stocks, _trade_date, _db)

    return

def get_basic_info(_stock_id, _db):
    global g_basic_info
    # TODO: check whether df contains this stock
    row = g_basic_info.loc[_stock_id, :]

    # 名称, 行业, 地区
    # 市盈率, 流通股本, 总股本, 上市日期
    info  = "%s-%s-%s\n" % (row['name'], row['industry'], row['area'])
    info += "市盈率 : %s\n" % row['pe']
    v1 = float(row['outstanding']) / 10000.00
    info += "流通股 : %.2f亿股\n" % v1
    v2 = float(row['totals']) / 10000.00
    info += "总股本 : %.2f亿股\n" % v2
    info += "上市   : %s\n" % row['timeToMarket']

    log_debug("info:\n%s", info)

    return info


def work_one_stock(_stock_id, _start_date, _days, _db):

    body = ""

    date_list  = pd.date_range(_start_date, periods=int(_days))

    log_debug("trade day: %s", date_list)
    body = ct_ticks_range(_stock_id, date_list, _db)

    # mail
    if len(body) > 0:
        # 2016/10/16
        basic_info = get_basic_info(_stock_id, _db)
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
    g_basic_info = ts.get_stock_basics()
    if g_basic_info is None:
        log_error("error: ts.get_stock_basics")
        return 

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
        days       = 26

        stock_id   = "000002"
        start_date = "2016-08-01"
        days       = 1

        start_date = "2016-10-14"
        days       = 1

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
        stock_id   = "000402"
        stock_id   = "000961"
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

        # check holiday 2016/9/3
        """
        if today_is_weekend():
            log_info("today is weekend, exit")
        else:
            log_info("today is workday, come on")
            work_one_day(trade_date, db)
        """
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

if __name__ == "__main__":
    main()
    exit()

#######################################################################

# ct_ticks.py
