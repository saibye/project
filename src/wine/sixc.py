#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *
from pub    import *


#
# code at 2018-6-5
# sixc-line cross
#
"""
"""

def sixc_load_cfg():
    saiobj.g_wine_start_rate= float(sai_conf_get2('sixc', 'start_rate'))
    saiobj.g_wine_cfg_loaded= True



def sixc_run():
    body = ''

    stock_id  = ref_id(0)
    this_date = ref_date(0)

    log_debug('TRAN sixc: %s -- %s', stock_id, this_date)

    length = ref_len()
    if length < 210:
        log_debug('%s too short: %d', stock_id, length)
        return 0

    sixc_load_cfg()


    rate = 100.00 * (ref_close(0) - ref_close(1)) / ref_close(1)
    log_info("rate: %.2f%%", rate)
    zt   = 100.00 * (ref_close(0) - ref_open(0))  / ref_close(1)
    # log_info("zt:   %.2f%%", zt)
    body += '涨幅: %.2f%%\n' % (rate)
    body += '柱体: %.2f%%\n' % (zt)


    START_RATE = saiobj.g_wine_start_rate
    if rate < START_RATE:
        log_info('start rate not match: %.2f%% > %.2f%%', rate, START_RATE)
        return 0


    """
    log_info("p-open:   %.2f", ref_open(0))
    log_info("pma5:     %.2f", ref_ma5(0))
    log_info("pma10:    %.2f", ref_ma10(0))
    log_info("pma20:    %.2f", ref_ma20(0))
    log_info("pma60:    %.2f", ref_ma60(0))
    log_info("pma200:   %.2f", ref_ma200(0))
    log_info("p-close:  %.2f", ref_close(0))
    """


    minp = min(ref_ma5(0), ref_ma10(0), ref_ma20(0), ref_ma60(0), ref_ma200(0))
    maxp = max(ref_ma5(0), ref_ma10(0), ref_ma20(0), ref_ma60(0), ref_ma200(0))
    """
    log_info("p-min:  %.2f", minp)
    log_info("p-max:  %.2f", maxp)
    """

    poly = 100.00 * (maxp - minp) / ref_close(1)
    log_info("poly:   %.2f%%", poly)
    body += '聚合: %.2f%%\n' % (poly)

    zt1 = 100.00 * (ref_close(0) - maxp) / ref_close(1)
    zt2 = 100.00 * (minp - ref_open(0))  / ref_close(1)
    """
    log_info("zt1:   %.2f%%", zt1)
    log_info("zt2:   %.2f%%", zt2)
    """
    body += '上柱体: %.2f%%\n' % (zt1)
    body += '下柱体: %.2f%%\n' % (zt2)


    """
    log_info("diff:     %.2f", ref_diff(0))
    log_info("dea:      %.2f", ref_dea(0))
    log_info("macd:     %.2f", ref_macd(0))
    """
    body += 'diff/dea/mach: %.2f, %.2f, %.2f\n' % (ref_diff(0), ref_dea(0), ref_macd(0))


    this_vr5     = ref_vol(0) / ref_vma5(0)
    this_vr10    = ref_vol(0) / ref_vma10(0)
    this_vr50    = ref_vol(0) / ref_vma50(0)
    body += '量比(5/10/50): %.2f, %.2f, %.2f\n' % (this_vr5, this_vr10, this_vr50)

    """
    log_info("vol:      %.2f", ref_vol(0))
    log_info("vma5:     %.2f, this_vr5:  %.2f%%", ref_vma5(0),  this_vr5)
    log_info("vma10:    %.2f, this_vr10: %.2f%%", ref_vma10(0), this_vr10)
    log_info("vma50:    %.2f, this_vr50: %.2f%%", ref_vma50(0), this_vr50)
    """

    # 穿越6线
    basic_rule = ref_close(0) > maxp and ref_open(0) < minp # cross


    # macd在0轴上方
    macd_rule  = ref_diff(0) > 0 and ref_dea(0) > 0 and ref_diff(0) < 0.2 and ref_dea(0) < 0.2


    # 放量
    vol_rule   = this_vr5 > 1 and this_vr10 > 1 and this_vr50 > 1


    ## 柱体上半部分空余 
    addit_rule = zt1 > 2

    rule = basic_rule and poly < 2 and macd_rule and addit_rule and vol_rule


    if rule:
        log_info('bingo: %s -- %s', stock_id, this_date)
        wine_mail('sixc', body)
        return 1

    return 0


saiobj.g_func_map['sixc'] = sixc_run


if __name__=="__main__":
    sailog_set("sixc.log")

    db = db_init()
    saiobj.g_db = db

    sai_load_conf2('wine.cfg')

    # 
    stock_id = '000860'
    trade_dt = '2018-03-29'

    sai_fmt_set_fetch_len(220)
    df = sai_fmt_simple(stock_id, trade_dt, db)
    sixc_run()

    db_end(db)

    log_debug("--end")


# sixc.py
