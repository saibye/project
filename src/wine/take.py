#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *
from pub    import *


# 
# code at 2018-6-8
# 002837 - 2017-06-02
"""
"""

def take_load_cfg():
    saiobj.g_wine_start_rate= float(sai_conf_get2('take', 'start_rate'))

    saiobj.g_wine_last_rate = float(sai_conf_get2('take', 'last_rate'))
    saiobj.g_wine_last_zt   = float(sai_conf_get2('take', 'last_zt'))

    saiobj.g_wine_vr5       = float(sai_conf_get2('take', 'vr5'))
    saiobj.g_wine_vr10      = float(sai_conf_get2('take', 'vr10'))
    saiobj.g_wine_vr50      = float(sai_conf_get2('take', 'vr50'))
    saiobj.g_wine_open_rate = float(sai_conf_get2('take', 'open_rate'))
    saiobj.g_wine_gap_rate  = float(sai_conf_get2('take', 'gap_rate'))

    saiobj.g_wine_cfg_loaded= True
    # log_debug('take config loaded')



def take_run():
    body = ''

    stock_id  = ref_id(0)
    this_date = ref_date(0)

    log_info('TRAN take: %s -- %s', stock_id, this_date)


    length = ref_len()
    if length < 90:
        # log_debug('%s too short: %d', stock_id, length)
        return 0

    # if not saiobj.g_wine_cfg_loaded:
    take_load_cfg()


    rate0 = 100.00 * (ref_close(0) - ref_close(1)) / ref_close(1)
    # log_info("rate0: %.2f%%", rate0)
    body += '跌幅: %.2f%%\n' % (rate0)

    open_rate0 = 100.00 * (ref_open(0) - ref_close(1)) / ref_close(1)
    # log_info("open-rate0: %.2f%%", open_rate0)
    body += '低开: %.2f%%\n' % (open_rate0)

    gap_rate0  = 100.00 * (ref_high(0) - ref_close(1)) / ref_close(1)
    # log_info("gap-rate0: %.2f%%", gap_rate0)
    body += '缺口: %.2f%%\n' % (gap_rate0)

    zt0   = 100.00 * (ref_close(0) - ref_open(0))  / ref_close(1)
    # log_info("zt0:   %.2f%%", zt0)
    # body += '柱体: %.2f%%\n' % (zt0)


    rate1 = 100.00 * (ref_close(1) - ref_close(2)) / ref_close(2)
    # log_info("rate1: %.2f%%", rate1)
    body += '昨日跌幅: %.2f%%\n' % (rate1)

    zt1   = 100.00 * (ref_close(1) - ref_open(1))  / ref_close(2)
    # log_info("zt1:   %.2f%%", zt1)
    body += '昨日柱体: %.2f%%\n' % (zt1)


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

    # 暴跌 + 长阴
    last_rule = rate1 < saiobj.g_wine_last_rate \
                and zt1 < saiobj.g_wine_last_zt

    # 低开高走 + 大缺口 + 放量
    this_rule = zt0 > 0 and zt0 < 4             \
                and open_rate0 < saiobj.g_wine_open_rate    \
                and gap_rate0  < saiobj.g_wine_gap_rate     \
                and ref_close(0) < ref_ma5(0)   \
                and ref_close(0) < ref_ma10(0)  \
                and ref_close(0) < ref_ma20(0)  \
                and ref_close(0) < ref_ma60(0)  \
                and this_vr5    > saiobj.g_wine_vr5 \
                and this_vr10   > saiobj.g_wine_vr10 \
                and this_vr50   > saiobj.g_wine_vr50

    # log_debug('last_rule: %s, this_rule: %s', last_rule, this_rule)

    if last_rule and this_rule:
        log_info('bingo: %s -- %s', stock_id, this_date)
        wine_mail('take', body)
        return 1


    return 0


saiobj.g_func_map['take'] = take_run


if __name__=="__main__":
    sailog_set("take.log")

    db = db_init()
    saiobj.g_db = db

    sai_load_conf2('wine.cfg')

    #
    stock_id = '002837'
    trade_dt = '2017-06-02'


    saiobj.g_to_send_mail = True

    sai_fmt_set_fetch_len(210)
    df = sai_fmt_simple(stock_id, trade_dt, db)
    take_run()

    db_end(db)

    log_debug("--end")


# take.py
