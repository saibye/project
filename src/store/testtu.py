#!/usr/bin/env python
# -*- encoding: utf8 -*-


from sqlalchemy import create_engine

import tushare as ts

from sailog  import *

print 'begin'


stock_id   = '002709'
start_date = '2016-06-29'
end_date   = '2016-06-30'
minute = '30'

#print ts.get_hist_data('600848',start='2015-01-05',end='2015-01-09')

"""
df = ts.get_hist_data(stock_id, start=start_date, end=end_date, ktype=minute)
print df

length = len(df)

for row_index, row in df.iterrows():
    print "-----------index is ",  row_index
    print "close is ", row.loc['close'], ", ma5 is ", row.loc['ma5'], ", change: ", row['p_change']

print "total row is ", length

#print df['close'].head(5)
print df['close'].head(5).median()
"""

"""
df = ts.get_today_all()
print df.head(5)
"""

"""
df = ts.get_realtime_quotes(['600848','000980','000981'])
print df.head()
"""

stock_id   = '002709'
start_date = '2016-07-20'
end_date   = '2016-07-21'
minute     = '30'

sailog_set("tu.log")

"""
df = ts.get_hist_data(stock_id, start=start_date, end=end_date, ktype=minute)
log_debug(df)
"""


#df = ts.get_today_ticks('000002')

#df = ts.get_today_ticks('300135') # good
#log_debug("\n%s", df[df.volume > 5000]) 

"""
df = ts.get_today_ticks('000839')
log_debug("\n%s", df[df.volume > 1000])
"""

"""
df = ts.get_today_ticks('000002')
log_debug("\n%s", df[df.volume > 10000])

df = ts.get_today_ticks('000002')
log_debug("\n%s", df[df.volume > 10000])

"""

"""
df = ts.get_tick_data('000678',date='2016-08-04')
log_debug("\n%s", df[df.volume > 10000])
"""


"""
df = ts.get_sina_dd('000678', date='2016-08-04', vol=10000) 
log_debug("\n%s", df)

df = ts.get_sina_dd('000002', date='2016-08-04', vol=10000) 
log_debug("\n%s", df)

df = ts.get_sina_dd('002652', date='2016-08-04', vol=1000) 
log_debug("\n%s", df)

df = ts.get_sina_dd('000918', date='2016-08-04', vol=10000)
log_debug("\n%s", df)
"""


df = ts.get_sina_dd('000885', date='2016-08-04', vol=5000)
log_debug("\n%s", df)


# end
