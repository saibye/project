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
# ST摘帽
# stXX --> XXYY
#######################################################################




"""
2016-12-25
insert into tbl_name ( 
stock_id, stock_old_name, stock_new_name,
inst_date, inst_time) 
values ('000504', '*ST生物', '南华生物', '2017-05-29', '09:41:00'); 
"""
def name_record_to_db(_stock_id, _old_name, _new_name, _work_date, _db):
    tm = get_time()
    sql = "insert into tbl_name (  \
stock_id, stock_old_name, stock_new_name, \
inst_date, inst_time)  \
values ('%s', '%s', '%s', '%s', '%s')" % (_stock_id, _old_name, _new_name, _work_date, tm)

    log_debug("sql: \n%s", sql)

    rv = sql_to_db_nolog(sql, _db)
    if rv != 0:
        log_error("error: record fupai: %s", sql)

    return rv


def work_one(_stock_id, _name, _work_date, _db):

    log_info("work_one [%s, %s] begin", _stock_id, _name)

    begin = get_micro_second()

    # new name
    name = get_name(_stock_id)

    if name.find("ST") != -1:
        log_info("new name still keeps bad1")
        return None

    if name.find("退") != -1:
        log_info("new name still keeps bad2")
        return None

    if name != _name:
        log_info("nice: %s [%s => %s]", _stock_id, _name, name)
        name_record_to_db(_stock_id, _name, name, _work_date, _db)
    else:
        log_info("old name")
        name = None

    log_debug("it costs %d us", get_micro_second() - begin)

    return name


def name_check_to_notice(_work_date, _db):

    sql = "select * from tbl_name where inst_date = '%s'" %(_work_date)
    log_info("sql: %s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("'%s' not found in db", _stock_id)
        return -1
    else:
        log_info("got data: %d lines", len(df))

    content = ""
    for row_index, row in df.iterrows():
        stock_id = row['stock_id']
        old_name = row['stock_old_name']
        new_name = row['stock_new_name']
        one  = "%s 摘帽 [%s] => [%s] (%s)\n" % (stock_id, old_name, new_name, _work_date)
        info = get_basic_info_all(stock_id, _db)
        one += info
        one += "++++++++++++++++++++++++++++++++++++++++\n"
        log_debug("\n%s", one)
        content += one

    if len(content) > 0:
        subject = "rename: %s" % (_work_date)
        log_debug("mail: %s", subject)
        log_debug("\n%s", content)
        if sai_is_product_mode():
            saimail(subject, content)
        else:
            pass
            # saimail(subject, content)


def xxx(_db):

    work_date = get_today()

    basic = get_stock_list_df_tu()
    if basic is None:
        log_debug("error: get_stock_list_df_tu failure")
        return -1

    content = ""
    for row_index, row in basic.iterrows():
        stock_id = row_index
        name = row['name']
        if name.find("ST") != -1:
            log_info("special treatment: [%s, %s]", stock_id, name)
            new = work_one(stock_id, name, work_date, _db)
        else:
            pass

    name_check_to_notice(work_date, _db)

    return 0


def work():
    db = db_init()

    xxx(db)

    db_end(db)


#######################################################################

def main():
    sailog_set("name.log")

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


# name.py
