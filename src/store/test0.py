#!/usr/bin/env python
# -*- encoding: utf8 -*-


from sqlalchemy import create_engine
import tushare as ts
import MySQLdb
import time
import pandas as pd
import numpy as np

from saiutil import *
from saidb   import *
from saisql  import *
from saicalc import *
from sailog  import *

#######################################################################


stock_id    = '002709'
stock_id    = '300028'
start_date  = '2016-07-20'
end_date    = '2016-07-22'
minute      = '30'




def prototype(_stock_id):
    print "work_prototype begin"

    df = ts.get_hist_data(_stock_id, start=start_date, end=end_date, ktype=minute)

    if df is None :
        print "is none"
    else :
        print "not none"

    length = len(df)
    print "total row is ", length

     #clear_stock_from_db(_stock_id, db)
     #df_to_db(df, db)
    sma(df, 5)
    sma(df, 10)
    sma(df, 20)
    sma(df, 30)
    sma(df, 60)
    sma(df, 150)

    s1 = ema(df, 12)
    df['ema12'] = s1

    s2 = ema(df, 26)
    df['ema26'] = s2

    s3 = diff(df, 12, 26)
    df['diff'] = s3

    s4 = dea(df, 9)
    df['dea'] = s4

    print df.sort_index(ascending=True)

    print "work_prototype end"

    return 

#######################################################################

def main():
    print "let's begin here!"

    prototype(stock_id)

    print "main ends, bye!"
    return

main()
exit()
print "can't arrive here"

#######################################################################


# test0.py
