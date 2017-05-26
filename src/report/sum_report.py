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
from saitu   import *


"""
策略：
"""
#######################################################################


def simple_create_html_begin(_date):
    head = """\
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>盘末统计</title>
<body>
<div id="container">
<p><strong>贪婪与恐惧，一天又一天</strong> </p>
<p><strong>""" + _date +"""</strong></p>
<div id="content">"""

    return head

def simple_create_html_end():

    end="""\
</div>
</div>
</body>
</html>"""

    return end


def sum_report_first(_recent_date, _db):

    sql = "select pub_date, (sum(buy1)-sum(sell1))/10000 N1, sum(buy1)/10000 B1, sum(sell1)/10000 S1, sum(mid1)/10000 M1 \
from tbl_tick_sum \
where pub_date <='%s' \
group by pub_date \
order by 1 desc limit 10" % (_recent_date)

    log_debug("sql: %s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("query tick_sum failure: %s", _recent_date)
        return ""
    elif df.empty:
        log_debug("df is empty: [%d]", len(df))
        return ""
    else:
        pass
        log_debug("nice: sum tick [%d]", len(df))

    log_debug("df:\n%s", df)

    table = """\
<table width="500" border="1" bordercolor="red" cellspacing="1">
<tr>
  <td><strong>日期</strong></td>
  <td><strong>净</strong></td>
  <td><strong>买</strong></td>
  <td><strong>卖</strong></td>
  <td><strong>中</strong></td>
</tr>"""

    for row_index, row in df.iterrows():
        log_info("row_index: [%s]", row_index)
        one = "<tr>\
<td> %s </td>\
<td> %.0f </td>\
<td> %.0f </td>\
<td> %.0f </td>\
<td> %.0f </td>\
</tr>" % (row['pub_date'], row['N1'], row['B1'], row['S1'], row['M1'])
        table += one

    end="</table>"
    table += end 

    log_debug("table:\n%s", table)

    return table


def sum_report_second(_date, _db):

    sql = "select (sum(buy1)-sum(sell1))/10000 N1, sum(buy1)/10000 B1, sum(sell1)/10000 S1, sum(mid1)/10000 M1, \
(sum(buy1000)-sum(sell1000))/10000 N2, sum(buy1000)/10000 B2, sum(sell1000)/10000 S2, sum(mid1000)/10000 M2, \
(sum(buy3000)-sum(sell3000))/10000 N3, sum(buy3000)/10000 B3, sum(sell3000)/10000 S3, sum(mid3000)/10000 M3, \
(sum(buy10000)-sum(sell10000))/10000 N4, sum(buy10000)/10000 B4, sum(sell10000)/10000 S4, sum(mid10000)/10000 M4 \
from tbl_tick_sum \
where pub_date ='%s'" % (_date)

    log_debug("sql: %s", sql)

    df = pd.read_sql_query(sql, _db);
    if df is None:
        log_info("query tick_sum failure: %s", _date)
        return ""
    elif df.empty:
        log_debug("df is empty: [%d]", len(df))
        return ""
    elif df.iloc[0, 0] is None:
        log_debug("df is empty2: [%d]", len(df))
        return ""
    else:
        pass
        log_debug("nice: sum tick [%d]", len(df))

    log_debug("df:\n%s", df)

    table = ""
    table += """<table width="500" border="1" bordercolor="red" cellspacing="1">"""
    table += """<tr>
<td><strong>粒度</strong></td>
<td><strong>净</strong></td>
<td><strong>买</strong></td>
<td><strong>卖</strong></td>
<td><strong>中</strong></td>
</tr>"""

    for row_index, row in df.iterrows():
        one = "<tr><td> 400 </td><td> %.0f </td><td> %.0f </td><td> %.0f </td><td> %.0f </td></tr>" %\
    (row['N1'], row['B1'], row['S1'], row['M1'])
        two = "<tr><td> 1000 </td><td> %.0f </td><td> %.0f </td><td> %.0f </td><td> %.0f </td></tr>" %\
    (row['N2'], row['B2'], row['S2'], row['M2'])
        three = "<tr><td> 3000 </td><td> %.0f </td><td> %.0f </td><td> %.0f </td><td> %.0f </td></tr>" %\
    (row['N3'], row['B3'], row['S3'], row['M3'])
        four = "<tr><td> 10000 </td><td> %.0f </td><td> %.0f </td><td> %.0f </td><td> %.0f </td></tr>" %\
    (row['N4'], row['B4'], row['S4'], row['M4'])
        table += one + two + three + four
        table += "</table>"
        break

    log_debug("table2:\n%s", table)

    return table


# 收盘后 报表
def sum_report_all(_date, _db):

    content = ""

    head = simple_create_html_begin(_date)
    content += head

    # 1. 当日
    table = sum_report_second(_date, _db)
    if len(table) <= 0:
        log_error("error: sum_report_second")
    else:
        log_debug("nice:  succeed")

    content += table
    content += "<p></p>"

    # 2. 最近5日
    table = sum_report_first(_date, _db)
    if len(table) <= 0:
        log_error("error: sum_report_first")
    else:
        log_debug("nice:  succeed")

    content += table


    end=simple_create_html_end()
    content += end 


    log_debug("content:\n%s", content)

    subject = "盘末统计%s" % (_date)
    saimail_html(subject, content)

    return 0


def sum_report_unit_test(_db):
    global g_inst_date
    global g_inst_time

    buy  = 0
    sell = 0
    mid  = 0

    stock_id   = "600016"
    stock_id   = "601003"
    trade_date = "2017-05-05"

    rv = sum_report_first(stock_id, trade_date, _db)
    if rv != 0:
        log_error("error: sum_report_first")
    else:
        log_debug("nice:  sum succeeds")

    return 0


def work():

    db = db_init()

    # sum_report_unit_test(db)

    trade_date = "2017-05-05"
    trade_date = get_today()

    rv = sum_report_all(trade_date, db)
    if rv:
        log_error("error: sum_report_all")

    db_end(db)


#######################################################################

def main():
    sailog_set("sum_report.log")

    log_info("------------------------------------------------")

    if sai_is_product_mode():
        # check holiday
        if today_is_weekend():
            log_info("today is weekend, exit")
            # work()
        else:
            log_info("today is workday, come on")
            work()
    else:
        log_info("test mode, come on")
        work()


    log_info("main ends, bye!")
    return

main()

#######################################################################

# sum_report.py
