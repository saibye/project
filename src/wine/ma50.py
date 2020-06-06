#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *
from pub    import *


# 涨停+放量+徘徊+缩量回踩ma50
# code at 2020-4-29
# 
# 
#

def ma50_load_cfg():
    #log_debug('ma50 config loaded')
    pass



def ma50_run():
    body = ''

    stock_id  = ref_id(0)
    this_date = ref_date(0)

    log_info('TRAN ma50: %s -- %s', stock_id, this_date)

    length = ref_len()
    if length < 220:
        return 0

    ma50_load_cfg()

    ################################################################
    # start day
    ################################################################
    k = 0
    price_rule = ref_high(k) >= ref_ma50(k) and ref_low(k) <= ref_ma50(k) \
                 and ref_close(k) > ref_ma200(k)
    if price_rule:
        log_debug("S-DAY: price touch ma50")
        pass
    else:
        log_info("sorry, S-DAY price not back")
        return 0

    ################################################################
    # 回踩日：缩量
    rate0 = 100.00 * (ref_close(k) - ref_close(k+1)) / ref_close(k+1)
    log_debug("S-DAY: rate0: %.2f%%", rate0)

    # 量比
    vr50 = ref_vol(k) / ref_vma50(k)
    vr10 = ref_vol(k) / ref_vma10(k)
    vr5  = ref_vol(k) / ref_vma5(k)
    body += "vr50: %.2f\n" % (vr50)
    body += "vr10: %.2f\n" % (vr10)
    body += "vr5 : %.2f\n" % (vr5)

    log_debug("S-DAY: (vr50,10,5): %.2f, %.2f, %.2f", vr50, vr10, vr5)

    vr_rule = vr50 < 1.0 and vr10 < 1.0 and vr5 < 1.0
    if vr_rule:
        log_debug("S-DAY: vr shrink")
        pass
    else:
        log_info("sorry, S-DAY vol not shrinkage")
        return 0


    ################################################################
    ################################################################
    # GO-UP day

    the_day = -1

    start = 20
    width = 20
    for x in range(width):
        i = x + start

        if i + 2 >= ref_len():
            log_error('too short: %d >= %d', i+2, ref_len())
            return 0

        rate = 100.00 * (ref_close(i) - ref_close(i+1)) / ref_close(i+1)
        if rate > 9.8:
            log_debug("GO-UP limit: %.2f%% [%s]", rate, ref_date(i))
        else:
            # log_debug("normal rate: %.2f%%", rate)
            continue

        # price check
        price_rule = ref_high(i) > ref_ma50(i) and ref_low(i+1) < ref_ma50(i)
        if price_rule:
            log_debug("GO-UP near ma50 [%s]", ref_date(i))
        else:
            log_debug("GO-UP far  ma50")
            continue

        # vol check
        k = i - 1
        vr50 = ref_vol(k) / ref_vma50(k)
        vr10 = ref_vol(k) / ref_vma10(k)
        vr5  = ref_vol(k) / ref_vma5(k)
        log_debug("C-DAY: (vr50,10,5): %.2f, %.2f, %.2f", vr50, vr10, vr5)

        width = 180
        bd = wine_volume_break_days(k, width)
        log_debug("C-vol break days: %d", bd)

        width = 180
        rk = wine_volume_rank(k, width)
        log_debug("C-vol rank: %d", rk)

        vol_rule = ref_vol(k) > ref_vol(i) \
                   and rk < 1 \
                   and bd > 150 \
                   and vr5 > 2 \
                   and vr10 > 3 \
                   and vr50 > 3
        if vol_rule:
            log_debug("vol rule match: %s", ref_date(i))
            the_day = i
            break
        else:
            log_debug("vol rule not match")
        

    if the_day > 0:
        log_debug("found: %d -- %s", the_day, ref_date(the_day))
    else:
        log_debug("not found that day")
        return 0

    ################################################################
    ################################################################
    ################################################################
    ################################################################



    if True:
        log_info('bingo: %s -- %s', stock_id, this_date)
        wine_mail('ma50', body)
        return 1

    return 0


saiobj.g_func_map['ma50'] = ma50_run


if __name__=="__main__":
    sailog_set("ma50.log")

    db = db_init()
    saiobj.g_db = db

    sai_load_conf2('wine.cfg')

    # saiobj.g_to_send_mail = True
    sailog_set_info()
    sailog_set_debug()

    one = True
    one = False

    if one:

        # 水晶光电
        trade_dt = '2019-07-17'
        stock_id = '002273'


        sai_fmt_set_fetch_len(220)
        df = sai_fmt_simple(stock_id, trade_dt, db)
        ma50_run()
    else:
        check_list = [
                ########################################################
                ########################################################

                ['600051', '2020-04-27', 1],  # 宁波联合
                ['603533', '2020-04-02', 1],  # 掌趣科技
                ]
        idx = 0
        for item in check_list:
            log_debug("-" * 60)
            stock_id = item[0]
            trade_dt = item[1]
            expect   = item[2]
            log_debug("idx: %dth, stock_id: %s, trade_date: %s, expect: %d", idx, stock_id, trade_dt, expect)

            sai_fmt_set_fetch_len(220)
            df = sai_fmt_simple(stock_id, trade_dt, db)
            rv = ma50_run()
            if rv != expect:
                log_error("sorry: NOT match: %s, %s, %d", stock_id, trade_dt, expect)
                break
            else:
                log_info("nice, RE got matched: %s, %s, %d", stock_id, trade_dt, expect)

            log_debug("-" * 60)
            idx += 1

        if idx == len(check_list):
            log_info("bingo: all matched")


    db_end(db)

    log_debug("--end")


# ma50.py
