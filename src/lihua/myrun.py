#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj

from common  import *
from fresh   import *



def work_one(_one, _date, _db):

    func_map =  saiobj.g_func_map
    txn_name = 'fresh'
    if not func_map.has_key(txn_name):
        log_error('error: [%s] no transaction', txn_name)
        return -1

    myfunc = saiobj.g_func_map[txn_name]
    if not callable(myfunc):
        log_error('error: [%s] not callable', txn_name)
        return -1

    sai_fmt_set_fetch_len(saiobj.g_fetched_len)

    #
    df = sai_fmt_simple(_one, _date, _db)
    if df is None:
        log_debug('is none')
        return 0
    elif df.empty:
        log_debug('is empty')
        return 0
    else:
        # log_debug('++')
        pass

    rv = myfunc(_one, _date, df)

    return rv



def work():
    db = db_init()

    sai_load_conf2('wine.cfg')
    saiobj.g_fetched_len = int(sai_conf_get2('wine', 'fetched_len'))

    trade_date = '2018-04-20'

    stock_list = get_stock_list_table_quick(db)

    for one, row in stock_list.iterrows():
        log_debug("-- %s --", one)
        one = '603214'
        work_one(one, trade_date, db)
        break


    db_end(db)



if __name__=="__main__":
    sailog_set("wine.log")

    work()

    log_debug("--end")

# myrun.py
