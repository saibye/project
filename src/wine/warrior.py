#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *
from pub    import *


# 
# code at 2018-7-12
# 5个白武士
# 603045 福达合金  good
# ?? 601990 南京证券 on way
"""
"""

def warrior_load_cfg():
    saiobj.g_wine_start_rate    = float(sai_conf_get2('warrior', 'start_rate'))
    saiobj.g_wine_total_up      = float(sai_conf_get2('warrior', 'total_up'))
    saiobj.g_wine_total_down    = float(sai_conf_get2('warrior', 'total_down'))
    saiobj.g_wine_cfg_loaded= True
    # log_debug('warrior config loaded')


def warrior_run():
    body = ''

    stock_id  = ref_id(0)
    this_date = ref_date(0)

    log_debug('TRAN warrior: %s -- %s', stock_id, this_date)

    length = ref_len()
    if length > 50 or length < 15:
        # log_debug('%s days not meet: %d', stock_id, length)
        return 0

    # if not saiobj.g_wine_cfg_loaded:
    warrior_load_cfg()

    # log_debug('len: %d', length)

    #######################################################################
    rate0 = 100.00 * (ref_close(0) - ref_close(1)) / ref_close(1)
    zt0   = 100.00 * (ref_close(0) - ref_open(0))  / ref_close(1)
    body += 'day0: 涨幅：%.2f%%，柱体：%.2f%%\n' % (rate0, zt0)


    #######################################################################
    rate1 = 100.00 * (ref_close(1) - ref_close(2)) / ref_close(2)
    zt1   = 100.00 * (ref_close(1) - ref_open(1))  / ref_close(2)
    body += 'day1: 涨幅：%.2f%%，柱体：%.2f%%\n' % (rate1, zt1)


    #######################################################################
    rate2 = 100.00 * (ref_close(2) - ref_close(3)) / ref_close(3)
    zt2   = 100.00 * (ref_close(2) - ref_open(2))  / ref_close(3)
    body += 'day2: 涨幅：%.2f%%，柱体：%.2f%%\n' % (rate2, zt2)

    #######################################################################
    rate3 = 100.00 * (ref_close(3) - ref_close(4)) / ref_close(4)
    zt3   = 100.00 * (ref_close(3) - ref_open(3))  / ref_close(4)
    body += 'day3: 涨幅：%.2f%%，柱体：%.2f%%\n' % (rate3, zt3)

    #######################################################################
    rate4 = 100.00 * (ref_close(4) - ref_close(5)) / ref_close(5)
    zt4   = 100.00 * (ref_close(4) - ref_open(4))  / ref_close(5)
    body += 'day4: 涨幅：%.2f%%，柱体：%.2f%%\n' % (rate4, zt4)

    #######################################################################

    rate5 = 100.00 * (ref_close(5) - ref_close(6)) / ref_close(6)
    zt5   = 100.00 * (ref_close(5) - ref_open(5))  / ref_close(6)

    #######################################################################

    """
    log_info("rate0: %.2f%%", rate0)
    log_info("zt0:   %.2f%%", zt0)

    log_info("rate1: %.2f%%", rate1)
    log_info("zt1:   %.2f%%", zt1)

    log_info("rate2: %.2f%%", rate2)
    log_info("zt2:   %.2f%%", zt2)

    log_info("rate3: %.2f%%", rate3)
    log_info("zt3:   %.2f%%", zt3)

    log_info("rate4: %.2f%%", rate4)
    log_info("zt4:   %.2f%%", zt4)



    log_info("p-close:  %.2f", ref_close(0))
    log_info("pma5:     %.2f", ref_ma5(0))
    log_info("pma10:    %.2f", ref_ma10(0))
    log_info("pma20:    %.2f", ref_ma20(0))
    log_info("pma60:    %.2f", ref_ma60(0))
    log_info("pma200:   %.2f", ref_ma200(0))
    """


    # close-price
    days1 = wine_continuous_high(0, 5, 'close')
    # log_info('new high days -- close: %d', days1)
    body += '收盘价新高天数: %d\n' % (days1)

    # high-price
    days2 = wine_continuous_high(0, 5, 'high')
    # log_info('new high days -- high: %d', days2)
    body += '最高价新高天数: %d\n' % (days2)

    # low-price
    days3 = wine_continuous_high(0, 5, 'low')
    # log_info('new high days -- low: %d', days3)
    body += '最低价新高天数: %d\n' % (days3)


    # 累计涨幅
    acc_rate = 100.00 *(ref_close(0) - ref_close(4)) / ref_close(4)
    # log_info('5日累计涨幅: %.2f%%', acc_rate)
    body += '5日累计涨幅: %.2f%%\n' % (acc_rate)

    # 前一日跌
    # log_info("rate5: %.2f%%", rate5)
    # log_info("zt5:   %.2f%%", zt5)
    body += '边界阴线: %.2f%%\n' % (rate5)

    # 前3日暴跌
    idx = wine_find_previous_highest(5, 5)
    # log_info('previous-high: %dth, %.2f', idx, ref_high(idx))
    down_rate = 100.00 * (ref_high(idx) - ref_close(5)) / ref_close(5)
    # log_info("deep-down:   %.2f%%", down_rate)
    body += '三日下跌: %.2f%%\n' % (down_rate)


    # 五个阳柱
    rule1 = zt0 > 0 and zt1 > 0     \
                and zt2 > 0         \
                and zt3 > 0         \
                and zt4 > 0

    # 连续新高
    rule21 = days1 >= 4 and days2 >=4 and days3 >= 4
    rule22 = days1 >= 3 and days2 >=3 and days3 >= 3 and (days1+days2+days3) >= 10 and False
    rule2  = (rule21 or rule22)

    # 升幅不大 18
    rule3 = acc_rate < saiobj.g_wine_total_up

    # 
    # 前日: 阴
    rule4 = rate5 < -3 and zt5 < -3

    # 前几日: 暴跌 30
    rule5 = down_rate > saiobj.g_wine_total_down


    # if rule1 and rule2 and rule3:
    if rule1 and rule2 and rule3 and rule4 and rule5:
        log_info('bingo: %s -- %s', stock_id, this_date)
        wine_mail('warrior', body)
        return 1


    return 0


saiobj.g_func_map['warrior'] = warrior_run


if __name__=="__main__":
    sailog_set("warrior.log")

    db = db_init()
    saiobj.g_db = db

    sai_load_conf2('wine.cfg')

    saiobj.g_to_send_mail = True

    # 福达合金 good
    stock_id = '603045'
    trade_dt = '2018-07-02'

    # 南京证券 ??
    # stock_id = '601990'
    # trade_dt = '2018-07-02'

    # saiobj.g_to_send_mail = True

    sai_fmt_set_fetch_len(50)
    df = sai_fmt_simple(stock_id, trade_dt, db)
    warrior_run()

    db_end(db)

    log_debug("--end")


# warrior.py
