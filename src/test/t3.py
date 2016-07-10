#!/usr/bin/env python
# -*- encoding: utf8 -*-


from sqlalchemy import create_engine

import tushare as ts


print 'begin'

engine = create_engine('mysql://tudev:wangfei@182.92.239.6/tu?charset=utf8')

print 'db connected!'

#df.to_sql('tick_data', engine, if_exists='append')

df = ts.get_stock_basics()
print df

date = df.ix['600993']['timeToMarket'] # 
print date

#df.to_sql('tbl_hist_data', engine, if_exists='append')


print 'bye'



