#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *
from pub    import *


# 直上直下
# code at 2018-9-25
#

def sim_load_cfg():
    saiobj.g_wine_start_rate= float(sai_conf_get2('sim', 'start_rate'))
    saiobj.g_wine_step_down = int(sai_conf_get2('sim', 'down_step'))
    saiobj.g_wine_step_up   = int(sai_conf_get2('sim', 'up_step'))
    saiobj.g_wine_total_down= float(sai_conf_get2('sim', 'total_down'))
    saiobj.g_wine_total_up  = float(sai_conf_get2('sim', 'total_up'))
    saiobj.g_wine_cfg_loaded= True
    #log_debug('sim config loaded')



def sim_run():
    body = ''

    stock_id  = ref_id(0)
    this_date = ref_date(0)

    log_info('TRAN sim: %s -- %s', stock_id, this_date)

    length = ref_len()

    sim_load_cfg()

    k1 = 0
    rate = 100.00 * (ref_close(0) - ref_close(1)) / ref_close(1)
    # log_info("rate: %.2f%%", rate)
    # log_info("close:%.2f",  ref_close(0))
    body += '涨幅: %.2f%%\n' % (rate)


    START_RATE = saiobj.g_wine_start_rate
    if rate > START_RATE:
        # log_info('start rate not match: %.2f%% > %.2f%%', rate, START_RATE)
        return 0

    step1 = saiobj.g_wine_step_down
    # log_debug('step: %d', step1)


    start = k1 + 1
    k2 = wine_find_previous_highest_close(start, step1)
    if k2 == 0:
        # log_info('not found k2')
        return 0
    else:
        log_debug('got k2 -- %d, %.2f, %s', k2, ref_close(k2), ref_date(k2))
        body += '前高: ref(%d): %s\n' % (k2, ref_date(k2))

    day1 = k2 - k1
    acc1 = (ref_close(k1) - ref_close(k2)) * 100.00 / ref_close(k2)
    log_debug('down: days: %d, rate: %.2f%%', day1, acc1)
    body += '累计跌幅: %.2f%%, %d天\n' % (acc1, day1)

    ACC_RATE1 = saiobj.g_wine_total_down
    if acc1 > ACC_RATE1:
        log_debug('acc1 rate not match: %.2f%% > %.2f%%', acc1, ACC_RATE1)
        return 0


    start = k2 + 1
    step2 = saiobj.g_wine_step_up
    k3 = wine_find_previous_lowest_close(start, step2)
    if k3 == 0:
        # log_info('not found k3')
        return 0
    else:
        log_info('got k3 -- %d, %.2f, %s', k3, ref_close(k3), ref_date(k3))
        body += '前低: ref(%d): %s\n' % (k3, ref_date(k3))

    day2 = k3 - k2
    acc2 = (ref_close(k2) - ref_close(k3)) * 100.00 / ref_close(k3)
    log_info('up: days: %d, rate: %.2f%%', day2, acc2)
    body += '累计升幅: %.2f%%, %d天\n' % (acc2, day2)

    ACC_RATE2 = saiobj.g_wine_total_up
    if acc2 < ACC_RATE2:
        log_info('acc1 rate not match: %.2f%% < %.2f%%', acc2, ACC_RATE2)
        return 0


    RATE_RATE = abs(1.0* acc2 / acc1)
    log_info('RATE-RATE: %.2f', RATE_RATE)
    if RATE_RATE >= 2.9:
        log_info('bingo: %s -- %s', stock_id, this_date)
        wine_mail('sim', body)
        return 1

    return 0


saiobj.g_func_map['sim'] = sim_run


if __name__=="__main__":
    sailog_set("sim.log")

    db = db_init()
    saiobj.g_db = db

    sai_load_conf2('wine.cfg')


    stock_id = '300104'
    trade_dt = '2018-09-19'

    stock_id = '600218'
    trade_dt = '2019-02-01'

    # saiobj.g_to_send_mail = True

    sai_fmt_set_fetch_len(200)
    df = sai_fmt_simple(stock_id, trade_dt, db)
    sim_run()

    db_end(db)

    log_debug("--end")


# sim.py
