#!/usr/bin/env python
# -*- encoding: utf8 -*-

from sailog  import *


g_db = None


# fetch N rows from tbl_day
g_fetched_len  = 100

# 0: no ref; 1: ref_close; 2: ref_ma10
g_fmt_mode     = 2


# function map
g_func_map = {}


# fresh
g_fresh_cfg_loaded = False
g_fresh_start_rate = -8
g_fresh_step = 3
g_fresh_step_zt   = -2
g_fresh_step_rate = -4
g_fresh_total_down= -20
g_fresh_total_up  = 40
g_fresh_up_down_rt= 2



if __name__=="__main__":
    sailog_set("saiobj.log")

    log_debug("this is public object")


# saiobj.py
