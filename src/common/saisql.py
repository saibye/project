#!/usr/bin/env python
# -*- encoding: utf8 -*-

import tushare as ts
import time
import pandas as pd
import numpy as np

from saiutil import *
from sailog  import *
from saitu   import *
from saidb   import *
from saimail import *



def sql_to_db_nolog(_sql, _db):
    cursor = _db.cursor()

    rv = 0

    try:
        cursor.execute(_sql)
        _db.commit()
    except Exception as e:
        _db.rollback()
        rv = -1

    return rv


def sql_to_db(_sql, _db):

    # 使用cursor()方法获取操作游标 
    cursor = _db.cursor()

    rv = 0

    try:
        # 执行sql语句
        cursor.execute(_sql)
        # 提交到数据库执行
        _db.commit()
    except Exception as e:
        # 发生错误时回滚
        log_error("error: sql failed for: %s", e)
        log_error("error: [%s]", _sql)
        _db.rollback()
        rv = -1

    return rv


def df_to_db(_stock_id, _df, _db):
    log_debug("i'm importing %s", _stock_id)

    dt = get_today()
    tm = get_time()

    for row_index, row in _df.iterrows():
        date2, time2 = row_index.split()
        #log_debug("date: %s, time: %s", date2, time2)
        #log_deubg("close is %s ", row.loc['close'])
        sql = row_to_sql(_stock_id, row_index, row, dt, tm)
        sql_to_db(sql, _db)

    return



def row_to_sql(_stock_id, _row_index, _row, _dt, _tm):
    date1, time1 = _row_index.split()

    sql = "insert into tbl_30min \
(pub_date, pub_time, stock_id, stock_loc, \
open_price, high_price, close_price, low_price, \
price_change, change_rate, deal_total_count, \
ma5, ma10, ma20, \
vma5, vma10, vma20, \
turnover, \
inst_date, inst_time) \
values ('%s', '%s', '%s', '%s',  \
'%.02f', '%.2f', '%.2f', \
'%.2f', '%.2f', '%.2f', \
'%.2f', '%.2f', '%.2f', \
'%.2f', \
'%.2f', '%.2f', '%.2f', '%.2f', \
'%s', '%s')" % \
    (date1, time1, _stock_id, 'cn', 
     _row.loc['open'], _row.loc['high'], _row.loc['close'], _row.loc['low'],
     _row.loc['price_change'], _row.loc['p_change'], _row.loc['volume'],
     _row.loc['ma5'], _row.loc['ma10'], _row.loc['ma20'],
     _row.loc['v_ma5'], _row.loc['v_ma10'], _row.loc['v_ma20'],
     _row.loc['turnover'],
     _dt, _tm)

    return sql


"""
2016/8/16
"""
def get_stock_list_table(_table, _db):
    sql = "select distinct stock_id from %s order by 1" % _table

    df = pd.read_sql_query(sql, _db);
    if df is None:
        return None
    else :
        return df.set_index('stock_id')

"""
2016/10/30
"""
def get_max_pub_date_kday(_stock_id, _db):
    sql = "select max(pub_date) pub_date from tbl_day where stock_id='%s'" % _stock_id

    df = pd.read_sql_query(sql, _db);

    return df


def get_one_kday(_stock_id, _pub_date, _db):
    sql = "select * from tbl_day where stock_id='%s' and pub_date='%s'" % (_stock_id, _pub_date)

    df = pd.read_sql_query(sql, _db);

    return df

"""
2016/12/25
"""
def get_max_pub_date_time_kunit(_stock_id, _table, _db):
    sql = "select max(pub_date_time) pub_date_time from %s where stock_id='%s'" % (_table, _stock_id)

    df = pd.read_sql_query(sql, _db);

    return df

"""
2017-7-9
"""
def get_max_pub_date_kweek(_stock_id, _db):
    sql = "select max(pub_date) pub_date from tbl_week where stock_id='%s'" % (_stock_id)

    df = pd.read_sql_query(sql, _db);

    return df

def get_one_kunit(_stock_id, _pub_date, _table, _db):
    sql = "select * from %s where stock_id='%s' and pub_date_time='%s'" % (_table, _stock_id, _pub_date)

    df = pd.read_sql_query(sql, _db);

    return df


def get_recent_pub_date(_pub_date, _N, _db):
    sql = "select distinct pub_date from tbl_day x where pub_date <='%s' order by pub_date desc limit %d" % (_pub_date, _N)

    df = pd.read_sql_query(sql, _db);

    return df


"""
2016/10/16
"""
def get_xsg_df(_stock_id, _db):
    sql = "select free_date, free_count, ratio from tbl_xsg where stock_id = '%s' order by free_date" % _stock_id
    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in xsg", _stock_id)
        return None
    else:
        # log_debug("df: \n%s", df)
        return df


def get_xsg_info(_stock_id, _db):
    info = ""

    xsg = get_xsg_df(_stock_id, _db)

    if xsg is None:
        return info

    if len(xsg) > 0:
        info = "解禁   :\n"

    for row_index, row in xsg.iterrows():
        info += "%s - %5s%% - %s 万\n" % (row['free_date'], row['ratio'], row['free_count'])

    # log_debug("info:\n%s", info)

    return info


"""
2017/5/29
"""
def get_rename_df(_stock_id, _db):
    sql = "select inst_date, stock_old_name, stock_new_name \
from tbl_name where stock_id = '%s' order by inst_date" % _stock_id
    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in xsg", _stock_id)
        return None
    else:
        return df


def get_rename_info(_stock_id, _db):
    info = ""

    xsg = get_rename_df(_stock_id, _db)

    if xsg is None:
        return info

    if len(xsg) > 0:
        info = "摘帽   :\n"

    for row_index, row in xsg.iterrows():
        info += "%s - %s => %s\n" % (row['inst_date'], row['stock_old_name'], row['stock_new_name'])

    # log_debug("info:\n%s", info)

    return info

def sai_save_good(_stock_id, _pub_date, _good_type, _key1, _key2, _key3, _key4, _db):
    inst_date = get_today()
    inst_time = get_time()

    sql = "insert into tbl_good \
(pub_date, stock_id, stock_loc, \
holder, good_type, good_reason, \
v1, v2, v3, v4, \
is_valid, inst_date, inst_time) \
values ('%s', '%s', '%s', \
'%s', '%s', '%s', \
'%s', '%s', '%s', '%s', \
'%s', '%s', '%s')" % \
    (_pub_date, _stock_id, 'cn', 
     'sai', _good_type, 'sweet',
     _key1, _key2, _key3, _key4,
     '1', inst_date, inst_time)

    # log_debug("sql: [%s]", sql)
    rv = sql_to_db(sql, _db)

    return rv


"""
2016/12/11
最后一个交易日期
"""
def get_last_trade_date(_stock_id, _db):
    sql = "select max(pub_date) pub_date from tbl_day where stock_id='%s'" % _stock_id

    df = pd.read_sql_query(sql, _db);
    if df is None :
        log_error("warn: stock %s last-trade-date is None, next", _stock_id)
        return None

    if df.empty:
        log_error("warn: stock %s last-trade-date is empty, next", _stock_id)
        return None

    last_date = df.iloc[0, 0]

    if last_date is not None:
        last_date = str(last_date)
        log_info("last trade date is %s", last_date)

    return last_date


def get_basic_info2(_stock_id, _db):
    info = ""

    sql = "select * from tbl_basic where stock_id = '%s'" % _stock_id
    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in basic", _stock_id)
        return info
    else:
        # log_debug("df: \n%s", df)
        pass

    if len(df) > 0:
        # 名称, 行业, 地区
        # 市盈率, 流通股本, 总股本, 上市日期
        info  = "%s-%s-%s\n" % (df['stock_name'][0], df['industry'][0], df['area'][0])

        info += "市盈率 : %s\n" % df['pe'][0]

        # 流通股
        v1 = float(df['outstanding'][0])

        # 当前价
        c = get_curr_price(_stock_id)
        if c is not None:
            v3 = c * v1
            info += "流通市 : %.2f亿\n" % v3

        info += "流通股 : %.2f亿股\n" % v1

        # 总股本
        v2 = float(df['totals'][0])
        info += "总股本 : %.2f亿股\n" % v2
        info += "上市   : %s\n" % df['time_to_market'][0]

    return info


"""
最新的复牌
"""
def get_fupai_info(_stock_id, _db):
    info = ""

    sql = "select * from tbl_fupai \
where stock_id = '%s' \
order by fupai_date desc limit 1" % (_stock_id)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in fupai", _stock_id)
        return info
    else:
        # log_debug("df: \n%s", df)
        pass

    if len(df) > 0:
        #  停牌日期, 复牌日期, 天数
        info  = "复牌   :\n"
        info += "%s - %s - %s天\n" % (df['tingpai_date'][0], df['fupai_date'][0], df['days'][0])

    return info

"""
2017-3-26
"""
def get_dadan_df(_stock_id, _db):
    sql = "select * from tbl_good where stock_id = '%s' and good_type like 'dadan%%' order by pub_date desc limit 7" % _stock_id
    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in good", _stock_id)
        return None
    else:
        # log_debug("df: \n%s", df)
        return df

def get_dadan_info(_stock_id, _db):
    info = ""

    dd = get_dadan_df(_stock_id, _db)

    if dd is None:
        return info

    if len(dd) > 0:
        info = "大单   :\n"

    for row_index, row in dd.iterrows():
        info += "%s,%s - %s, %.0f手(%.0f), p%s\n" % (row['pub_date'], row['v4'], row['good_type'], row['v1'], row['v3'], row['v2'])

    # log_debug("info:\n%s", info)

    return info

"""
2017-4-6
龙湖榜
"""
def get_longhu_df(_stock_id, _db):
    sql = "select * from tbl_top_list where stock_id = '%s' order by pub_date desc limit 5" % _stock_id
    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in tbl_top_list", _stock_id)
        return None
    else:
        # log_debug("df: \n%s", df)
        return df

def get_longhu_info(_stock_id, _db):
    info = ""

    lh = get_longhu_df(_stock_id, _db)

    if lh is None:
        return info

    if len(lh) > 0:
        info = "龙虎榜 (千万元) :\n"

    for row_index, row in lh.iterrows():
        info += "%s ……%s\n 买:%.2f, 卖:%.2f, 净:%.2f\n" % (row['pub_date'], row['reason'][-17:], \
                row['buy']/1000, row['sell']/1000, (row['buy']-row['sell'])/1000)

    # log_debug("info:\n%s", info)

    return info

"""
返回基础信息、限售股信息
返回复牌信息 2016-12-25
"""
def get_basic_info_all(_stock_id, _db):
    info = ""

    info += get_basic_info2(_stock_id, _db)

    info += get_fupai_info(_stock_id, _db)

    info += get_dadan_info(_stock_id, _db)

    info += get_rename_info(_stock_id, _db)

    info += get_xsg_info(_stock_id, _db)

    info += get_longhu_info(_stock_id, _db)

    return info


"""
2017/4/16
最后一个交易日期
"""
def get_newest_trade_date(_db):
    sql = "select max(pub_date) pub_date from tbl_day"

    df = pd.read_sql_query(sql, _db);
    if df is None :
        log_error("warn: stock %s last-trade-date is None, next", _stock_id)
        return None

    if df.empty:
        log_error("warn: stock %s last-trade-date is empty, next", _stock_id)
        return None

    newest_date = df.iloc[0, 0]

    if newest_date is not None:
        newest_date = str(newest_date)
        log_info("newest trade date is %s", newest_date)

    return newest_date


"""
指定日期涨幅
"""
def get_day_rate(_stock_id, _pub_date, _db):
    sql = "select round((close_price/last_close_price - 1)*100, 2) rate \
from tbl_day \
where stock_id='%s' and pub_date='%s' \
and last_close_price > 0" % (_stock_id, _pub_date)

    df = pd.read_sql_query(sql, _db);
    if df is None :
        log_error("warn: stock %s,%s is None", _stock_id, _pub_date)
        return -100

    if df.empty:
        log_error("warn: stock %s,%s is empty", _stock_id, _pub_date)
        return -100 

    rate = df.iloc[0, 0]
    return rate


"""
上市天数
"""
def get_day_to_market(_stock_id, _pub_date, _db):
    sql = "select datediff('%s', str_to_date(time_to_market, '%%Y%%m%%d')) days \
from tbl_basic \
where stock_id = '%s'" % (_pub_date, _stock_id)

    df = pd.read_sql_query(sql, _db);
    if df is None :
        log_error("warn: stock %s,%s is None", _stock_id, _pub_date)
        return 10001

    if df.empty:
        log_error("warn: stock %s,%s is empty", _stock_id, _pub_date)
        return 10002 

    days = df.iloc[0, 0]

    if days is None:
        log_error("days is None: %s, %s", _stock_id, _pub_date)
        return 10003 

    return days


"""
是ST
"""
def is_ST(_stock_id):
    name = get_name(_stock_id)
    if name is None:
        log_info("not found, consider not ST")
    else:
        if name.find("ST") != -1:
            log_info("[%s -> %s] is ST", _stock_id, name)
            return 1
        else:
            log_info("[%s -> %s] not ST", _stock_id, name)

    return 0


"""
2017/8/12
最后一个交易日期
"""
def get_newest_index_trade_date(_db):
    sql = "select max(pub_date) pub_date from tbl_index_day"

    df = pd.read_sql_query(sql, _db);
    if df is None :
        log_error("warn: stock %s last-trade-date is None, next", _stock_id)
        return None

    if df.empty:
        log_error("warn: stock %s last-trade-date is empty, next", _stock_id)
        return None

    newest_date = df.iloc[0, 0]

    if newest_date is not None:
        newest_date = str(newest_date)
        log_info("newest trade date is %s", newest_date)

    return newest_date


"""
2017/9/6
"""
def get_stock_list_table_quick(_db):
    sql = "select distinct stock_id from tbl_day where pub_date=(select max(pub_date) from tbl_day) order by 1"

    df = pd.read_sql_query(sql, _db);
    if df is None:
        return None
    else :
        return df.set_index('stock_id')

#######################################################################
if __name__=="__main__":
    sailog_set("saisql.log")
    log_info("main begin here!")

    db = db_init()

    #------------------------------------------------------------------
    """
    stock_id  = "601886"
    stock_id  = "901886"
    last_date = get_last_trade_date(stock_id, db)
    log_debug("last of [%s] is [%s]", stock_id, last_date)

    stock_id  = "600868"
    stock_id  = "900868"
    info = get_basic_info2(stock_id, db)
    log_debug("basic:\n%s", info)

    stock_id  = "601901"
    info = get_basic_info_all(stock_id, db)
    log_debug("all:\n%s", info)

    stock_id  = "000757"
    info = get_fupai_info(stock_id, db)
    log_debug("fupai:\n%s", info)

    stock_id  = "000757"
    info = get_basic_info_all(stock_id, db)
    log_debug("all2:\n%s", info)

    stock_id  = "601668"
    info = get_dadan_info(stock_id, db);
    log_debug("dd: \n%s", info)

    stock_id  = "603768"
    info = get_longhu_info(stock_id, db);
    log_debug("lh: \n%s", info)

    stock_id  = "603768"
    info = get_basic_info_all(stock_id, db);
    log_debug("all: \n%s", info)

    subject = "all-info %s" % (stock_id)
    content = info
    saimail(subject, content)
    """

    stock_id  = "601375"
    pub_date  = "2017-04-23"
    rt = get_day_rate(stock_id, pub_date, db)
    log_info("rate is [%.2f%%]", rt)

    stock_id  = "601375"
    pub_date  = "2017-04-23"
    days = get_day_to_market(stock_id, pub_date, db)
    log_info("days is [%d]", days)

    stock_id  = "000504"
    info = get_basic_info_all(stock_id, db);
    log_debug("all: \n%s", info)

    stock_id  = "000504"
    stock_id  = "600149"
    if is_ST(stock_id):
        log_debug("%s YES", stock_id)
    else:
        log_debug("%s NO", stock_id)

    db_end(db)
    log_info("main ends  bye!")


# saisql.py
