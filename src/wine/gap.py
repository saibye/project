#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *
from pub    import *


# 缺口
# code at 2019-1-26
# 600218 全柴动力

def gap_load_cfg():
    saiobj.g_wine_start_rate= float(sai_conf_get2('gap', 'start_rate'))
    #log_debug('gap config loaded')



def gap_run():
    body = ''

    stock_id  = ref_id(0)
    this_date = ref_date(0)

    log_debug('TRAN gap: %s -- %s', stock_id, this_date)

    length = ref_len()

    gap_load_cfg()

    k1 = 0
    rate = 100.00 * (ref_close(0) - ref_close(1)) / ref_close(1)
    log_debug("rate: %.2f%%", rate)
    body += '涨幅: %.2f%%\n' % (rate)


    START_RATE = saiobj.g_wine_start_rate
    if rate < START_RATE:
        log_info('start rate not match: %.2f%% > %.2f%%', rate, START_RATE)
        return 0

    # 取跳空幅度
    gap_rate = 100.00 * (ref_low(0) - ref_high(1)) / ref_close(1)
    log_info("gap: %.2f%%",  gap_rate)

    # 取成交量比
    this_vr5     = ref_vol(0) / ref_vma5(0)
    this_vr10    = ref_vol(0) / ref_vma10(0)
    this_vr50    = ref_vol(0) / ref_vma50(0)
    body += '今日量比(5/10/50): %.2f, %.2f, %.2f\n' % (this_vr5, this_vr10, this_vr50)

    log_info("vol:      %.2f", ref_vol(0))
    log_info("vma5:     %.2f, this_vr5:  %.2f", ref_vma5(0),  this_vr5)
    log_info("vma10:    %.2f, this_vr10: %.2f", ref_vma10(0), this_vr10)
    log_info("vma50:    %.2f, this_vr50: %.2f", ref_vma50(0), this_vr50)

    # 取突破 
    # - 天数*3
    # - 均线

    # 前一天贴近均线


    """
    step1 = saiobj.g_wine_step_down
    # log_debug('step: %d', step1)


    start = k1 + 1
    k2 = wine_find_previous_highest_close(start, step1)
    if k2 == 0:
        # log_info('not found k2')
        return 0
    else:
        log_info('got k2 -- %d, %.2f, %s', k2, ref_close(k2), ref_date(k2))
        body += '前高: ref(%d): %s\n' % (k2, ref_date(k2))

    day1 = k2 - k1
    acc1 = (ref_close(k1) - ref_close(k2)) * 100.00 / ref_close(k2)
    log_info('down: days: %d, rate: %.2f%%', day1, acc1)
    body += '累计跌幅: %.2f%%, %d天\n' % (acc1, day1)

    ACC_RATE1 = saiobj.g_wine_total_down
    if acc1 > ACC_RATE1:
        log_info('acc1 rate not match: %.2f%% > %.2f%%', acc1, ACC_RATE1)
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
    if RATE_RATE >= 3:
        log_info('bingo: %s -- %s', stock_id, this_date)
        wine_mail('gap', body)
        return 1
    """

    return 0


saiobj.g_func_map['gap'] = gap_run


if __name__=="__main__":
    sailog_set("gap.log")

    db = db_init()
    saiobj.g_db = db

    sai_load_conf2('wine.cfg')


    stock_id = '600218'
    trade_dt = '2019-01-14'

    # saiobj.g_to_send_mail = True

    sai_fmt_set_fetch_len(200)
    df = sai_fmt_simple(stock_id, trade_dt, db)
    gap_run()

    db_end(db)

    log_debug("--end")


# gap.py
