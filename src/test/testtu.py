#!/usr/bin/env python
# -*- encoding: utf8 -*-


from sqlalchemy import create_engine

import tushare as ts

from sailog  import *
from saiutil import *

import matplotlib.pyplot as plt

def dump_gp(_g):
    for i, j in _g:
        log_debug(i)
        log_debug("-----")
        log_debug(j)

def dump_df(_df, _base):
    log_debug("hello")
    gp = df[df.volume > _base].groupby('type')['volume'].sum()
    log_debug("size is %d", len(gp))
    buy  = 0
    sell = 0
    for s_idx, s_val in gp.iteritems():
        log_debug("--: %s, %s", s_idx, s_val)
        if s_idx == "涔扮洏":
            buy = s_val
        elif s_idx == "鍗栫洏":
            sell = s_val
        else :
            pass

    log_debug("buy: %d;  sell: %d", buy, sell)
    return


def get_buy_sell_rate(_df, _base):
    rate = 0.0

    buy  = 0
    sell = 0

    gp = df[df.volume > _base].groupby('type')['volume'].sum()

    for s_idx, s_val in gp.iteritems():
        if s_idx == "涔扮洏":
            buy = s_val
        elif s_idx == "鍗栫洏":
            sell = s_val
        else :
            pass

    if buy > 0 and sell > 0:
        rate = 1.0 * buy / sell
        
    return rate


def get_rate_list(_df, _list):
    rs = []

    for base in _list :
        rate = get_buy_sell_rate(_df, base)
        rs.append(rate)
        log_debug("base: %d, rate: %.2f", base, rate)

    return rs

def check_df_rates(_df):
    lst = [100, 200, 400, 800, 1000, 2000, 3000]
    exp = [1,   1,   1,   1,   1,    2,    6]
    exp = [2,   2,   2,   2.7, 3.5,  1.5,  1]
    exp = [2,   1.8, 1,   1,   1,    1,    1]
    exp = [2,   2,   2,   2,   1,    1,    1]
    exp = [4,   4,   9,   15,  1,    1,    1]

    rs = get_rate_list(df, lst)

    rank = 0
    idx = 0
    for i in rs:
        if i < 1 and i != 0.0:
            rank = -1
            log_debug("[%d]: buy less than sell, means bad", lst[idx])
            break

        if i > 10:
            rank += 10000
        elif i >= 6:
            rank += 1000
        elif i >= 4:
            rank += 100
        elif i >= 3:
            rank += 10
        elif i >= 2:
            rank += 1

        idx += 1

    return rank


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

"""
# buy
#df = ts.get_sina_dd('000885', date='2016-08-04', vol=5000)
df = ts.get_sina_dd('600606', date='2016-08-15', vol=10000)
log_debug("\n%s", df)
"""

# sell
day     = '2016-08-16'
stock   = '300015' # 鐖卞皵鐪肩 # right
stock   = '600120' # 娴欐睙涓滄柟
stock   = '002142' # 瀹佹尝閾惰

# buy
"""
day     = '2016-08-17'
stock   = '000959' #
stock   = '603028' #
"""

# buy
"""
day     = '2016-08-16'
stock   = '300185' # 閫氳閲嶅伐
stock   = '600705' # 涓埅璧勬湰
stock   = '300459' #
stock   = '002495' #
stock   = '600570' #
stock   = '000978' #

stock   = '002792' #
stock   = '300073' #
stock   = '000585' #
"""

day     = '2016-08-17'
stock   = '002598'
stock   = '002110'
stock   = '300218'
stock   = '000885'
stock   = '000652'
stock   = '600084'
stock   = '002694'
stock   = '000736'

day     = '2016-08-17'
stock   = '600187'

#base = 10000
#df = ts.get_sina_dd(stock, date=day, vol=base)
#df = ts.get_tick_data(stock, date=day)
#df = df.sort_values(by='time')

#df = df.head(1400)

"""
day     = '2016-08-17'
stock   = '000839'
base    = 10000
day     = '2016-08-16'
stock   = '002142'
stock   = '300015'
stock   = '000002'
stock   = '000885'
day     = '2016-08-10'
day     = '2016-08-03'
base    = 100
df = ts.get_sina_dd(stock, date=day, vol=base)
log_debug("head.1:\n%s", df)
"""

"""

#df[df.type == '涔扮洏']['volume'] = 0
#df.loc[df.type=='涔扮洏', 'volume'] = 0
df['buy']  = df['volume']
df['sell'] = df['volume']
df.loc[df.type=='鍗栫洏', 'buy']  = 0
df.loc[df.type=='涔扮洏', 'sell'] = 0
log_debug("head.2:\n%s", df)
df = df.set_index('time').sort_index()
kk = df.loc[:, ['buy', 'sell']].cumsum()
#kk.plot()
kk.buy.plot(color='r')
kk.sell.plot(color='g')
log_debug("kk.2:\n%s", kk)
plt.show()


exit()

base  = 10
log_debug("%d:\n%s", base, df[df.volume > base].groupby('type')['volume'].sum())

base  = 50
log_debug("%d:\n%s", base, df[df.volume > base].groupby('type')['volume'].sum())

base  = 100
log_debug("%d:\n%s", base, df[df.volume > base].groupby('type')['volume'].sum())

base  = 200
log_debug("%d:\n%s", base, df[df.volume > base].groupby('type')['volume'].sum())

base  = 400
log_debug("%d:\n%s", base, df[df.volume > base].groupby('type')['volume'].sum())

base  = 800
log_debug("%d:\n%s", base, df[df.volume > base].groupby('type')['volume'].sum())

base  = 1000
log_debug("%d:\n%s", base, df[df.volume > base].groupby('type')['volume'].sum())

base  = 2000
log_debug("%d:\n%s", base, df[df.volume > base].groupby('type')['volume'].sum())

base  = 3000
log_debug("%d:\n%s", base, df[df.volume > base].groupby('type')['volume'].sum())

base  = 5000
log_debug("%d:\n%s", base, df[df.volume > base].groupby('type')['volume'].sum())

rank = check_df_rates(df)
log_debug("rank: %d", rank)
"""

def rt_dadan_check_sell(_stock_id, _df, _vol_base, _count_base, _price):

    good = 0

    buy  = "涔扮洏"
    sell = "鍗栫洏"

    con1 = 0

    subject = ""
    body    = ""

    stock_id  = _stock_id

    for row_index, row in _df.iterrows():
        direction = row['type']
        volume    = row['volume']
        tm        = row['time']
        price     = row['price']


        if volume >= _vol_base:
            if direction == sell:
                con1 = con1 + 1
                log_info("杩炵画sell: [%d, %s, %d, %s]", con1, tm, volume, direction)
            else :
                con1 = 0
                log_info("鏈塨uy鐩