#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *
from pub    import *


# 次新
# code at 2018-5-12
# 几乎连续三个跌停
# 300624 万兴科技 2018-5-12
"""
     u
    u  d 
   u    d 
  u      d
 u
u
"""

def fresh_load_cfg():
    saiobj.g_wine_start_rate= float(sai_conf_get2('fresh', 'start_rate'))
    saiobj.g_wine_step      = int(sai_conf_get2('fresh', 'find_step'))
    saiobj.g_wine_step_zt   = float(sai_conf_get2('fresh', 'green_zt'))
    saiobj.g_wine_step_rate = float(sai_conf_get2('fresh', 'green_rate'))
    saiobj.g_wine_total_down= float(sai_conf_get2('fresh', 'total_down'))
    saiobj.g_wine_total_up  = float(sai_conf_get2('fresh', 'total_up'))
    saiobj.g_wine_up_down_rt= float(sai_conf_get2('fresh', 'up_down_rate'))
    saiobj.g_wine_cfg_loaded= True
    log_debug('fresh config loaded')



def fresh_run():
    body = ''

    stock_id  = ref_id(0)
    this_date = ref_date(0)

    log_debug('TRAN fresh: %s -- %s', stock_id, this_date)

    length = ref_len()
    if length > 30:
        log_debug('%s too long: %d', stock_id, length)
        return 0
    body += '次新天数: %d\n' % (length)

    if not saiobj.g_wine_cfg_loaded:
        fresh_load_cfg()

    rate = 100.00 * (ref_close(0) - ref_close(1)) / ref_close(1)
    log_info("rate: %.2f%%", rate)
    zt   = 100.00 * (ref_close(0) - ref_open(0))  / ref_close(1)
    log_info("zt:   %.2f%%", zt)

    START_RATE = saiobj.g_wine_start_rate
    if rate > START_RATE:
        log_info('start rate not match: %.2f%% > %.2f%%', rate, START_RATE)
        return 0

    step = saiobj.g_wine_step
    log_debug('step: %d', step)

    start = 0+1
    k2 = wine_find_previous_green(start, step)
    if k2 == 0:
        log_info('not found k2')
        return 0
    else:
        log_info('got k2 -- %d', k2)

    start = k2+1
    k3 = wine_find_previous_green(start, step)
    if k3 == 0:
        log_info('not found k3')
        return 0
    else:
        log_info('got k3 -- %d', k3)

    if k3+1 >= length:
        log_info('k3 -- %d', k3)
        return 0

    TOTAL_DOWN = saiobj.g_wine_total_down
    total_down = 100.00 * (ref_close(0) - ref_close(k3+1)) / ref_close(k3+1)
    log_info('down-rate -- %.2f --> %.2f =  %.2f%%', ref_close(k3+1), ref_close(0), total_down)
    if total_down > TOTAL_DOWN:
        log_error('error: total-rate not matched: %.2f', total_down)
        return 0
    body += '累计跌幅: %.2f%%\n' % (total_down)

    start = k3+1
    min_close = wine_find_total_up(start, 7)
    if min_close > 1000:
        log_error('error: invalid min-close: %.2f', min_close)
        return 0
    total_up = 100.00 * (ref_close(k3+1) - min_close) / min_close
    body += '累计上升: %.2f%%\n' % (total_up)
    TOTAL_UP = saiobj.g_wine_total_up
    log_info('up-rate -- %.2f --> %.2f =  %.2f%%', min_close, ref_close(k3+1), total_up)
    if total_up > TOTAL_UP and abs(total_up/total_down) > saiobj.g_wine_up_down_rt:
        log_info('bingo: %s -- %s', stock_id, this_date)
        wine_mail('fresh', body)
        return 1

    return 0


saiobj.g_func_map['fresh'] = fresh_run


if __name__=="__main__":
    sailog_set("fresh.log")

    db = db_init()
    saiobj.g_db = db
    sai_load_conf2('wine.cfg')

    # 万兴科技
    stock_id = '300624'
    trade_dt = '2018-02-06'

    sai_fmt_set_fetch_len(40)
    df = sai_fmt_simple(stock_id, trade_dt, db)
    fresh_run()

    db_end(db)

    log_debug("--end")


# fresh.py
