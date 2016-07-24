#!/usr/bin/env python
# -*- encoding: utf8 -*-


from sqlalchemy import create_engine

import tushare as ts


print 'begin'

engine = create_engine('mysql://tudev:wangfei@127.0.0.1/tu?charset=utf8')

print 'db connected!'

#df.to_sql('tick_data', engine, if_exists='append')



df = ts.get_h_data('600993')

print df

#df.to_sql('tbl_h_data', engine, if_exists='append')


print 'bye'



