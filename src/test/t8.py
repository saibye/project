#!/usr/bin/env python
# -*- encoding: utf8 -*-


from sqlalchemy import create_engine

import tushare as ts


print 'begin'

df = ts.get_realtime_quotes('002709') 
print df[['code','name','price','bid','ask','volume','amount', 'date', 'time']]

#print df

print 'bye'



