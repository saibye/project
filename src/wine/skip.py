#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *
from pub    import *


# 不强求次新
# ref_k(0) --> ref_k(m) --> ref_k(m+n)
# code at 2018-6-4
# 603518 维格娜丝

def skip_load_cfg():
    saiobj.g_wine_start_rate= float(sai_conf_get2('skip', 'start_rate'))
    saiobj.g_wine_step      = int(sai_conf_get2('skip', 'find_step'))
    saiobj.g_wine_step_zt   = float(sai_conf_get2('skip', 'green_zt'))
    saiobj.g_wine_step_rate = float(sai_conf_get2('skip', 'green_rate'))
    saiobj.g_wine_total_down= float(sai_conf_get2('skip', 'total_down'))
    saiobj.g_wine_total_up  = float(sai_conf_get2('skip', 'total_up'))
    saiobj.g_wine_up_down_rt= float(sai_conf_get2('skip', 'up_down_rate'))
    saiobj.g_wine_cfg_loaded= True
    #log_debug('skip config loaded')



def skip_run():
    body = ''

    stock_id  = ref_id(0)
    this_date = ref_date(0)

    log_info('TRAN skip: %s -- %s', stock_id, this_date)

    length = ref_len()

    skip_load_cfg()

    rate = 100.00 * (ref_close(0) - ref_close(1)) / ref_close(1)
    # log_info("rate: %.2f%%", rate)
    zt   = 100.00 * (ref_close(0) - ref_open(0))  / ref_close(1)
    # log_info("zt:   %.2f%%", zt)
    body += '涨幅: %.2f%%\n' % (rate)
    body += '柱体: %.2f%%\n' % (zt)


    START_RATE = saiobj.g_wine_start_rate
    if rate > START_RATE:
        # log_info('start rate not match: %.2f%% > %.2f%%', rate, START_RATE)
        return 0

    step = saiobj.g_wine_step
    # log_debug('step: %d', step)

    start = 0+1
    k2 = wine_find_previous_green(start, step)
    if k2 == 0:
        # log_info('not found k2')
        return 0
    else:
        log_info('got k2 -- %d', k2)
        body += 'ref(%d): %s\n' % (k2, ref_date(k2))

    start = k2+1
    k3 = wine_find_previous_green(start, step)
    if k3 == 0:
        log_info('not found k3')
        return 0
    else:
        log_info('got k3 -- %d', k3)
        body += 'ref(%d): %s\n' % (k3, ref_date(k3))

    if k3+1 >= length:
        log_info('k3 -- %d reach end', k3)
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
        wine_mail('skip', body)
        return 1

    return 0


saiobj.g_func_map['skip'] = skip_run


if __name__=="__main__":
    sailog_set("skip.log")

    db = db_init()
    saiobj.g_db = db

    sai_load_conf2('wine.cfg')

    # 
    stock_id = '603518'
    trade_dt = '2018-02-09'

    # 
    stock_id = '603386'
    trade_dt = '2018-06-01'

    # 
    stock_id = '603056'
    trade_dt = '2018-02-13'


    # 
    stock_id = '603356'
    trade_dt = '2018-03-23'


    saiobj.g_to_send_mail = True

    sai_fmt_set_fetch_len(200)
    df = sai_fmt_simple(stock_id, trade_dt, db)
    skip_run()

    db_end(db)

    log_debug("--end")


# skip.py
