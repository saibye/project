#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pandas as pd
import tushare as ts

from sailog  import *


"""
print ts.xsg_data()
"""


"""
df = ts.get_stock_basics()
print df
"""

"""
df = ts.profit_data(year='2016', top=90)
df = df.sort_values(by='report_date',ascending=False)
print df
"""

"""
df = ts.get_hist_data('000420')
print df
"""


df = ts.get_h_data('000002', autype='qfq', start='2015-01-01', end='2016-10-30')
for row_index, row in df.iterrows():
    print row

#print df




# test1.py
