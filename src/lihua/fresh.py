#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *


def fresh_find_previous_green(_start, _width):

    ZT  = saiobj.g_fresh_step_zt
    RATE= saiobj.g_fresh_step_rate

    for x in range(_width):
        i = x + _start

        if i + 2 >= ref_len():
            log_error('too short: %d < %d', i+2, ref_len())
            return 0

        rate = 100.00 * (ref_close(i) - ref_close(i+1)) / ref_close(i+1)
        amp  = 100.00 * (ref_high(i)  - ref_low(i)) / ref_close(i+1)
        zt   = 100.00 * (ref_close(i) - ref_open(i)) / ref_close(i+1)
        log_debug('++date(%d): %s', i, ref_date(i))
        log_debug('++rate(%d): %.2f', i, rate)
        log_debug('++amp (%d): %.2f', i, amp)
        log_debug('++zt  (%d): %.2f', i, zt)
        if zt < ZT:
            log_info('++%s -- ref(%d) matched: zt:%.2f%%', ref_date(i), i, zt)
            return i

    return 0

def fresh_find_total_up(_start, _width):

    ZT  = saiobj.g_fresh_step_zt
    RATE= saiobj.g_fresh_step_rate

    min_close = 9999
    for x in range(_width):
        i = x + _start
        if i + 1 >= ref_len():
            log_error('too short: %d < %d', i+1, ref_len())
            return min_close

        if ref_close(i) < min_close:
            min_close = ref_close(i)

    return min_close


def fresh_load_cfg():
    saiobj.g_fresh_start_rate= float(sai_conf_get2('fresh', 'start_rate'))
    saiobj.g_fresh_step      = int(sai_conf_get2('fresh', 'find_step'))
    saiobj.g_fresh_step_zt   = float(sai_conf_get2('fresh', 'green_zt'))
    saiobj.g_fresh_step_rate = float(sai_conf_get2('fresh', 'green_rate'))
    saiobj.g_fresh_total_down= float(sai_conf_get2('fresh', 'total_down'))
    saiobj.g_fresh_total_up  = float(sai_conf_get2('fresh', 'total_up'))
    saiobj.g_fresh_up_down_rt= float(sai_conf_get2('fresh', 'up_down_rate'))
    saiobj.g_fresh_cfg_loaded= True
    log_debug('fresh config loaded')


def fresh(_stock_id, _date, _df):
    log_debug('fresh: %s, %s', _stock_id, _date)

    length = len(_df)
    if length > 30:
        log_debug('%s too long: %d', _stock_id, length)
        return 0

    if not saiobj.g_fresh_cfg_loaded:
        fresh_load_cfg()

    START_RATE = saiobj.g_fresh_start_rate

    rate = 100.00 * (ref_close(0) - ref_close(1)) / ref_close(1)
    log_info("rate: %.2f%%", rate)

    step = saiobj.g_fresh_step
    log_debug('step: %d', step)

    start = 0+1
    k2 = fresh_find_previous_green(start, step)
    log_info('got k2 -- %d', k2)

    start = k2+1
    k3 = fresh_find_previous_green(start, step)
    log_info('got k3 -- %d', k3)

    if k3+1 >= length:
        log_info('k3 -- %d', k3)
        return 0

    TOTAL_DOWN = saiobj.g_fresh_total_down
    total_down = 100.00 * (ref_close(0) - ref_close(k3+1)) / ref_close(k3+1)
    log_info('down-rate -- %.2f --> %.2f =  %.2f%%', ref_close(k3+1), ref_close(0), total_down)
    if total_down > TOTAL_DOWN:
        log_error('error: total-rate not matched: %.2f', total_down)
        return 0

    start = k3+1
    min_close = fresh_find_total_up(start, 7)
    if min_close > 1000:
        log_error('error: invalid min-close: %.2f', min_close)
        return 0
    total_up = 100.00 * (ref_close(k3+1) - min_close) / min_close
    TOTAL_UP = saiobj.g_fresh_total_up
    log_info('up-rate -- %.2f --> %.2f =  %.2f%%', min_close, ref_close(k3+1), total_up)
    if total_up > TOTAL_UP and abs(total_up/total_down) > 2:
        log_info('bingo: %s -- %s', _stock_id, _date)
        return 1

    return 0


saiobj.g_func_map['fresh'] = fresh


if __name__=="__main__":
    sailog_set("fresh.log")

    db = db_init()
    sai_load_conf2('lihua.cfg')

    stock_id = '300675'
    trade_dt = '2017-08-10'

    sai_fmt_set_fetch_len(100)
    df = sai_fmt_simple(stock_id, trade_dt, db)
    fresh(stock_id, trade_dt, df)

    db_end(db)

    log_debug("--end")


# fresh.py
