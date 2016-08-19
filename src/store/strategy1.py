#!/usr/bin/env python
# -*- encoding: utf8 -*-


from sqlalchemy import create_engine
import tushare as ts
import MySQLdb
import time
import pandas as pd
import numpy as np

from saiutil import *
from saidb   import *
from saisql  import *
from saicalc import *
from sailog  import *
from saimail import *

#######################################################################


g_mail_list = []

"""
"""

def get_df_from_db1(_stock_id, _db):
    dt = get_date_by(0)
    #sql = "select * from tbl_30min t where stock_id='%s' order by pub_date desc, pub_time desc limit 300" % _stock_id
    #sql = "select * from tbl_30min t where stock_id='%s' order by pub_date desc, pub_time desc limit 10" % _stock_id
    sql = "select * from tbl_30min t where pub_date = '%s' and stock_id='%s' \
           order by pub_date desc, pub_time desc limit 1" % (dt, _stock_id)

    sql = "select * from tbl_30min t where stock_id='%s' \
           order by pub_date desc, pub_time desc limit 1" % (_stock_id)

    # log_debug("sql: [%s]", sql)

    df = pd.read_sql_query(sql, _db);

    return df


def strategy1_get_one(_stock_id, _db):

    df = get_df_from_db1(_stock_id, _db)

    if df is None:
        # print "stock %s none,  exit" % _stock_id
        return None

    if df.empty:
        # print "stock %s emtpy, exit" % _stock_id
        return None

    df = df.set_index(['pub_date', 'pub_time'])
    df = df.sort_index(ascending=True)

    return df


# execute the algorithm
def strategy1_rule_one(_stock_id, _df, _list):

    last  = _df.tail(1)
    idx   = last.index[0]

    op    = last['open_price'][0]
    close = last['close_price'][0]
    high  = last['high_price'][0]
    low   = last['low_price'][0]

    ma5   = last['ma5'][0]
    ma10  = last['ma10'][0]
    ma20  = last['ma20'][0]

    minp = min(ma5, ma10, ma20)
    maxp = max(ma5, ma10, ma20)

    rate = minp / maxp * 100

    body = ""

    if close >= op \
        and close >= maxp \
        and op    <= minp \
        and ( (rate  >= 99.85 and close >= 10.00 )  or (rate  >= 99.9 and close <  10.00 ) ) \
        and 1     == 1:
        # log_info("buy: %s at %s", _stock_id, idx)
        # log_debug("stock: %s, close: %.2f, open: %.2f", _stock_id, close, op)
        # log_debug(">>>ma5: %.2f, ma10: %.2f, ma20: %.2f", ma5, ma10, ma20)
        # log_debug(">>>min: %.2f, max: %.2f,  rate: %.2f", minp, maxp, rate)
        body += "buy: %s at %.2f. (%.2f, %.2f, %.2f) %s\n" % (_stock_id, close, ma5, ma10, ma20, idx)
        log_debug(">>>%s", body)
    else :
        # log_info("not ready: %s at %s", _stock_id, idx)
        pass

    if len(body) > 0:
        _list.append(body)

    return


def strategy1_check(_stocks, _db):
    global g_mail_list

    for row_index, row in _stocks.iterrows():
        stock_id = row_index
        # log_debug("---stock is %s",  stock_id)

        # get df
        begin = get_micro_second()
        df = strategy1_get_one(stock_id, _db)
        # log_debug("get_one costs %d", get_micro_second() - begin)

        if df is None :
            continue

        # check rule
        begin = get_micro_second()
        strategy1_rule_one(stock_id, df, g_mail_list)
        # log_debug("rule_one costs %d", get_micro_second() - begin)
        """
        """

    return


"""
从10点开始，每半小时执行一次
"""

def rt_timer(_stocks, _db):
    end_time = '16:00:00'
    time_map = {'10:15:00':0, '10:45:00':0,
        '11:15:00':0, '11:45:00':0,
        '13:45:00':0, '14:15:00':0,
        '14:45:00':0, '15:15:00':0}

    """ -- test data
    time_map = {'10:05:00':0, '10:35:00':0,
        '11:05:00':0, '11:35:00':0,
        '13:35:00':0, '14:05:00':0,
        '14:35:00':0, '15:05:00':0,
        '15:32:00':0, '15:33:00':0}
    """

    counter = 0

    while 1:
        counter = counter + 1
        to_run = check_time_to_run(time_map)

        if to_run:
            log_info(">>>>>let's run here")

            begin = get_micro_second()

            # check at this time
            strategy1_check(_stocks, _db)
            log_debug("check accomplished")

            diff = get_micro_second() - begin;
            log_info("check costs %d us", diff)

            # mail
            if len(g_mail_list) > 0 :
                log_info("let's mail")
                subject = "strategy1: ma5, ma10, ma20"
                body    = ""
                for item in g_mail_list :
                    body   +=  item
                saimail(subject, body)

        else:
            # log every 10 minutes(20s * 30).
            if counter == 30:
                log_debug(">>>>>sorry, no need to run")
                counter = 0

        curr = get_time()
        if curr >= end_time:
            log_info("'%s' means end today", curr)
            break

        time.sleep(20)

    return


def work():
    db = db_init()

    saimail_init()

    # get list of all stocks
    stocks = get_stock_list_df_db(db)
    log_debug("get stock list: %s",  stocks)

    # run 6 times a day
    rt_timer(stocks, db)

    db_end(db)


#######################################################################

def main():
    print "let's begin here!"

    sailog_set("strategy1.log")

    begin = get_micro_second()

    work()

    log_debug("work costs %d", get_micro_second() - begin)

    log_debug("+++++++++++++++++++++++++++++++++++++++++++++++++")
    """
    """

    print "main ends, bye!"

    return

main()
exit()
print "can't arrive here"

#######################################################################

# strategy1.py
