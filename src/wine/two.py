#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *
from pub    import *



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



def two_run(_stock_id, _date, _df):
    log_debug('tran two: %s', _date)

    """
    length = len(_df)
    if length > 30:
        log_debug('%s too long: %d', _stock_id, length)
        return 0

    if not saiobj.g_wine_cfg_loaded:
        two_load_cfg()

    START_RATE = saiobj.g_wine_start_rate

    rate = 100.00 * (ref_close(0) - ref_close(1)) / ref_close(1)
    log_info("rate: %.2f%%", rate)
    zt   = 100.00 * (ref_close(0) - ref_open(0))  / ref_close(1)
    log_info("zt:   %.2f%%", zt)

    step = saiobj.g_wine_step
    log_debug('step: %d', step)

    start = 0+1
    k2 = wine_find_previous_green(start, step)
    log_info('got k2 -- %d', k2)

    start = k2+1
    k3 = wine_find_previous_green(start, step)
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

    start = k3+1
    min_close = wine_find_total_up(start, 7)
    if min_close > 1000:
        log_error('error: invalid min-close: %.2f', min_close)
        return 0
    total_up = 100.00 * (ref_close(k3+1) - min_close) / min_close
    TOTAL_UP = saiobj.g_wine_total_up
    log_info('up-rate -- %.2f --> %.2f =  %.2f%%', min_close, ref_close(k3+1), total_up)
    if total_up > TOTAL_UP and abs(total_up/total_down) > 2:
        log_info('bingo: %s -- %s', _stock_id, _date)
        return 1
    """

    return 0


saiobj.g_func_map['two'] = two_run


if __name__=="__main__":
    sailog_set("two.log")

    db = db_init()
    sai_load_conf2('wine.cfg')

    stock_id = '300675'
    trade_dt = '2017-08-10'

    sai_fmt_set_fetch_len(40)
    df = sai_fmt_simple(stock_id, trade_dt, db)
    two_run(stock_id, trade_dt, df)

    db_end(db)

    log_debug("--end")


# two.py
