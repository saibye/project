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
    if length < 100:
        return 0

    gap_load_cfg()

    # 当天放量
    k = 0
    rate = 100.00 * (ref_close(k) - ref_close(k+1)) / ref_close(k+1)
    # log_debug("rateT0: %.2f%%", rate)
    body += '涨幅T0: %.2f%%\n' % (rate)


    START_RATE = 8.0  # saiobj.g_wine_start_rate
    if rate < START_RATE:
        log_info('start rate not match: %.2f%% > %.2f%%', rate, START_RATE)
        return 0

    # 取T0成交量比
    this_vr5     = ref_vol(k) / ref_vma5(k)
    this_vr10    = ref_vol(k) / ref_vma10(k)
    this_vr50    = ref_vol(k) / ref_vma50(k)
    body += 'T0量比(5/10/50): %.2f, %.2f, %.2f\n' % (this_vr5, this_vr10, this_vr50)

    if this_vr50 < 3.2:
        log_debug("sorry: T0：量比不足: %.2f", this_vr50)
        return 0
    else:
        log_info("T0: vol:      %.2f", ref_vol(k))
        log_info("T0: vma5:     %.2f, this_vr5:  %.2f", ref_vma5(k),  this_vr5)
        log_info("T0: vma10:    %.2f, this_vr10: %.2f", ref_vma10(k), this_vr10)
        log_info("T0: vma50:    %.2f, this_vr50: %.2f", ref_vma50(k), this_vr50)
        pass

    # 前一天：涨停+缺口
    k = 1
    rate = 100.00 * (ref_close(k) - ref_close(k+1)) / ref_close(k+1)
    log_debug("rateT1: %.2f%%", rate)
    # body += '涨幅T1: %.2f%%\n' % (rate)

    # START_RATE = saiobj.g_wine_start_rate
    if rate < 9.8:
        log_info('start rate not match: %.2f%% > %.2f%%', rate, START_RATE)
        return 0


    # 取跳空幅度
    gap_rate = 100.00 * (ref_low(k) - ref_high(k+1)) / ref_high(k+1)
    body += '缺口T1: %.2f%%\n' % (gap_rate)
    if gap_rate < 5.0:
        log_debug("sorry: 缺口不足: %.2f%%",  gap_rate)
        return 0
    else:
        log_info("GAP: %.2f%%",  gap_rate)
        pass


    # 取T1成交量比
    this_vr5     = ref_vol(k) / ref_vma5(k)
    this_vr10    = ref_vol(k) / ref_vma10(k)
    this_vr50    = ref_vol(k) / ref_vma50(k)
    body += 'T1量比(5/10/50): %.2f, %.2f, %.2f\n' % (this_vr5, this_vr10, this_vr50)

    """
    if this_vr50 < 5:
        log_debug("sorry: T1：量比不足: %.2f", this_vr50)
        return 0
    else:
        log_info("T1: vol:      %.2f", ref_vol(k))
        log_info("T1: vma5:     %.2f, this_vr5:  %.2f", ref_vma5(k),  this_vr5)
        log_info("T1: vma10:    %.2f, this_vr10: %.2f", ref_vma10(k), this_vr10)
        log_info("T1: vma50:    %.2f, this_vr50: %.2f", ref_vma50(k), this_vr50)
        pass
    """


    # 缺口前3天，存在未突破50
    k = 2
    disA = 100.00 * abs(ref_close(k) - ref_ma50(k)) / ref_ma50(k)
    disB = 100.00 * abs(ref_close(k+1) - ref_ma50(k+1)) / ref_ma50(k+1)
    disC = 100.00 * abs(ref_close(k+2) - ref_ma50(k+2)) / ref_ma50(k+2)
    log_debug("disABC: %.2f, %.2f, %.2f", disA, disB, disC)
    rule_break_just_now = min(disA, disB, disC) < 3.0
    if rule_break_just_now:                          
        log_info("good, break MA50 just now")
    else:
        log_debug("sorry, already break long time")
        return 0
        

    # 取突破天数
    k = 1
    b_day = wine_break_days(k, 80)
    body += '突破天数: %d\n' % (b_day)
    if b_day < 10:
        log_debug("sorry: T1突破天数: %d", b_day)
        return 0
    else:
        log_debug("T1突破天数: %d", b_day)


    body += "\n\n建议在阴线时，贴着均线MA5买入\n"
    if True:
        log_info('bingo: %s -- %s', stock_id, this_date)
        wine_mail('gap', body)
        return 1

    return 0


saiobj.g_func_map['gap'] = gap_run


if __name__=="__main__":
    sailog_set("gap.log")

    db = db_init()
    saiobj.g_db = db

    sai_load_conf2('wine.cfg')


    # 全柴动力
    stock_id = '600218'
    trade_dt = '2019-01-15'

    # 华仪电气
    stock_id = '600290'
    trade_dt = '2019-03-13'

    # saiobj.g_to_send_mail = True

    sai_fmt_set_fetch_len(200)
    df = sai_fmt_simple(stock_id, trade_dt, db)
    gap_run()

    db_end(db)

    log_debug("--end")


# gap.py
