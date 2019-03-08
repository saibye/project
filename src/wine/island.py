#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *
from pub    import *


# 岛
# code at 2019-2-16
# 300250 初灵信息
# 000616 海航投资

def island_load_cfg():
    saiobj.g_wine_start_rate= float(sai_conf_get2('island', 'start_rate'))
    saiobj.g_wine_step      = int(sai_conf_get2('island', 'find_step'))
    #log_debug('island config loaded')



def island_run():
    body = ''

    stock_id  = ref_id(0)
    this_date = ref_date(0)

    log_debug('TRAN island: %s -- %s', stock_id, this_date)

    length = ref_len()
    if length < 30:
        return 0

    island_load_cfg()

    lowX = ref_low(0) 

    if lowX > ref_high(1):
        log_info ("有缺口: %s -- %s", stock_id, this_date)
    else:
        # log_debug("无缺口: %s -- %s", stock_id, this_date)
        return 0

    # 取跳空幅度
    gap_rateX = 100.00 * (ref_low(0) - ref_high(1)) / ref_high(1)
    body += '缺口X: %.2f%%\n' % (gap_rateX)

    if gap_rateX > 1.0:
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
        # log_info('start rateX too small: %.2f%% < %.2f%%', rateX, START_RATE)
        return 0


    # 取向下的缺口
    STEP = saiobj.g_wine_step
    pair_day, region_high = wine_island_exist(1, STEP)
    if pair_day < 0:
        log_debug("不是岛")
        return 0

    # 检查一致性缺口
    if region_high > lowX:
        log_debug("sorry: ref_low(0) < region_highest...")
        return 0

    # 检查价格相近
    rateS = 100.00 * abs(ref_close(0) - ref_close(pair_day)) / ref_close(0)
    log_debug("rate-Compare: %.2f%%", rateS)


    # 岛的起点，要跌破所有均线 TODO
    close_price = ref_close(pair_day)
    press_rule =  close_price  < ref_ma5(pair_day) and \
        close_price < ref_ma10(pair_day) and \
        close_price < ref_ma20(pair_day) and \
        close_price < ref_ma50(pair_day)
    if not press_rule:
        log_debug("未压制")
        return 0



    # 岛的起点下沉缺口大小
    gap_rateY = 100.00 * (ref_low(pair_day) - ref_high(pair_day-1)) /  ref_high(pair_day-1)
    body += '缺口Y: %.2f%%\n' % (gap_rateY)

    if gap_rateY > 1.0:
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



    if True:
        log_info('bingo: %s -- %s', stock_id, this_date)
        wine_mail('island', body)
        return 1

    return 0


saiobj.g_func_map['island'] = island_run


if __name__=="__main__":
    sailog_set("island.log")

    db = db_init()
    saiobj.g_db = db

    sai_load_conf2('wine.cfg')


    # bad1
    trade_dt = '2019-01-18'
    stock_id = '300116'

    # bad2
    trade_dt = '2019-01-03'
    stock_id = '603016'

    # saiobj.g_to_send_mail = True

    # 海航投资
    trade_dt = '2018-10-15'
    stock_id = '000616'

    # 初灵信息
    trade_dt = '2019-01-31'
    stock_id = '300250'

    # bad3
    trade_dt = '2018-10-15'
    stock_id = '603008'

    # bad4
    trade_dt = '2018-10-15'
    stock_id = '300638'

    # 东方金钰
    trade_dt = '2019-02-11'
    stock_id = '600086'

    sai_fmt_set_fetch_len(200)
    df = sai_fmt_simple(stock_id, trade_dt, db)
    island_run()

    db_end(db)

    log_debug("--end")


# island.py
