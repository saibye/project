#!/usr/bin/env python
# -*- encoding: utf8 -*-


from sqlalchemy import create_engine

import tushare as ts


print 'begin'

engine = create_engine('mysql://tudev:wangfei@182.92.239.6/tu?charset=utf8')

print 'db connected!'

#df.to_sql('tick_data', engine, if_exists='append')


df = ts.get_sina_dd('600993', date='2016-06-03') # default >=400shou
print df

#df = ts.get_sina_dd('600993', date='2015-12-24', vol=500)  # indicate >= 500

print 'bye'



