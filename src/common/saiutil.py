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
import json


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

def get_year():
    dt = time.strftime("%Y", time.localtime()) 
    return str(dt)


'''
    if n>=0,date is larger than today
    if n<0,date is less than today
    date format = "YYYY-MM-DD"
'''
def get_date_by(n=0):
    if (n<0):
        n = abs(n)
        dt = date.today()-timedelta(days=n)
    else:
        dt = date.today()+timedelta(days=n)

    return str(dt)



'''''
get today,date format="YYYY-MM-DD"
'''''
def today():
    return date.today()



'''''
get datetime,format="YYYY-MM-DD HH:MM:SS"
'''
def dai_datetime():
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


def sai_analyze_system_config():
    system_config = "%s/sai.conf" % os.getenv('HOME')
    if os.path.isfile(system_config):
        json_file_fd = open(system_config)
        return json.load(json_file_fd)
    else :
        log_error("system_config[%s] 错误!", system_config)
        return -1


def sai_is_product_mode():
    product_mode = 1
    system_json = sai_analyze_system_config()
    if system_json == -1:
        log_error("error: no config, default production mode")
        return True

    product_mode =  system_json['instance']['product_mode']
    log_debug("product_mode: [%s]", product_mode)
    return (product_mode == "1")


if __name__=="__main__":
    sailog_set("saiutil.log")
    print(today())
    print(get_date_by(20))
    print(get_date_by(-3))

    if today_is_weekend():
        print("is weekend")
    else:
        print("not")

    if sai_is_product_mode():
        log_debug("is  product mode")
    else:
        log_debug("NOT product mode")


# saiutil.py
