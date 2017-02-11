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
    chance3000 = 0

    open_price  = _df['price'][0]
    close_price = _df['price'][-1]

    if close_price <= 2.0:
        log_error("warn: stock %s is too cheap, next", _stock_id)
        return -4, None, None, None, None, None, None

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

        # 3000 special -- 2016-12-25
        if base == 3000:
            buy3  = buy  / 10000.00
            sell3 = sell / 10000.00
            diff3 = diff / 10000.00
            if rate >= 20 and diff3 >= 20:
                log_info("无脑入20: [%.2f][%.2f]", rate, diff3)
                chance3000 = 7
                content += "3000 -- 无脑入20\n"
            elif rate >= 20 and diff3 >= 15:
                log_info("无脑入15: [%.2f][%.2f]", rate, diff3)
                chance3000 = 6
                content += "3000 -- 无脑入15\n"
            elif rate >= 10 and diff3 >= 10:
                log_info("很强烈10: [%.2f][%.2f]", rate, diff3)
                chance3000 = 5
                content += "3000 -- 很强烈10\n"
            elif rate >= 10 and diff3 >= 5:
                log_info("较强烈05: [%.2f][%.2f]", rate, diff3)
                chance3000 = 3
                content += "3000 -- 较强烈05\n"
            elif buy3 >= 3 and sell3 <= 0.0:
                log_info("无卖盘03: [%.2f][%.2f]", buy3, sell3)
                chance3000 = 1
                content += "3000 -- 无卖盘03\n"
            else:
                log_debug("3000: [%.2f][%.2f][%.2f]", buy3, sell3, rate)
                chance3000 = 0

        buy_list.append(buy/10000.00)
        sell_list.append(sell/10000.00)
        net_list.append(diff/10000.00)

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

    return  rank, content, min_rate, buy_list, sell_list, net_list, chance3000


def get_history_rank(_stock_id, _trade_date, _db):
    sql = "select * from tbl_net_rank where stock_id='%s' \
and pub_date < '%s' order by pub_date desc limit 3" % (_stock_id, _trade_date)
    # log_debug("%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("rank no history1", _stock_id)
        return ""
    elif df.empty:
        log_debug("df is empty: [%d]", len(df))
        return ""
    else:
        pass
        log_debug("nice: tick history [%d]", len(df))

    content = ""
    for row_index, row in df.iterrows():
        factor = row['close_price'] / 10.0
        item = "\nrank: %.0f, %s, %s, %.2f元\n" % (row['rank'], row['subject'], row['pub_date'], row['close_price'])
        item  += "0001 B: %.2f, S: %.2f, N: %.2f, %.2f\n" % (row['buy1'], row['sell1'], row['net1'], row['net1']*factor)
        item  += "0200 B: %.2f, S: %.2f, N: %.2f, %.2f\n" % (row['buy200'], row['sell200'], row['net200'], row['net200']*factor)
        item  += "0400 B: %.2f, S: %.2f, N: %.2f, %.2f\n" % (row['buy400'], row['sell400'], row['net400'], row['net400']*factor)
        item  += "0800 B: %.2f, S: %.2f, N: %.2f, %.2f\n" % (row['buy800'], row['sell800'], row['net800'], row['net800']*factor)
        item  += "1000 B: %.2f, S: %.2f, N: %.2f, %.2f\n" % (row['buy1000'], row['sell1000'], row['net1000'], row['net1000']*factor)
        item  += "2000 B: %.2f, S: %.2f, N: %.2f, %.2f\n" % (row['buy2000'], row['sell2000'], row['net2000'], row['net2000']*factor)
        item  += "3000 B: %.2f, S: %.2f, N: %.2f, %.2f\n" % (row['buy3000'], row['sell3000'], row['net3000'], row['net3000']*factor)
        content = content + item

    # log_info("history: \n%s", content)
    return content


def ct_ticks(_stocks, _trade_date, _db):
    global g_has_noticed

    if sai_is_product_mode():
        tick_set_sina_mode()
    else:
        tick_set_feng_mode()

    tdall = get_stock_quotation()
    if tdall is None:
        log_error("error: get_stock_quotation")
        return -1

    chged = tdall['changepercent']
    open_se = tdall['open']
    close_se= tdall['trade']

    body = ""
    for row_index, row in _stocks.iterrows():
        stock_id = row_index

        tdchg = chged.get(stock_id)
        if tdchg is None:
            tdchg = 0.0
        log_debug("stock %s today changed: %.2f%%", stock_id, tdchg)

        op = open_se.get(stock_id)
        if op is None:
            op = 0.0
            op = get_open_price(stock_id)
            if op is None:
               op = 0

        cp = close_se.get(stock_id)
        if cp is None:
            cp = get_curr_price(stock_id)
            if cp is None:
               cp = 0

        log_debug("open: %.2f, close: %.2f", op, cp)

        df = get_tick(stock_id, _trade_date)
        if df is None :
            log_error("warn: stock %s, %s is None, next", stock_id, _trade_date)
            continue

        subject0 = "流入"
        db_cata  = "0"
        rank, content, rate, list1, list2, list3, chance = ct_ticks_analyze(stock_id, _trade_date, df, _db)
        # if rank >= 500 or (rank >= 109 and rank % 100 == 9):
        # if rank >= 100 or (rank >= 109 and rank % 100 == 9):
        # if rank >= 109 or (rank >= 100 and tdchg > 9.5) or (rank >= 59 and rate >= 2.0):
        if rank >= 100 or (rank >= 50 and tdchg > 9.8) or (rank >= 50 and rate >= 2.0):
            # very good

            if tdchg > 9.8 and rate >= 2.0:
                subject0 = "涨停+高比"
                db_cata  = "4"
            elif tdchg > 9.8:
                subject0 = "涨停"
                db_cata  = "3"
            elif rate >= 2.0:
                subject0 = "高比"
                db_cata  = "2"
            else:
                subject0 = "吸筹"
                db_cata  = "1"

            if chance == 7:
                subject0 += "+无脑3K20"
            if chance == 6:
                subject0 += "+无脑3K15"
            elif chance == 5:
                subject0 += "+兴奋3K10"
            elif chance == 3:
                subject0 += "+兴奋3K05"
            elif chance == 1 and tdchg > -9:
                subject0 += "+机会3K03"

            subject1 = "rank: %d | %s %s %s" % (rank, stock_id, subject0, _trade_date)

            if g_has_noticed.has_key(stock_id):
                pass
            else:
                g_has_noticed[stock_id] = 1

                """
                # 2016/10/16
                basic_info = get_basic_info(stock_id)
                content = content + basic_info

                # 2016/10/16
                xsg_info = get_xsg_info(stock_id, _db)
                content = content + xsg_info
                """

                # all-info 2016/12/24
                all_info = get_basic_info_all(stock_id, _db)
                content = content + all_info

                # his-rank 2016/12/24
                his_info = get_history_rank(stock_id, _trade_date, _db)
                content = content + his_info

                log_info("%s\n%s", subject1, content)
                if sai_is_product_mode():
                    saimail(subject1, content)
                else:
                    log_info("simulate: mail")
                    # saimail(subject1, content)
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
            dt = get_today()
            tm = get_time()
            sql = "insert into tbl_net_rank \
(pub_date, stock_id, stock_loc,  watcher, \
open_price, close_price, \
net1, net200, net400, net800, net1000, net2000, net3000, \
subject, cata, rate, \
rank, \
buy1, buy200, buy400, buy800, buy1000, buy2000, buy3000, \
sell1, sell200, sell400, sell800, sell1000, sell2000, sell3000, \
inst_date, inst_time) \
values ('%s', '%s', '%s', '%s',  \
'%.2f', '%.2f', \
'%.2f', '%.2f', '%.2f', '%.2f', '%.2f', '%.2f', '%.2f', \
'%s', '%s', '%.2f', \
'%d', \
'%.2f', '%.2f', '%.2f', '%.2f', '%.2f', '%.2f', '%.2f', \
'%.2f', '%.2f', '%.2f', '%.2f', '%.2f', '%.2f', '%.2f', \
'%s', '%s')" %  (_trade_date, stock_id, 'cn', 'sai', op, cp, list3[0], list3[1], list3[2], list3[3], list3[4], list3[5], list3[6], subject0, db_cata, tdchg, rank, list1[0], list1[1], list1[2], list1[3], list1[4], list1[5], list1[6], list2[0], list2[1], list2[2], list2[3], list2[4], list2[5], list2[6], dt, tm)
            log_debug("%s", sql)
            sql_to_db_nolog(sql, _db)

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

        rank, content, rate, l1, l2, l3, ch = ct_ticks_analyze(_stock_id, trade_date, df, _db)
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
        """
        # 2016/10/16
        basic_info = get_basic_info(_stock_id)
        body = body + basic_info

        # 2016/10/16
        xsg_info = get_xsg_info(_stock_id, _db)
        body = body + xsg_info
        """

        all_info = get_basic_info_all(_stock_id, _db)
        body = body + all_info

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

        stock_id   = "000672"
        trade_date = "2016-12-23"
        log_debug("default::: %s, %s, %s", start_date, days, stock_id)
        # work_one_stock(stock_id, start_date, days, db)
        get_history_rank(stock_id, trade_date, db)
    elif argc == 1:

        # mode1: check all stocks
        trade_date = "2016-08-10"
        trade_date = "2016-08-09"

        trade_date = _args[0]

        log_debug("trade_date2: %s", trade_date)

        # check holiday 2016/9/3 && 2016/11/27
        if sai_is_product_mode():
            if today_is_weekend():
                log_info("today is weekend, exit")
            else:
                log_info("today is workday, come on")
                work_one_day(trade_date, db)
        else:
            work_one_day(trade_date, db)
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

    args = get_args()

    work(args)

    log_info("main ends, bye!")
    return

if __name__ == "__main__":
    main()
    exit()

#######################################################################

# ct_ticks.py
