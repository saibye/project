#!/usr/bin/env python
# -*- encoding: utf8 -*-


from sqlalchemy import create_engine
import tushare as ts


print 'begin'

engine = create_engine('mysql://tudev:wangfei@127.0.0.1/tu?charset=utf8')

print 'db connected!'

df = ts.get_tick_data('600993', date='2016-06-02')

#print df

# create table and insert data
#df.to_sql('tick_data',engine)

print 'middle'

df.to_sql('tick_data', engine, if_exists='append')

print 'bye'

