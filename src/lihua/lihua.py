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
# lihua import from excel
#######################################################################

def import_from_excel(_year, _file_name, _db):

    log_info("")

    sheet_name = ''

    for mon in range(12):
        sheet_name = '%s-%s' % (_year, mon+1)
        log_debug('sheet: %s', sheet_name)
        import_from_excel_sheet(_file_name, sheet_name, _db)


    return 0


def import_from_excel_sheet(_file_name, _sheet_name, _db):

    log_info("")


    res_dir = '%s/project/res' % os.getenv('HOME')
    log_debug("dir: [%s]", res_dir)

    file_path  = '%s/%s' % (res_dir, _file_name)
    log_debug("path: [%s]", file_path)

    #sheet_name = '1975-1'

    # df = pd.read_excel(file_path, index_col=None, header=None, sheet_name=sheet_name)
    # df = pd.read_excel(file_path, index_col=0, sheet_name=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    df = pd.read_excel(file_path, index_col=0, sheet_name=_sheet_name)
    log_debug(df)

    date = ''
    close_price = 0.0
    deal_price  = 0.0
    action      = ''
    position    = ''

    for idx, row in df.iterrows():
        date = idx.date()
        close_price = row['收盘价']
        deal_price  = row['成交价']
        action      = row['买卖']
        position    = row['未平仓']

        log_debug('[%s], [%s], [%s], [%s], [%s]', date, close_price, deal_price, action, position)

        if np.isnan(close_price):
            log_debug('[%s] is not in market3 [%s]', date, close_price)
            continue

        if np.isnan(deal_price):
            log_debug('keep: [%s]', date)
            sql = "insert into tbl_lihua_day (pub_date, close_price) "\
                    "values ('%s', '%s')" % (date, close_price)
        else:
            log_debug('deal: [%s]', date)
            sql = "insert into tbl_lihua_day (pub_date, close_price, deal_price, action, position) values " \
                  "('%s', '%s', '%s', '%s', '%s')" % (date, close_price, deal_price, action, position)

        log_debug('[%s]', sql)

        rv = sql_to_db_nolog(sql, _db)
        if rv != 0:
            log_error("error: sql_to_db %s", sql)

    return 0


def work():
    db = db_init()

    year = '1975'
    year = '1976'

    file_name  = 'gs%s.xlsx' % (year)

    import_from_excel(year, file_name, db)

    db_end(db)


#######################################################################

def main():
    sailog_set("lihua_import.log")

    log_info("let's begin here!")

    work()

    log_info("main ends, bye!")
    return

main()

#######################################################################


#
