#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *
from pub    import *


# 夹紧 convergence
# ma50 + ma200
# code at 2020-4-8
#

def conv_load_cfg():
    # saiobj.g_wine_vol_break = int(sai_conf_get2('conv', 'volume_break_day'))
    # saiobj.g_wine_upper_edge= float(sai_conf_get2('conv', 'upper_edge'))
    log_debug('conv config loaded')



def conv_run():
    stars= ''
    body = ''

    stock_id  = ref_id(0)
    this_date = ref_date(0)

    log_info('TRAN conv: %s -- %s', stock_id, this_date)

    length = ref_len()
    if length < 240:
        # log_debug("days too short: %d", length)
        return 0

    conv_load_cfg()


    k = 0
    break_rule = ref_close(k) >= ref_ma50(k) and ref_close(k+1) <= ref_ma50(k+1)
    if break_rule:
        pass
    else:
        log_debug("sorry, (conv)not just break")
        return 0

    ################################################################
    ################################################################

    k = 1
    a = ref_ma50(k)
    b = ref_ma200(k)
    rate = 100.00 * min(a, b) / max(a, b)
    if rate >= 97:
        pass
    else:
        log_debug("sorry, (conv)not near enough: %.2f%%", rate)
        return 0


    ################################################################
    ################################################################
    # days = wine_ma50_above_ma200_days(1, 100)
    # log_info("conv(%s): above(ma50, ma200): %d", stock_id, days)

    baseline = 90.0
    days = wine_ma50_near_ma200_days(1, 100, baseline)
    # log_info("conv(%s): near(ma50, ma200) > %.2f: %d", stock_id, baseline, days)
    if days >= 40:
        pass
    else:
        log_debug("sorry, (conv)recent not near(90%%) enough: %d", days)
        return 0

    baseline = 85.0
    days = wine_ma50_near_ma200_days(1, 100, baseline)
    # log_info("conv(%s): near(ma50, ma200) > %.2f: %d", stock_id, baseline, days)
    if days >= 70:
        pass
    else:
        log_debug("sorry, (conv)recent not near(85%%) enough: %d", days)
        return 0

    ################################################################
    width = 50
    days = wine_ma200_ascending_days(1, width)
    ascend_rule = days >= 49
    if ascend_rule:
        pass
    else:
        log_debug("sorry, ma200 not ascending: %d", days)
        return 0

    ################################################################
    width = 30
    days = wine_ma50_close_ma200_days(1, width)
    # log_debug("conv(%s): inner(ma50, ma200): %d/%d", stock_id, days, width)
    if days >= 15:
        log_info("conv: rank++")
    else:
        log_debug("conv: too jump: %d", days)

    ################################################################
    ################################################################
    ################################################################
    ################################################################

    if True:
        saimail_set_subject_prefix(stars)
        log_info('bingo: %s -- %s', stock_id, this_date)
        wine_mail('conv', body)
        return 1

    return 0


saiobj.g_func_map['conv'] = conv_run


if __name__=="__main__":
    sailog_set("conv.log")

    db = db_init()
    saiobj.g_db = db

    sai_load_conf2('wine.cfg')

    # saiobj.g_to_send_mail = True

    one = True
    one = False

    if one:
        # 腾博股份
        trade_dt = '2019-08-05'
        stock_id = '300363'

        sai_fmt_set_fetch_len(220)
        df = sai_fmt_simple(stock_id, trade_dt, db)
        conv_run()
    else:
        check_list = [
                # ma50 > ma200
                ['002058', '2019-09-05', 1],  # 威尔泰
                ['000100', '2019-11-25', 1],  # TCL
                ['000725', '2019-11-26', 1],  # X
                ['000063', '2019-12-12', 1],  # 中兴通信
                ['601066', '2019-12-13', 1],  # 中信建投

                # ma200 > ma50
                ['600127', '2020-03-23', 1],  # 金健米业

                ]
        idx = 0
        for item in check_list:
            log_debug("-" * 60)
            stock_id = item[0]
            trade_dt = item[1]
            expect   = item[2]
            log_debug("idx: %dth, stock_id: %s, trade_date: %s, expect: %d", idx, stock_id, trade_dt, expect)

            sai_fmt_set_fetch_len(300)
            df = sai_fmt_simple(stock_id, trade_dt, db)
            if df is None:
                log_error("sorry: sai_fmt_simple lack data: %s, %s", stock_id, trade_dt)
                break

            rv = conv_run()
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


# conv.py
