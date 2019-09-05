#!/usr/bin/env python
# -*- encoding: utf8 -*-

from datetime import *

import numpy as np
import pandas as pd
import baostock as bs
import tushare  as ts

from saiutil import *
from saidb   import *
from saisql  import *
from saicalc import *
from sailog  import *
from saitu   import *

#
# migrate TUSHARE to BAOSTOCK
# 2019-9-2, 9-5
#

#######################################################################

def k_day_one_to_db(_stock_id, _df, _st_date, _db):

    dt = get_today()
    tm = get_time()

    # assume data [1: 100]
    # 1: compare whether to fuquan
    # [1:100] to db

    if _st_date is not None:

        # 1. compare
        # new_close_price = _df['close'][0]
        # new_close_price = _df.iloc[0,2]
        # new_close_price = _df.loc[0, ['close']]
        new_close_price = _df['close'][0]

        # the close price of max-pub-date
        tbl_df = get_one_kday(_stock_id, _st_date, _db)
        tbl_close_price = tbl_df['close_price'][0]

        log_debug("close: web[%s] : [%s]table", new_close_price, tbl_close_price)
        # compare, update if not equal
        rate = new_close_price / tbl_close_price
        if rate == 1.0:
            # log_debug("[%s, %s] no need to fuquan", new_close_price, tbl_close_price)
            pass
        else:
            log_debug("warn! fuquan, rate: %.3f", rate)
            sql = "update tbl_day set open_price = round(open_price * %.3f, 2), \
close_price = round(close_price * %.3f, 2), \
low_price   = round(low_price * %.3f,   2), \
high_price  = round(high_price * %.3f,  2), \
last_close_price = round(last_close_price * %.3f, 2), \
deal_total_count = round(deal_total_count / %.3f, 0) \
deal_total_amount = round(deal_total_amount / %.3f, 0) \
where stock_id = '%s' \
and pub_date <= '%s'" % \
                   (rate, rate, rate, \
                    rate, rate, rate, \
                    rate, \
                    _stock_id, _st_date)
            rv = sql_to_db(sql, _db)
            if rv != 0:
                log_error("error: sql_to_db %s", sql)
                return -1



    # init last close price
    # last_close_price = _df['close'][0]
    # last_close_price = _df.iloc[0,2]

    # import dataframe to db
    counter = 0
    for row_index, row in _df.iterrows():
        if row.loc['volume'] < 1.0:
            log_debug("sorry, no volume: %s, price:%.2f, volume:%.2f",
                    row.loc['date'], row.loc['close'], row.loc['volume'])
            continue

        counter = counter + 1

        pub_date = '%s' % (row.loc['date']) # api for  get-k-data
        # pub_date = '%s' % (row_index) # api for  h-data

        # 前复权
        sql = "insert into tbl_day \
(pub_date, stock_id, stock_loc, \
open_price, high_price, close_price, low_price, \
last_close_price, \
deal_total_count, deal_total_amount, \
inst_date, inst_time) \
values ('%s', '%s', '%s',  \
'%.2f', '%.2f', '%.2f', '%.2f', \
'%.2f', \
'%.3f', '%.3f', \
'%s', '%s')" % \
       (pub_date, _stock_id, 'cn', 
        row.loc['open'], row.loc['high'], row.loc['close'], row.loc['low'],
        row.loc['preclose'],
        row.loc['volume'], row.loc['amount'],
        dt, tm)

        # last_close_price = row.loc['close']

        # log_debug("%s", sql)
        rv = sql_to_db_nolog(sql, _db)
        if rv != 0:
            log_error("error: sql_to_db %s", sql)

    log_debug("%s: processed: %d", _stock_id, counter);

    return 0


def k_day_get_max_date(_stock_id, _db):
    df = get_max_pub_date_kday(_stock_id, _db)

    if df is None :
        log_error("warn: stock %s max-pub-date is None, next", _stock_id)
        return None

    if df.empty:
        log_error("warn: stock %s max-pub-date is empty, next", _stock_id)
        return None

    for row_index, row in df.iterrows():
        max_date = row['pub_date']

    if max_date is not None:
        # log_info("max pub_date is %s", max_date)
        pass

    return max_date


def k_day_one_stock(_stock_id, _db):
    # log_info("k_day_one_stock begin")

    # get max-date from table, as start date
    max_date = k_day_get_max_date(_stock_id, _db)
    ed_date = get_date_by(0)

    # log_debug("[%s, %s]", max_date, ed_date)

    # qfq
    if max_date is None:
        st_date = '2017-07-01'
        st_date = '2014-01-01'
        st_date = '2018-01-03'
        st_date = '2016-01-01'
        log_debug("it's first time: [%s]", _stock_id)
    else:
        st_date = str(max_date)
        # log_debug("a old friend: [%s]", _stock_id)

    log_debug("[%s, %s]", st_date, ed_date)

    # get from web(by tushare)
    begin = get_micro_second()

    try:
        # df = ts.get_k_data(_stock_id, autype='qfq', start=st_date, end=ed_date) # reject by tencent since 2018-7-16
        stock_id = 'sz.'+_stock_id
        c = _stock_id[0]
        if c == '6':
            stock_id = 'sh.'+_stock_id
        log_debug("stock_id: %s => %s", _stock_id, stock_id)

        rs = bs.query_history_k_data_plus(stock_id,
                "date,code,open,high,low,close,preclose,volume,amount",
                start_date=st_date, end_date=ed_date,
                frequency="d", adjustflag="2")
        log_debug('query_history_k_data_plus: %s, %s', rs.error_code, rs.error_msg)

        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        df = pd.DataFrame(data_list, columns=rs.fields)

        df["open"]      = pd.to_numeric(df["open"])
        df["close"]     = pd.to_numeric(df["close"])
        df["high"]      = pd.to_numeric(df["high"])
        df["low"]       = pd.to_numeric(df["low"])
        df["preclose"]  = pd.to_numeric(df["preclose"])
        df["volume"]    = pd.to_numeric(df["volume"])
        df["amount"]    = pd.to_numeric(df["amount"])

    except Exception as e:
        log_error("warn:error: %s get_k_data exception!, %s", _stock_id, e)
        return -4

    # calc cost time
    log_info("get web data [%s] costs %d us", _stock_id, get_micro_second()-begin)

    if df is None :
        log_error("warn: stock %s is None, next", _stock_id)
        return -1

    if df.empty:
        log_error("warn: stock %s is empty, next", _stock_id)
        return -2

    df.sort_index(ascending=True, inplace=True)
    # df = df.sort_index(ascending=True)
    # df = df.reindex(index=range(0, len(df)))
    # log_debug("df: \n%s", df)

    begin = get_micro_second()

    k_day_one_to_db(_stock_id, df, max_date, _db)

    log_info("one_to_db costs %d us", get_micro_second() - begin)

    # log_info("function k_day_one_stock end")

    return 



def k_day_one_check_bad(_stock_id, _db):
    is_bad = False

    # log_info("k_day_one_check begin")

    sql = "select pub_date, close_price from tbl_day where stock_id='%s' order by pub_date" % _stock_id
    # log_debug("%s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None :
        # log_error("warn: stock %s is None, next", _stock_id)
        return False

    if df.empty:
        # log_error("warn: stock %s is empty, return", _stock_id)
        return False

    if len(df) <= 2:
        # log_error("warn: stock %s is short, next", _stock_id)
        return False

    counter = 0
    rate = 0
    this_close = 0
    last_close = 0
    for row_index, row in df.iterrows():
        this_close = row['close_price']
        pub_date   = row['pub_date']

        if this_close <= 0:
            log_error("error: close data %.2f", this_close)
            is_bad = True
            break

        if counter > 0 and last_close > 0:
            rate = abs(this_close - last_close) / last_close * 100
            if rate > 11:
                log_error("bad: %s - %s - %.2f", pub_date, _stock_id, rate)
                log_error("   : %s", sql)
                is_bad = True
                break

        counter = counter + 1
        last_close = this_close

    if is_bad:
        log_info("delete: %s is bad, let's clear data", _stock_id)

        #
        sql = "delete from tbl_day where stock_id = '%s'" % (_stock_id)
        log_debug("day sql: [%s]", sql)
        rv = sql_to_db(sql, _db)

        # add tbl_30min 2017-6-18
        sql = "delete from tbl_30min where stock_id = '%s'" % (_stock_id)
        log_debug("30min sql: [%s]", sql)
        rv = sql_to_db(sql, _db)

        # add tbl_week 2017-7-9
        sql = "delete from tbl_week where stock_id = '%s'" % (_stock_id)
        log_debug("week sql: [%s]", sql)
        rv = sql_to_db(sql, _db)

        # add tbl_30min 2017-9-6
        sql = "delete from tbl_15min where stock_id = '%s'" % (_stock_id)
        log_debug("15min sql: [%s]", sql)
        rv = sql_to_db(sql, _db)

    return is_bad 


def work():
    db = db_init()

    lg = bs.login()
    log_debug("bs: login code: %s", lg.error_code)
    if lg.error_code != "0":
        log_info("error: login failure: %s, %s", lg.error_code, lg.error_msg)
        return 1



    """
    stock_id = "600050"
    stock_id = "002460"
    stock_id = "000932"
    stock_id = "300107"
    stock_id = "300735"
    stock_id = "000590"
    stock_id = "603996"
    log_debug("stock: %s", stock_id)
    k_day_one_stock(stock_id, db)
    return 0
    """


    # max-much
    # stocks = get_stock_quotation() # bug only 100 rows 2017-6-7 -- fixed by upgrade 2017-7-5

    # much
    # step1: get from web
    # stocks = get_stock_list_df_tu() # not real time 2017-5-31

    # TODO: TMP 2017-6-7
    # table = "tbl_day"
    # stocks = get_stock_list_table(table, db)

    # 2018-6-1
    stocks = get_stock_quotation()
    if stocks is None:
        log_error('error: warn:  get_stock_quotation failure')
        stocks = get_stock_list_df_tu()
        if stocks is None:
            log_error('error: warn:  get_stock_list_df_tu failure')
            stocks = get_stock_list_table('tbl_day', db)
            log_info('3: stock list used from table: %d', len(stocks))
        else:
            log_info('2: stock list used from get_stock_list_df_tu -- get_stock_basics')
    else:
        log_info('1: stock list used from get_stock_quotation -- get_today_all')
        log_info('df\n%s', stocks)

    # step2: to db
    begin = get_micro_second()

    # to db
    for row_index, row in stocks.iterrows():
        stock_id = row_index
        log_debug("stock: %s", stock_id)

        # check bad data
        # stock_id = "002837"
        k_day_one_check_bad(stock_id, db)
        # break

        # import to DB
        k_day_one_stock(stock_id, db)

    log_info("save-all costs %d us", get_micro_second()-begin)


    """
    stock_id = "700002"
    start = k_day_get_max_date(stock_id, db);
    log_debug("start: [%s]", start);
    """

    bs.logout()

    db_end(db)


#######################################################################

def main():
    sailog_set("kday_bs.log")

    log_info("let's begin here!")

    if sai_is_product_mode():
        if today_is_weekend():
            log_info("today is weekend, exit")
            # work()
        else:
            log_info("today is workday, come on")
            work()
    else:
        work()

    log_info("main ends, bye!")
    return

main()
exit()

#######################################################################


# k_day_bs.py
