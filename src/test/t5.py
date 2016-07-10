#!/usr/bin/env python
# -*- encoding: utf8 -*-


from sqlalchemy import create_engine

import tushare as ts


print 'begin'

df = ts.get_today_all()
print df


#df.plot(title='close price')

#print 'bye'



