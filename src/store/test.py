#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pandas as pd
import tushare as ts


v = "a"

print v

def fun(_v):
    v  = 'b'
    _v = 'c'

fun(v)
print v

s1 = pd.Series(0, index=range(10))

s1[0] = 'x'
print s1

print ts.xsg_data()

#df = ts.profit_data(top=60)
#print df.sort('shares',ascending=False)

df = ts.get_stock_basics()
print df


# test.py
