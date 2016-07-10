#!/usr/bin/env python
# -*- encoding: utf8 -*-


from sqlalchemy import create_engine

import tushare as ts


print 'begin'

#df = ts.get_hist_data('600993')
#df = ts.get_hist_data('002709')
#print df.head(1)

df = ts.get_hist_data('002709', ktype='30')
print df.head(1)


print 'bye'



