#!/usr/bin/env python
# -*- encoding: utf8 -*-

import tushare as ts
import time
import pandas as pd
import numpy as np

from time import strftime, localtime
from datetime import timedelta, date
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


def datetime():
    '''''
    get datetime,format="YYYY-MM-DD HH:MM:SS"
    '''
    return strftime("%Y-%m-%d %H:%M:%S",localtime())


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


if __name__=="__main__":
    print today()  
    print datetime()
    print get_date_by(20)
    print get_date_by(-3)



# saiutil.py
