#!/usr/bin/env python
# -*- encoding: utf8 -*-

import tushare as ts
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

from saiutil import *
from saidb   import *
from saisql  import *
from saicalc import *
from sailog  import *
from saimail import *

#######################################################################


def work(_args):
    db = db_init()

    dt = get_today()
    tm = get_time()

    df = ts.get_stock_basics()

    se = pd.Series(dt, df.index)

    engine = create_engine('mysql://tudev:wangfei@127.0.0.1/tu?charset=utf8')
    df.to_sql('tbl_kkk', engine)

    db_end(db)


#######################################################################

def main():
    sailog_set("import_basic.log")

    log_info("main begins")

    saimail_init()

    args = get_args()

    work(args)

    log_info("main ends, bye!")
    return

main()
exit()

#######################################################################

# import_basic.py
