#!/usr/bin/env python
# -*- encoding: utf8 -*-


from sqlalchemy import create_engine

import tushare as ts



import pandas as pd
import numpy  as np
import matplotlib.pyplot as plt


s = pd.Series([1,3,5, np.nan, 6, 8])

dates  = pd.date_range('20160601', periods=6)


df = pd.DataFrame(np.random.randn(6, 4), index=dates, columns=list('ABCD'))


df2 = pd.DataFrame({ 'A': 1.,
      'B': pd.Timestamp('20160605'),
      'C': pd.Series(1, index=list(range(4)), dtype='float32'),
      'D': np.array([3] * 4, dtype='int32'),
      'E': pd.Categorical(["test", "train", "test", "train"]),
      'F': 'foo' })

df2.dtypes

df2.head()

df2.tail(3)


df.index
df.columns
df.values


df.describe()


df.T()

df.sort_index(axis=1, ascending=False)

df.sort_values(by='B')













