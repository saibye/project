#!/usr/bin/env python
# -*- encoding: utf8 -*-


#import tushare as ts
#import pandas as pd
#import numpy as np

from saiutil import *
from saidb   import *
from saisql  import *
from saicalc import *
from sailog  import *
from saimail import *
from sairef  import *
from saitech import *
from saifmt  import *

import saiobj

from stop    import *



def work():
    db = db_init()

    saiobj.g_db = db


    func_map =  saiobj.g_func_map

    txn_name = 'stop'

    if func_map.has_key(txn_name):
        myfunc = saiobj.g_func_map[txn_name]
        myfunc()
    else:
        return 0


    db_end(db)



if __name__=="__main__":
    sailog_set("myrun.log")

    work()

    log_debug("--end")

# myrun.py
