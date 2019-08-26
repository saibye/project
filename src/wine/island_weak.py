#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *
from pub    import *


# 岛 -- 弱化
# code at 2019-2-28
# 000526 紫光学大

def island2_load_cfg():
    saiobj.g_wine_start_rate= float(sai_conf_get2('island_weak', 'start_rate'))
    saiobj.g_wine_step      = int(sai_conf_get2('island_weak', 'find_step'))
    #log_debug('island_weak config loaded')



def island2_run():
    body = ''

    stock_id  = ref_id(0)
    this_date = ref_date(0)

    log_debug('TRAN island_weak: %s -- %s', stock_id, this_date)

    length = ref_len()
    if length < 30:
        return 0

    island2_load_cfg()

    lowX = ref_low(0) 

    if lowX > ref_high(1):
        # log_info ("有缺口: %s -- %s", stock_id, this_date)
        pass
    else:
        # log_debug("无缺口: %s -- %s", stock_id, this_date)
        return 0

    # 取跳空幅度
    gap_rateX = 100.00 * (ref_low(0) - ref_high(1)) / ref_high(1)
    body += '缺口X: %.2f%%\n' % (gap_rateX)

    # log_info("gapX: %.2f%%",  gap_rateX)

    if gap_rateX > 0.5:
        # log_info("gapX: %.2f%%",  gap_rateX)
        pass
    else:
        log_debug("gapX: %.2f%% too small",  gap_rateX)
        return 0

    # 涨幅
    rateX = 100.00 * (ref_close(0) - ref_close(1)) / ref_close(1)
    # log_debug("rateX: %.2f%%", rateX)
    body += '涨幅X: %.2f%%\n' % (rateX)

    START_RATE = saiobj.g_wine_start_rate
    if rateX < START_RATE:
        log_info('start rateX too small: %.2f%% > %.2f%%', rateX, START_RATE)
        return 0


    # 取向下的缺口
    STEP = saiobj.g_wine_step
    pair_day, region_high = wine_island_exist(1, STEP)
    if pair_day < 0:
        log_debug("不是岛")
        return 0

    # 检查价格相近
    rateS = 100.00 * abs(ref_close(0) - ref_close(pair_day)) / ref_close(0)
    log_debug("rate-Compare: %.2f%%", rateS)


    # 岛的起点，要跌破所有均线
    close_price = ref_close(pair_day)
    press_rule =  close_price  < ref_ma5(pair_day) and \
        close_price < ref_ma10(pair_day) and \
        close_price < ref_ma20(pair_day)
    if not press_rule:
        log_debug("未压制")
        return 0



    # 岛的起点下沉缺口大小
    gap_rateY = 100.00 * (ref_low(pair_day) - ref_high(pair_day-1)) /  ref_high(pair_day-1)
    body += '缺口Y: %.2f%%\n' % (gap_rateY)
    log_info("gapY: %.2f%%",  gap_rateY)

    if gap_rateY >= 0.15:
        log_info("gapY: %.2f%%",  gap_rateY)
    else:
        log_debug("gapY: %.2f%% too small",  gap_rateY)
        return 0


    # 岛的起点下沉跌幅
    rateY = 100.00 * (ref_close(pair_day-1) - ref_close(pair_day)) / ref_close(pair_day)
    log_debug("rateY: %.2f%%", rateY)
    body += '涨幅Y: %.2f%%\n' % (rateY)

    # 岛的起点跌幅
    rateZ = 100.00 * (ref_close(pair_day) - ref_close(pair_day+1)) / ref_close(pair_day+1)
    log_debug("rateZ: %.2f%%", rateZ)
    body += '涨幅Z: %.2f%%\n' % (rateZ)


    k = 0
    vr50 = ref_vol(k) / ref_vma50(k)
    vr10 = ref_vol(k) / ref_vma10(k)
    vr5  = ref_vol(k) / ref_vma5(k)
    body += "vr50: %.2f\n" % (vr50)
    body += "vr10: %.2f\n" % (vr10)
    body += "vr5 : %.2f\n" % (vr5)
    log_debug("ISLAND: vr50: %.2f", vr50)
    log_debug("ISLAND: vr10: %.2f", vr10)
    log_debug("ISLAND: vr5 : %.2f", vr5)

    counter = 0
    if vr50 >= 2:
        counter += 1

    if vr10 >= 2:
        counter += 1

    if vr5  >= 2:
        counter += 1

    log_debug("量比超过2的天数: %d", counter)
    if counter >= 2:
        pass
    else:
        log_info("无量，取消: %d", counter)
        return 0


    if True:
        log_info('bingo: %s -- %s', stock_id, this_date)
        wine_mail('island_weak', body)
        return 1

    return 0


saiobj.g_func_map['island_weak'] = island2_run


if __name__=="__main__":
    sailog_set("island_weak.log")

    db = db_init()
    saiobj.g_db = db

    sai_load_conf2('wine.cfg')


    # saiobj.g_to_send_mail = True


    check_list = [
            ['000526', '2018-10-29', 1],  # 紫光学大
            ['600369', '2018-10-23', 1],  # 西南证券
            ['601375', '2018-10-23', 1],  # 中原证券
            ['601990', '2018-10-23', 1],  # 南京证券
            ['300010', '2019-01-31', 1],  # 立思辰
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
        rv = island2_run()
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


# island_weak2.py
