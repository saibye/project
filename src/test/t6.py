#!/usr/bin/env python
# -*- encoding: utf8 -*-


from sqlalchemy import create_engine

import tushare as ts


print 'begin'

engine = create_engine('mysql://tudev:wangfei@127.0.0.1/tu?charset=utf8')

print 'db connected!'

#df.to_sql('tick_data', engine, if_exists='append')

# tick
df = ts.get_tick_data('600993', date='2016-06-02')
print df.head(10)


df = ts.get_today_ticks('600993')
print df.head(10)

"""
# real time !!!
df = ts.get_realtime_quotes('600993') #Single stock symbol
print df[['code','name','price','bid','ask','volume','amount','time']]

# shanghai
print ts.get_realtime_quotes('sh')

# ...
print ts.get_realtime_quotes(['sh','sz','hs300','sz50','zxb','cyb'])

# or mixed
print ts.get_realtime_quotes(['sh','600993'])
"""

print 'bye'



