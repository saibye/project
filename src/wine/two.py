#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *
from pub    import *


# 次新
# code at 2018-5-12
# 连续两个跌停
#
"""
     u
    u  d 
   u    d 
  u      
 u
u
"""

def two_load_cfg():
    saiobj.g_wine_start_rate= float(sai_conf_get2('two', 'start_rate'))
    saiobj.g_wine_step      = int(sai_conf_get2('two', 'find_step'))
    saiobj.g_wine_step_zt   = float(sai_conf_get2('two', 'green_zt'))
    saiobj.g_wine_step_rate = float(sai_conf_get2('two', 'green_rate'))
    saiobj.g_wine_total_down= float(sai_conf_get2('two', 'total_down'))
    saiobj.g_wine_total_up  = float(sai_conf_get2('two', 'total_up'))
    saiobj.g_wine_up_down_rt= float(sai_conf_get2('two', 'up_down_rate'))
    saiobj.g_wine_cfg_loaded= True
    log_debug('two config loaded')



def two_run():
    body = ''

    stock_id  = ref_id(0)
    this_date = ref_date(0)

    log_info('TRAN two: %s -- %s', stock_id, this_date)

    length = ref_len()
    if length > 30:
        # log_debug('%s too old: %d', stock_id, length)
        return 0
    body += '次新天数: %d\n' % (length)

    # if not saiobj.g_wine_cfg_loaded:
    two_load_cfg()


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

    kh = k2+1
    # kh = wine_find_previous_highest(start, 3)
    log_info('k-highest -- %d', kh)

    TOTAL_DOWN = saiobj.g_wine_total_down
    total_down = 100.00 * (ref_close(0) - ref_close(kh)) / ref_close(kh)
    log_info('down-rate -- %.2f --> %.2f =  %.2f%%', ref_close(kh), ref_close(0), total_down)
    if total_down > TOTAL_DOWN:
        log_error('error: total-rate not matched: %.2f', total_down)
        return 0

    body += '累计跌幅: %.2f%%\n' % (total_down)

    start = kh
    min_close = wine_find_total_up(start, 7)
    if min_close > 1000:
        log_error('error: invalid min-close: %.2f', min_close)
        return 0
    total_up = 100.00 * (ref_close(kh) - min_close) / min_close
    body += '累计上升: %.2f%%\n' % (total_up)
    TOTAL_UP = saiobj.g_wine_total_up
    log_info('up-rate -- %.2f --> %.2f =  %.2f%%', min_close, ref_close(kh), total_up)
    if total_up > TOTAL_UP and abs(total_up/total_down) > saiobj.g_wine_up_down_rt:
        log_info('bingo: %s -- %s', stock_id, this_date)
        wine_mail('two', body)
        return 1

    return 0


saiobj.g_func_map['two'] = two_run


if __name__=="__main__":
    sailog_set("two.log")

    db = db_init()
    saiobj.g_db = db

    sai_load_conf2('wine.cfg')






    # 南都物业
    stock_id = '603506'
    trade_dt = '2018-02-14'

    # good 华菱精工
    stock_id = '603356'
    trade_dt = '2018-02-06'

    # 广州港
    stock_id = '601228'
    trade_dt = '2017-04-24'

    # 锋龙股份
    stock_id = '002931'
    trade_dt = '2018-04-27'


    sai_fmt_set_fetch_len(40)
    df = sai_fmt_simple(stock_id, trade_dt, db)
    two_run()

    db_end(db)

    log_debug("--end")


# two.py
