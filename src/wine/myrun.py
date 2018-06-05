#!/usr/bin/env python
# -*- encoding: utf8 -*-

import saiobj
from common  import *
from pub     import *

from fresh   import *
from two     import *
from san     import *

from stop    import *

from skip    import *

from sixc    import *


def my_work_one_day_stock(_txn_list, _one, _date, _db):
    rv = 0

    #
    sai_fmt_set_fetch_len(saiobj.g_fetch_len)

    #
    df = sai_fmt_simple(_one, _date, _db)
    if df is None:
        log_debug('is none')
        return 0
    elif df.empty:
        log_debug('is empty')
        return 0
    else:
        # log_debug('length(detail(%s)): %d', _one, len(df))
        pass

    for txn_name in _txn_list:
        myfunc = saiobj.g_func_map[txn_name]
        rv += myfunc()

    return rv


def my_is_valid(_txn_list):

    if len(_txn_list) == 0:
        print('error: txn-list is empty')
        return False

    for one in _txn_list:
        if not saiobj.g_func_map.has_key(one):
            print('error: txn [%s] not found' % one)
            log_error('error: [%s] no transaction', one)
            return False

        somefunc = saiobj.g_func_map[one]
        if not callable(somefunc):
            log_error('error: [%s] not callable', one)
            return False

    log_debug('nice: txn verified')

    return True


def my_get_txn_list(_txns):
    txn_list = _txns.split(',')
    for i in range(len(txn_list)):
        txn_list[i] = txn_list[i].strip()

    return txn_list


def my_get_trade_date(_trade_date):

    trade_date = ''

    if len(_trade_date) == 0:
        trade_date = get_date_by(-1)
    elif _trade_date[0] == '-':
        offset = int(_trade_date)
        trade_date = get_date_by(offset)
    else:
        log_debug('think [%s] as a date', _trade_date)
        trade_date = _trade_date

    return trade_date




def my_work_one_day(_date, _stock_list, _txn_list, _db):

    # log_debug('my_work_one_day begin')

    for one, row in _stock_list.iterrows():
        # one = '002930'
        log_debug("-- %s --", one)
        my_work_one_day_stock(_txn_list, one, _date, _db)
        # break

    # log_debug('my_work_one_day end')
    return 0


def regression():
    sailog_set("re.log")
    log_debug('this is regression mode')


    saiobj.g_to_send_mail = True

    txns = sai_conf_get2('regression', 'case')
    txn_list = my_get_txn_list(txns)
    log_debug('txn-list: %s', txn_list)

    # txn_list ==> functions
    if not my_is_valid(txn_list):
        print('error: invalid case: %s' % (case_name))
        log_error('error: invalid case: %s', case_name)
        return 1

    saiobj.g_fetch_len = int(sai_conf_get2('regression', 'fetch_len'))
    log_debug('want fetch_len: [%d]', saiobj.g_fetch_len)

    till_date = sai_conf_get2('regression', 'till_date')
    till_date = my_get_trade_date(till_date)
    log_debug('till_date: [%s]', till_date)

    days = int(sai_conf_get2('regression', 'days'))
    log_debug('days: [%d]', days)

    db = db_init()
    saiobj.g_db = db

    date_df = get_recent_pub_date(till_date, days, db)
    if date_df is None:
        log_error("error: get_recent_pub_date failure")
        return -1
    else:
        date_df.set_index("pub_date", inplace=True)

    stock_list = get_stock_list_table_quick(db)

    for row_index, row in date_df.iterrows():
        trade_date = row_index
        log_debug("regression-trade_date -----[%s]-----", trade_date)
        my_work_one_day(trade_date, stock_list, txn_list, db)

    db_end(db)


def work():

    #
    args = get_args()
    if len(args) == 0:
        print('usage')
        print('python %s case-name' % (__file__))
        case_name = 'all'
    else:
        case_name = args[0]

    sai_load_conf2('wine.cfg')

    # check is-regressoin ?
    if case_name == 're':
        regression()
        return 0

    # casename ==> txn_list
    txns = sai_conf_get2('case', case_name)
    txn_list = my_get_txn_list(txns)
    log_debug('txn-list: %s', txn_list)

    # txn_list ==> functions
    if not my_is_valid(txn_list):
        print('error: invalid case: %s' % (case_name))
        log_error('error: invalid case: %s', case_name)
        return 1

    saiobj.g_fetch_len = int(sai_conf_get2('boot', 'fetch_len'))
    log_debug('want fetch_len: [%d]', saiobj.g_fetch_len)

    trade_date = sai_conf_get2('boot', 'trade_date')
    trade_date = my_get_trade_date(trade_date)
    log_debug('trade_date: [%s]', trade_date)

    to_mail = sai_conf_get2('boot', 'mail')
    if to_mail == '1':
        saiobj.g_to_send_mail = True

    db = db_init()
    saiobj.g_db = db

    stock_list = get_stock_list_table_quick(db)

    my_work_one_day(trade_date, stock_list, txn_list, db)

    db_end(db)


if __name__=="__main__":
    sailog_set("wine.log")

    work()

    log_debug("--end")

# myrun.py
