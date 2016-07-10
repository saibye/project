#!/usr/bin/env python
# -*- encoding: utf8 -*-


from sqlalchemy import create_engine
import tushare as ts


print 'begin'

dt = '2016-06-08'
dt = '2016-06-07'
dt = '2016-06-06'

#df = ts.get_tick_data('002709', date='2016-06-08')
#df = ts.get_tick_data('002709', date='2016-06-07')
#df = ts.get_tick_data('002709', date='2016-06-06')
#df = ts.get_tick_data('002709', date='2016-06-03')

#df = ts.get_tick_data('002709', date=dt)

dt = '2015-11-13'
dt = '2015-12-01'
dt = '2015-12-07'
dt = '2015-11-30'
dt = '2015-12-18'
dt = '2015-12-02'
df = ts.get_tick_data('000002', date=dt)


print 'middle'
#print df

#n = 1000
#df2 = df.tail(n).head(n-1);
df2 = df[df.volume < 100]
df2 = df

#print df2

print df2.groupby('type').sum()

exit()
print exit

df3 = ts.get_sina_dd('002709', date=dt)
print df3.groupby('type').sum()


print 'xxx'

print ts.get_sina_dd('002709', date='2016-06-08').groupby('type').sum()
print ts.get_sina_dd('002709', date='2016-06-07').groupby('type').sum()
print ts.get_sina_dd('002709', date='2016-06-06').groupby('type').sum()

print 'yyy'

print ts.get_sina_dd('002709', date='2016-06-03').groupby('type').sum()
print ts.get_sina_dd('002709', date='2016-06-02').groupby('type').sum()
print ts.get_sina_dd('002709', date='2016-06-01').groupby('type').sum()
print ts.get_sina_dd('002709', date='2016-05-31').groupby('type').sum()
print ts.get_sina_dd('002709', date='2016-05-30').groupby('type').sum()

print 'zzz'

print ts.get_sina_dd('002709', date='2016-05-19').groupby('type').sum()
print ts.get_sina_dd('002709', date='2016-05-20').groupby('type').sum()

print 'aaa'
print ts.get_sina_dd('002709', date='2016-05-23').groupby('type').sum()
print ts.get_sina_dd('002709', date='2016-05-24').groupby('type').sum()
print ts.get_sina_dd('002709', date='2016-05-25').groupby('type').sum()
print ts.get_sina_dd('002709', date='2016-05-26').groupby('type').sum()
print ts.get_sina_dd('002709', date='2016-05-27').groupby('type').sum()

print 'bye'

