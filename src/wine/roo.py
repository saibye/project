#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *
from pub    import *


# 袋鼠尾 Kangaroo tail
# code at 2019-3-8
# 002017 东信和平 2018-12-3

def roo_load_cfg():
    saiobj.g_wine_start_rate= float(sai_conf_get2('roo', 'start_rate'))
    saiobj.g_wine_step      = int(sai_conf_get2('roo', 'find_step'))
    #log_debug('roo config loaded')



def roo_run():
    body = ''

    stock_id  = ref_id(0)
    this_date = ref_date(0)

    log_debug('TRAN roo: %s -- %s', stock_id, this_date)

    length = ref_len()
    if length < 30:
        return 0

    roo_load_cfg()


    # day0 第一天，小阳柱
    rate0 = 100.00 * (ref_close(0) - ref_close(1)) / ref_close(1)
    zt0   = 100.00 * (ref_close(0) - ref_open(0))  / ref_close(1)
    body += "zt(-): %.2f%%\n" % (zt0)
    log_debug("rate0: %.2f%%, zt0:%.2f%%", rate0, zt0)
                                     

    if rate0 > 1.0 and zt0 > 1.0:
        pass
    else:
        log_debug("sorry, day0 not match")
        return 0

    # day0, high
    rule0 = ref_high(0) > ref_high(1) and zt0 < 2.0
    if rule0:
        log_info("high point matched")
        pass
    else:
        log_debug("sorry, high point not match")
        return 0


    # day1 第二天 长下影线
    rate1 = 100.00 * (ref_close(1) - ref_close(2)) / ref_close(2)
    zt1   = 100.00 * (ref_close(1) - ref_open(1))  / ref_close(2)
    log_debug("rate1: %.2f%%, zt1:%.2f%%", rate1, zt1)

    # 下影线
    small = min(ref_close(1), ref_open(1))
    shadow= 100.00 * (small - ref_low(1)) / ref_close(2)
    body += "shadow(+): %.2f%%\n" % (shadow)
    log_debug("shadow1: %.2f%%", shadow)
                                     

    if rate1 < 1.0 and shadow > 4.0 and zt1 < 2.0:
        pass
    else:
        log_debug("sorry, day1 not match")
        return 0

    # 下行趋势
    rule1 = ref_close(1) < ref_ma5(1) and ref_close(1) < ref_ma10(1)  and ref_close(1) < ref_ma20(1) 
    if rule1:
        log_info("day1 MA matched")
        pass
    else:
        log_debug("sorry, day1 MA not match")
        return 0


    # day2 第三天 阴线
    rate2 = 100.00 * (ref_close(2) - ref_close(3)) / ref_close(3)
    zt2   = 100.00 * (ref_close(2) - ref_open(2))  / ref_close(3)
    log_debug("rate2: %.2f%%, zt1:%.2f%%", rate2, zt2)

    if ref_high(1) < ref_low(2):
        body += "有缺口\n"


    if rate2 < -3.0:
        pass
    else:
        log_debug("sorry, day2 not match")
        return 0
        


    if True:
        log_info('bingo: %s -- %s', stock_id, this_date)
        wine_mail('roo', body)
        return 1

    return 0


saiobj.g_func_map['roo'] = roo_run


if __name__=="__main__":
    sailog_set("roo.log")

    db = db_init()
    saiobj.g_db = db

    sai_load_conf2('wine.cfg')


    # saiobj.g_to_send_mail = True

    # 东信和平
    trade_dt = '2018-12-03'
    stock_id = '002017'


    sai_fmt_set_fetch_len(200)
    df = sai_fmt_simple(stock_id, trade_dt, db)
    roo_run()

    db_end(db)

    log_debug("--end")


# roo.py
