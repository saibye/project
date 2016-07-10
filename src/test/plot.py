#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import pandas   as pd
import numpy    as np
import matplotlib.pyplot as plt


ts = pd.Series(np.random.randn(1000), index=pd.date_range('1/1/2000', periods=1000))
ts = ts.cumsum()

#ts.plot()
#plt.show()


df = pd.DataFrame(np.random.randn(1000, 4), index=ts.index, columns=list('ABCD'))
df.cumsum()
#plt.figure()
#df.plot()
#plt.show()

df3 = pd.DataFrame(np.random.randn(1000, 2), columns=['B', 'C']).cumsum()
df3['A'] = pd.Series(list(range(len(df))))
#df3.plot(x='A', y='B')
#plt.show()

#plt.figure();
#df.ix[5].plot(kind='bar'); plt.axhline(0, color='k') # nice
#df.ix[5].plot.bar(); plt.axhline(0, color='k')

df2 = pd.DataFrame(np.random.rand(10, 4), columns=['a', 'b', 'c', 'd'])
#df2.plot.bar()
#df2.plot.bar(stacked=True)
#plt.show()

# box
df = pd.DataFrame(np.random.rand(10, 5), columns=['A', 'B', 'C', 'D', 'E'])
#df.plot.box()
#print df
#plt.show()


# scatter
df = pd.DataFrame(np.random.rand(50, 4), columns=['a', 'b', 'c', 'd'])
# case1: 
#df.plot.scatter(x = 'a', y='b')
#plt.show()
# case2:
#ax = df.plot.scatter(x='a', y='b', color='Orange', label='Group1')
#df.plot.scatter(x='c', y='d', color='DarkGreen', label='Group 2', ax=ax)
#plt.show()
# case3:
#df.plot.scatter(x='a', y='b', s=df['c']*200)
#plt.show()


# pie
series = pd.Series(3 * np.random.rand(4), index=['a', 'b', 'c', 'd'], name='fei')
#series.plot.pie(figsize=(6, 6))
#plt.show()


# kde
ser = pd.Series(np.random.randn(1000))
#ser.plot.kde()
#plt.show()


# lag
from pandas.tools.plotting import lag_plot
plt.figure()
#data = pd.Series(0.0 +
#        0.9 * np.sin(np.linspace(-99*np.pi, 99*np.pi, num=1000)))
#data = pd.Series(0.1 * np.random.rand(1000) +
#        0.9 * np.sin(np.linspace(-99*np.pi, 99*np.pi, num=1000)))
#print data
#lag_plot(data)
#plt.show()















