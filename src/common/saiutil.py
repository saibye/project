#!/usr/bin/env python
# -*- encoding: utf8 -*-

import sys
import tushare as ts
import time
import pandas as pd
import numpy as np

from time import strftime, localtime
from datetime import timedelta, date
import datetime
import calendar

from sailog  import *



def get_today():
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    dt = time.strftime("%Y-%m-%d", time.localtime()) 
    return dt

def get_time():
    tm = time.strftime("%H:%M:%S", time.localtime()) 
    return tm 

def get_micro_second():
    tm = time.time() * 1000000
    return tm 

def get_date_by(n=0):
    '''''
    if n>=0,date is larger than today
    if n<0,date is less than today
    date format = "YYYY-MM-DD"
    '''
    if (n<0):
        n = abs(n)
        dt = date.today()-timedelta(days=n)
    else:
        dt = date.today()+timedelta(days=n)

    return str(dt)



def today():
    '''''
    get today,date format="YYYY-MM-DD"
    '''''
    return date.today()


def dai_datetime():
    '''''
    get datetime,format="YYYY-MM-DD HH:MM:SS"
    '''
    return strftime("%Y-%m-%d %H:%M:%S",localtime())

# 2016/8/21
def today_weekday():
    d = datetime.datetime.now()
    return  d.isoweekday()

def today_is_weekend():
    n = today_weekday()
    if n == 6 or n == 7:
        return 1
    else:
        return 0

def check_time_to_run(_time_map):

    to_run = 0

    for item in sorted(_time_map.keys()):
        already_processed = _time_map[item]

        if already_processed:
            #log_debug("[%s] already done, next", item)
            continue

        curr = get_time()
        #log_debug("curr time: %s", curr)

        # reach the time
        if curr >= item:
            _time_map[item] = 1
            to_run = 1
            log_info("nice: trigger: %s > %s", curr, item)

    return to_run

# 此函数只能调用一次 
def get_args():
    sys.argv.pop(0)
    args = sys.argv
    return args


if __name__=="__main__":
    print today()  
    print get_date_by(20)
    print get_date_by(-3)
    if today_is_weekend():
        print "is weekend"
    else:
        print "not"



# saiutil.py
