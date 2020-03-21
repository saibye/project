#!/usr/bin/env python
# -*- encoding: utf8 -*-

from sailog  import *

g_db = None

g_debug = 'no'


# fetch N rows from tbl_day
g_fetch_len = 100

# 0: no ref; 1: ref_close; 2: ref_ma10
g_fmt_mode  = 2

# 0: no mail; 1: send mail
g_to_send_mail = False

# function map
g_func_map = {}

# 
g_mail_sep = '/_'*20 + '/\n'

g_subject_prefix = ''


# fresh
g_wine_cfg_loaded = False
g_wine_start_rate = -8
g_wine_step = 3
g_wine_step_zt   = -2
g_wine_step_up  = 10
g_wine_step_down= 5
g_wine_step_rate = -4
g_wine_total_down= -20
g_wine_total_up  = 40
g_wine_up_down_rt= 2
g_wine_stage     = 5
g_wine_gap       = 4


g_wine_last_rate = -8
g_wine_last_zt   = -8
g_wine_vr5       = 2
g_wine_vr10      = 2
g_wine_vr50      = 5
g_wine_last_rate = -8
g_wine_last_rate = -8
g_wine_open_rate = -9
g_wine_gap_rate  = -3


g_wine_vol_break = 50
g_wine_pri_break = 30
g_wine_lower_edge= -2
g_wine_upper_edge= 8


# 2020-3-11
g_photo_dir = '/tmp'
g_plot_len = 400

g_photo_suffix = '.png'



if __name__=="__main__":
    sailog_set("saiobj.log")

    log_debug("this is public object")


# saiobj.py
