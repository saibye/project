#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import pandas   as pd
import numpy    as np
import matplotlib.pyplot as plt
import seaborn  as sns


sns.set(style='ticks')

df = sns.load_dataset("anscombe")

# Show the results of a linear regression within each dataset
#sns.lmplot(x="x", y="y", col="dataset", hue="dataset", data=df,
#        col_wrap=2, ci=None, palette="muted", size=4, 
#        scatter_kws={"s": 50, "alpha": 1})


# Load one of the data sets that come with seaborn
tips =sns.load_dataset("tips")
     
print tips.dtypes
#print tips

#sns.jointplot("total_bill","tip",tips,kind='reg');

#sns.lmplot("total_bill","tip",tips,col="smoker");

#plt.show()




