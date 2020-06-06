#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *
from pub    import *


# 倍量
# code at 2020-4-12
# 格力电器 2019-1-15

def doub_load_cfg():
    log_debug('doub config loaded')



def doub_run():
    stars= ''
    body = ''

    stock_id  = ref_id(0)
    this_date = ref_date(0)

    log_info('TRAN doub: %s -- %s', stock_id, this_date)

    length = ref_len()
    if length < 110:
        log_debug("days too short: %d", length)
        return 0

    doub_load_cfg()

    # 
    k = 0
    rate  = 100.00 * (ref_close(k) - ref_close(k+1)) / ref_close(k+1)
    body += 'rate(0): %.2f%%\n' % rate
    log_debug("DOUB-DAY: rate: %.2f%%", rate)

    # 量比
    vr  = ref_vol(k) / ref_vol(k+1)
    vr_rule = vr >= 1.99

    log_debug("DOUB-DAY: %s vr: %.2f", stock_id, vr)

    if vr_rule:
        body += 'vr(0): %.2f\n' % (vr)
        pass
    else:
        log_debug("sorry, vr not exeed 2: %.2f", vr)
        return 0

    ################################################################
    ################################################################
    # 价格在 ma50 附近
    price_rule = ref_close(0) >= ref_ma50(0)
    if price_rule:
        pass
    else:
        log_debug("sorry, price not satisfied")
        return 0


    ################################################################
    ################################################################

    count = 0
    cost_days = 0
    sum_vr = 0.0
    sum_de = 0.0
    sum_rt = 0.0

    width = 30
    for i in range(width):
        if i + 1 >= ref_len():
            log_error('error: too short: %d < %d', i+1, ref_len())
            return 0

        vr = 1.0 *  ref_vol(i) / ref_vol(i+1)
        rt = 100.00*(ref_close(i) - ref_close(i+1)) / ref_close(i+1)
        rt50= 100.00*(ref_close(i) - ref_ma50(i)) / ref_ma50(i)
        if rt > 0 and vr > 1.99:
            count  += 1
            sum_vr += vr
            sum_rt += rt
            sum_de += rt50
            body += '(%d)%s: vr: %.2f, rt: %.2f%%\n' % (count, ref_date(i), vr, rt)
            # log_debug("[%s, %s, %d/%d] => vr: %.2f, rate: %.2f%%", ref_id(i), ref_date(i), count, i+1, vr, rt)

            if count == 4:
                cost_days = i

    if count == 0:
        log_debug("sorry, no volume doubled")
        return 0

    avg_vr = sum_vr/count
    avg_rt = sum_rt/count
    avg_de = abs(sum_de)/count

    body += 'avg-vr:   %.2f\n'    % avg_vr
    body += 'avg-rt:   %.2f\n'    % avg_rt
    body += 'avg-rt50: %.2f%%\n'  % avg_de
    body += 'cost_days: %d\n'  % cost_days
    log_debug("from[%s] => %d, avg(vr): %.2f, avg(de): %.2f%%, avg(rt): %.2f%%, 4cost: %d",
            ref_date(i), count, avg_vr, avg_de, avg_rt, cost_days)


    stat_rule = count >= 4 and avg_vr > 3.0 and avg_rt > 3.2 and avg_de < 1.2
    if stat_rule:
        pass
    else:
        log_debug("sorry, stat not satisfied: %d, %.2f, %.2f%%", count, avg_vr, avg_rt)
        return 0

    if cost_days < 30:
        stars += '*'

    if count > 5:
        stars += '*'

    if avg_rt > 3:
        stars += '*'

    if avg_rt > 5:
        stars += '*'

    if avg_de < 1:
        stars += '*'



    ################################################################
    ################################################################
    # 深幅下跌 ?


    ################################################################
    ################################################################


    if True:
        saimail_set_subject_prefix(stars)
        log_info('bingo: %s -- %s', stock_id, this_date)
        wine_mail('doub', body)
        return 1

    return 0


saiobj.g_func_map['doub'] = doub_run


if __name__=="__main__":
    sailog_set("doub.log")

    db = db_init()
    saiobj.g_db = db

    sai_load_conf2('wine.cfg')

    # saiobj.g_to_send_mail = True
    sailog_set_info()
    sailog_set_debug()

    one = True
    one = False

    if one:
        # 格力电器
        trade_dt = '2019-01-15'
        stock_id = '000651'

        sai_fmt_set_fetch_len(220)
        df = sai_fmt_simple(stock_id, trade_dt, db)
        doub_run()
    else:
        check_list = [
                # 
                ['000651', '2019-01-15', 1],  # 格力电器
                ['002273', '2019-07-17', 1],  # 水晶光电
                ['000725', '2019-02-11', 1],  # X
                ['000725', '2016-10-10', 1],  # X
                ['000725', '2019-11-26', 1],  # X
                ['601668', '2016-07-04', 1],  # 中国建筑

                #  TODO
                ['601012', '2018-11-01', 1],  # 隆基股份  ...
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
            if df is None:
                log_error("sorry: sai_fmt_simple lack data: %s, %s", stock_id, trade_dt)
                break

            rv = doub_run()
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


# doub.py
