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

#######################################################################


def work(_args):
    db = db_init()

    if len(_args) == 1:
        holder = _args[0]
    else:
        holder = 'sai'

    dt = get_today()
    tm = get_time()

    sql = "update tbl_real_trade set is_valid = '0' where holder = '%s'" % holder
    log_info("%s", sql)

    sql_to_db_nolog(sql, db)

    db_end(db)


#######################################################################

def main():
    sailog_set("clear_bought.log")

    log_info("main begins")

    saimail_init()

    args = get_args()

    work(args)

    log_info("main ends, bye!")
    return

main()
exit()

#######################################################################

# clear_bought.py
