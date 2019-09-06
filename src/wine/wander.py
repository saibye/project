#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *
from pub    import *


# 缺口+放量+徘徊+突破
# code at 2019-8-28
# 002273 水晶光电 20190717
# 601595 上海电影 2019-08-16
# 300735 光弘科技 2019-07-24 TODO

def wander_load_cfg():
    #log_debug('wander config loaded')
    pass



def wander_run():
    body = ''

    stock_id  = ref_id(0)
    this_date = ref_date(0)

    log_info('TRAN wander: %s -- %s', stock_id, this_date)

    length = ref_len()
    if length < 220:
        return 0

    wander_load_cfg()

    ################################################################
    ################################################################
    # BREAK day

    # 突破日: 放量
    k = 0
    rate0 = 100.00 * (ref_close(k) - ref_close(k+1)) / ref_close(k+1)
    # log_debug("GAP-DAY: rate0: %.2f%%", rate0)

    # 量比
    vr50 = ref_vol(k) / ref_vma50(k)
    vr10 = ref_vol(k) / ref_vma10(k)
    vr5  = ref_vol(k) / ref_vma5(k)
    body += "vr50: %.2f\n" % (vr50)
    body += "vr10: %.2f\n" % (vr10)
    body += "vr5 : %.2f\n" % (vr5)

    # log_debug("BREAK-DAY: vr50: %.2f", vr50)
    # log_debug("BREAK-DAY: vr10: %.2f", vr10)
    # log_debug("BREAK-DAY: vr5 : %.2f", vr5)

    counter = 0
    if vr50 >= 2:
        counter += 1
    if vr10 >= 2:
        counter += 1
    if vr5 >= 2:
        counter += 1

    vr_rule = counter >= 2
    # log_debug("BREAK-DAY: vr rule: %s, %d", vr_rule, counter)
    if vr_rule:
        pass
    else:
        log_info("sorry, BREAK-DAY vr not exeed 2")
        return 0


    ################################################################
    ################################################################

    # 突破天数

    ## 价突破天数
    price_break_days= wine_close_break_days2(k, 200)
    price_break_rule= price_break_days >= 50

    if price_break_rule:
        log_debug("BREAK-DAY: price break enough days: %d", price_break_days)
        pass
    else:
        log_info("sorry, price break(2) days too small: %d", price_break_days)
        return 0

    ################################################################
    ################################################################
    # GAP day

    # exist GAP and volume
    width = 30
    gap_rate, gap_idx = wine_find_previous_gap(k, width)
    if gap_idx < 0:
        log_info("sorry, not found gap: %d", width)
        return 0
    else:
        log_debug("GAP: %dth, %.2f%%, at %s", gap_idx, gap_rate, ref_date(gap_idx))

    # gap-rate
    gap_rate_rule = gap_rate > 5
    if gap_rate_rule:
        log_info("GAP-DAY rise enough: %.2f%%", gap_rate)
        pass
    else:
        log_info("sorry, gap_rate too small: %.2f", gap_rate)
        return 0

    # at least 10 days
    if gap_idx < 10:
        log_info("sorry, wander too short: %d", gap_idx)
        return 0


    # 量比(1)
    k = gap_idx
    vr50 = ref_vol(k) / ref_vma50(k)
    vr10 = ref_vol(k) / ref_vma10(k)
    vr5  = ref_vol(k) / ref_vma5(k)

    log_debug("GAP-DAY(1): vr50: %.2f", vr50)
    log_debug("GAP-DAY(1): vr10: %.2f", vr10)
    log_debug("GAP-DAY(1): vr5 : %.2f", vr5)

    counter = 0
    if vr50 >= 2:
        counter += 1
    if vr10 >= 2:
        counter += 1
    if vr5 >= 2:
        counter += 1

    gap_vr_rule1 = counter >= 2
    log_debug("GAP-DAY(1): gap-vr rule: %s", gap_vr_rule1)


    # 量比(2)
    k = gap_idx-1
    vr50 = ref_vol(k) / ref_vma50(k)
    vr10 = ref_vol(k) / ref_vma10(k)
    vr5  = ref_vol(k) / ref_vma5(k)

    log_debug("GAP-DAY(2): vr50: %.2f", vr50)
    log_debug("GAP-DAY(2): vr10: %.2f", vr10)
    log_debug("GAP-DAY(2): vr5 : %.2f", vr5)

    counter = 0
    if vr50 >= 2:
        counter += 1
    if vr10 >= 2:
        counter += 1
    if vr5 >= 2:
        counter += 1

    gap_vr_rule2 = counter >= 2
    log_debug("GAP-DAY(2): gap-vr rule: %s", gap_vr_rule2)

    # has volume around GAP day
    gap_vr_rule = gap_vr_rule1 or gap_vr_rule2
    if gap_vr_rule:
        log_info("GAP-DAY has volume!")
    else:
        log_info("GAP-DAY no volume!")
        return 0

    ################################################################
    ################################################################
    # deviation
    devia_rate = 100.00 * (ref_close(0) - ref_close(gap_idx)) / ref_close(gap_idx)
    # log_debug("devia-rate: %.2f%%", devia_rate)
    devia_rule = devia_rate < 3
    if devia_rule:
        log_info("devia rate is nearby: %.2f%%", devia_rate)
    else:
        log_info("sorry, devia rate too high: %.2f%%", devia_rate)
        return 0


    # cmd rule
    cmp_rule= ref_close(0) > ref_close(gap_idx) and ref_high(0) > ref_high(gap_idx)
    if cmp_rule:
        log_debug("cmp-rule: %s", cmp_rule)
    else:
        log_info("sorry, cmp rule not match")
        return 0


    ################################################################
    ################################################################
    # 3 day after GAP
    # TODO

    ################################################################
    ################################################################


    # ma20 ascending
    ma20_ascend = ref_ma20(0) > ref_ma20(14) and ref_ma20(5) > ref_ma20(15)
    # log_debug("ma20 asceding: %s", ma20_ascend)
    if ma20_ascend:
        log_debug("ma20 asceding: %s", ma20_ascend)
    else:
        log_info("sorry, ma20 not ascending")
        return 0


    # exceed ma50
    k = gap_idx
    ma50_rule = ref_close(k) > ref_ma50(k)
    # log_debug("exceed ma50 : %s",  ma50_rule)

    if ma50_rule:
        log_info("ma50 rule mached")
    else:
        log_info("sorry, need break ma50, %.2f vs %.2f", ref_close(k), ref_ma50(k))
        return 0

    ################################################################
    ################################################################
    # box

    # avg & std
    width = gap_idx - 0 - 1
    avg, std = wine_region_calculation(0, width)
    log_info("avg: %.2f, std: %.2f", avg, std)
    std_rule = std < 0.08
    if std_rule:
        log_info("std rule is low enough: %.2f", std)
    else:
        log_info("sorry, std too high: %.2f", std)
        return 0


    # avg-rate
    avg_rate = 100.00 * (ref_close(0) - avg) / avg
    # log_debug("avg-rate: %.2f%%", avg_rate)
    avg_rate_rule = avg_rate < 6
    if avg_rate_rule:
        log_info("avg rate is nearby: %.2f%%", avg_rate)
    else:
        log_info("sorry, avg rate too high: %.2f", avg_rate)
        return 0


    # fish
    width = gap_idx - 0
    fish_list = wine_find_fish(0, width)
    log_debug("%s", fish_list)
    fish_rule = len(fish_list) == 3 and fish_list[0] >= 2 and fish_list[1] <= -2 and fish_list[2] >= 5
    if fish_rule:
        log_info("is a fish!")
        pass
    else:
        log_info("sorry, not a fish: %s", fish_list)
        return 0


    # near ma20
    width = gap_idx - 0
    near_rate, near_idx =  wine_near_with_ma20(0, width)
    near_rule = near_rate < 1
    if near_rule:
        log_info("near_ma20: %.2f%%, %s", near_rate, ref_date(near_idx))
    else:
        log_info("sorry, far from ma20: %.2f%%", near_rate)
        return 0


    ################################################################
    ################################################################
    ################################################################
    ################################################################



    if True:
        log_info('bingo: %s -- %s', stock_id, this_date)
        wine_mail('wander', body)
        return 1

    return 0


saiobj.g_func_map['wander'] = wander_run


if __name__=="__main__":
    sailog_set("wander.log")

    db = db_init()
    saiobj.g_db = db

    sai_load_conf2('wine.cfg')

    # saiobj.g_to_send_mail = True

    one = True
    one = False

    if one:

        # 水晶光电
        trade_dt = '2019-07-17'
        stock_id = '002273'


        sai_fmt_set_fetch_len(220)
        df = sai_fmt_simple(stock_id, trade_dt, db)
        wander_run()
    else:
        check_list = [
                ########################################################
                ########################################################

                ['002273', '2019-07-17', 1],  # 水晶光电
                ['601595', '2019-08-16', 1],  # 上海电影
                ['300735', '2019-07-24', 0],  # 光弘科技 # 
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
            rv = wander_run()
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


# wander.py
