#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *
from pub    import *


# 
# code at 2018-6-10
# 启明星
"""
"""

def qiming_load_cfg():
    saiobj.g_wine_start_rate= float(sai_conf_get2('qiming', 'start_rate'))
    saiobj.g_wine_cfg_loaded= True
    # log_debug('qiming config loaded')



def qiming_run():
    body = ''

    stock_id  = ref_id(0)
    this_date = ref_date(0)

    log_info('TRAN qiming: %s -- %s', stock_id, this_date)


    length = ref_len()
    if length < 110:
        log_debug('%s too short: %d', stock_id, length)
        return 0

    # if not saiobj.g_wine_cfg_loaded:
    qiming_load_cfg()


    rate0 = 100.00 * (ref_close(0) - ref_close(1)) / ref_close(1)
    # log_info("rate0: %.2f%%", rate0)
    body += '跌幅: %.2f%%\n' % (rate0)

    zt0   = 100.00 * (ref_close(0) - ref_open(0))  / ref_close(1)
    # log_info("zt0:   %.2f%%", zt0)
    # body += '柱体: %.2f%%\n' % (zt0)


    rate1 = 100.00 * (ref_close(1) - ref_close(2)) / ref_close(2)
    # log_info("rate1: %.2f%%", rate1)
    body += '昨日跌幅: %.2f%%\n' % (rate1)

    zt1   = 100.00 * (ref_close(1) - ref_open(1))  / ref_close(2)
    # log_info("zt1:   %.2f%%", zt1)
    body += '昨日柱体: %.2f%%\n' % (zt1)


    rate2 = 100.00 * (ref_close(2) - ref_close(3)) / ref_close(3)
    # log_info("rate2: %.2f%%", rate2)
    body += '前日跌幅: %.2f%%\n' % (rate2)

    zt2   = 100.00 * (ref_close(2) - ref_open(2))  / ref_close(3)
    # log_info("zt2:   %.2f%%", zt2)
    body += '前日柱体: %.2f%%\n' % (zt2)


    """
    log_info("p-close:  %.2f", ref_close(0))
    log_info("pma5:     %.2f", ref_ma5(0))
    log_info("pma10:    %.2f", ref_ma10(0))
    log_info("pma20:    %.2f", ref_ma20(0))
    log_info("pma60:    %.2f", ref_ma60(0))
    log_info("pma200:   %.2f", ref_ma200(0))
    """


    this_vr5     = ref_vol(0) / ref_vma5(0)
    this_vr10    = ref_vol(0) / ref_vma10(0)
    this_vr50    = ref_vol(0) / ref_vma50(0)
    body += '今日量比(5/10/50): %.2f, %.2f, %.2f\n' % (this_vr5, this_vr10, this_vr50)

    """
    log_info("vol:      %.2f", ref_vol(0))
    log_info("vma5:     %.2f, this_vr5:  %.2f%%", ref_vma5(0),  this_vr5)
    log_info("vma10:    %.2f, this_vr10: %.2f%%", ref_vma10(0), this_vr10)
    log_info("vma50:    %.2f, this_vr50: %.2f%%", ref_vma50(0), this_vr50)
    """


    last_vr5     = ref_vol(1) / ref_vma5(1)
    last_vr10    = ref_vol(1) / ref_vma10(1)
    last_vr50    = ref_vol(1) / ref_vma50(1)

    """
    log_info("vol:      %.2f", ref_vol(1))
    log_info("vma5:     %.2f, last_vr5:  %.2f%%", ref_vma5(1),  last_vr5)
    log_info("vma10:    %.2f, last_vr10: %.2f%%", ref_vma10(1), last_vr10)
    log_info("vma50:    %.2f, last_vr50: %.2f%%", ref_vma50(1), last_vr50)
    """


    # 今日: 涨停 + 跳空
    this_rule = zt0 > 3                         \
                and rate0 > 9.9                 \
                and ref_open(0) > ref_open(1)   \
                and ref_open(0) > ref_close(1)

    # 昨日: 大跌 + 缩量 + 跳空
    last_rule = zt1 < 2 and rate1 < -2         \
                and max(ref_close(1), ref_open(1)) < ref_close(2)   \
                and max(ref_close(1), ref_open(1)) > ref_ma60(1)    \
                and max(ref_close(1), ref_open(1)) > ref_ma200(1)   \
                and last_vr5    < 1 \
                and last_vr10   < 1 \
                and last_vr50   < 1

    # 前日: 暴跌 + 长阴
    last_last = zt2 < -5 and rate2 < -9.9       

    # log_debug('this_rule: %s, last_rule: %s, last_last: %s', this_rule, last_rule, last_last)

    if last_rule and this_rule and last_last:
        log_info('bingo: %s -- %s', stock_id, this_date)
        wine_mail('qiming', body)
        return 1


    return 0


saiobj.g_func_map['qiming'] = qiming_run


if __name__=="__main__":
    sailog_set("qiming.log")

    db = db_init()
    saiobj.g_db = db

    sai_load_conf2('wine.cfg')

    # 
    stock_id = '600908'
    trade_dt = '2017-05-02'

    stock_id = '002889'
    trade_dt = '2018-05-31'


    # saiobj.g_to_send_mail = True

    sai_fmt_set_fetch_len(210)
    df = sai_fmt_simple(stock_id, trade_dt, db)
    qiming_run()

    db_end(db)

    log_debug("--end")


# qiming.py
