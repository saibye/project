#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *
from pub    import *


# 立桩量 + 量升价索 + ma200
# code at 2019-8-23
# 300363 腾博股份 20190805

def pile_load_cfg():
    saiobj.g_wine_vol_break = int(sai_conf_get2('pile', 'volume_break_day'))
    saiobj.g_wine_pri_break = int(sai_conf_get2('pile', 'price_break_day'))
    saiobj.g_wine_lower_edge= float(sai_conf_get2('pile', 'lower_edge'))
    saiobj.g_wine_upper_edge= float(sai_conf_get2('pile', 'upper_edge'))
    #log_debug('pile config loaded')



def pile_run():
    stars= ''
    body = ''

    stock_id  = ref_id(0)
    this_date = ref_date(0)

    log_info('TRAN pile: %s -- %s', stock_id, this_date)

    length = ref_len()
    if length < 220:
        # log_debug("days too short: %d", length)
        return 0

    pile_load_cfg()


    # 立桩日: 放量
    k = 3
    rate3 = 100.00 * (ref_close(k) - ref_close(k+1)) / ref_close(k+1)
    # log_debug("PILE-DAY: rate3: %.2f%%", rate3)

    # 量比
    vr50 = ref_vol(k) / ref_vma50(k)
    vr10 = ref_vol(k) / ref_vma10(k)
    vr5  = ref_vol(k) / ref_vma5(k)
    vr_rule = vr50 >= 2 and vr10 >= 2 and vr5 >= 2

    log_debug("PILE-DAY: %s vr50: %.2f", stock_id, vr50)
    log_debug("PILE-DAY: %s vr10: %.2f", stock_id, vr10)
    log_debug("PILE-DAY: %s vr5 : %.2f", stock_id, vr5)
    log_debug("PILE-DAY: vr rule: %s", vr_rule)

    if vr_rule:
        pass
    else:
        log_debug("sorry, vr not exeed 2")
        return 0


    ################################################################
    ################################################################

    # 突破天数
    ## 量突破天数
    vol_break_days  = wine_volume_break_days(k, 200)
    vol_break_rule  = vol_break_days >= saiobj.g_wine_vol_break
    log_debug("PILE-DAY: %s volume break days: %d, rule: %s", stock_id, vol_break_days, vol_break_rule)
    body += "volume break days: %d+++\n" % (vol_break_days)

    if vol_break_rule:
        pass
    else:
        log_info("sorry, volume break days too small: %d", vol_break_days)
        return 0

    # STAR
    if vol_break_days >= 200:
        stars += "**"
    elif vol_break_days >= 100:
        stars += "*"

    ## 量排名
    vol_rank = wine_volume_rank(k, 100)
    body += "volume rank: %dth--\n" % (vol_rank)
    # log_debug("PILE-DAY: %s volume rank: %d", stock_id, vol_rank)
    rank_rule = vol_rank <= 5
    if rank_rule:
        pass
    else:
        log_info("sorry, volume rank is high: %d", vol_rank)
        return 0

    if vol_rank <= 1:
        stars += '*'


    body += "vr50: %.2f++\n" % (vr50)
    body += "vr10: %.2f\n" % (vr10)
    body += "vr5 : %.2f\n" % (vr5)

    ## 价突破天数
    price_break_days= wine_close_break_days2(k, 200)
    price_break_rule= price_break_days >= saiobj.g_wine_pri_break
    # log_debug("PILE-DAY: price  break days: %d, rule: %s", price_break_days, price_break_rule)

    if price_break_rule:
        pass
    else:
        if vr50 > 4:
            price_break_days   = wine_close_break_days2(k-1, 200)
            if price_break_days >= saiobj.g_wine_pri_break:
                pass
            else:
                log_info("sorry, price break(2) days too small: %d", price_break_days)
                return 0
        elif ref_close(0) > ref_close(1) and ref_close(1) > ref_close(2):
            price_break_days   = max(wine_close_break_days2(0, 200),
                    wine_close_break_days2(1, 200),
                    wine_close_break_days2(2, 200))
            if price_break_days >= saiobj.g_wine_pri_break:
                pass
            else:
                log_info("sorry, price break(2) days too small: %d", price_break_days)
                return 0
        else:
            log_info("sorry, price break(1) days too small: %d", price_break_days)
            return 0


    ################################################################
    ################################################################

    # near ma200
    near200_rate, near200_day = wine_near_with_ma200(k, 8)
    # log_debug("nearest to ma200: %dth, %.2f", near200_day, near200_rate)
    near200_rule = near200_rate < 2


    # near ma50
    near50_rate, near50_day = wine_near_with_ma50(k, 8)
    # log_debug("nearest to ma50: %dth, %.2f", near50_day, near50_rate)
    near50_rule = near50_rate < 3


    near_price = 1.0
    if near200_rule and near50_rule:
        log_info("near to both ma200 and ma50")
        near_price = ref_close(near200_day)
    elif near200_rule:
        log_info("near to only ma200")
        near_price = ref_close(near200_day)
    elif near50_rule:
        log_debug("near to only ma50")
        near_price = ref_close(near50_day)
    else:
        log_info("sorry, far from ma200 and ma50: %.2f, %.2f", near200_rate, near50_rate)
        return 0

    devia_rate = 100.00 * (ref_close(0) - near_price) / near_price
    log_debug("devia_rate: %.2f%%", devia_rate)
    devia_rule = devia_rate < 20.0
    if devia_rule:
        pass
    else:
        log_info("sorry, deviate a lot: %.2f%%", devia_rate)
        return 0


    # ma20 ascending
    ma20_ascend = ref_ma20(4) > ref_ma20(24) and ref_ma20(6) > ref_ma20(26)
    # log_debug("ma20 asceding: %s(opt)", ma20_ascend)
    if ma20_ascend:
        stars += '*'
        pass


    # ma5, 10, 20, 50, 200 twist
    cross5_rate, cross5_day = wine_ma_twist_5line(k, 7)
    cross5_rule = cross5_rate < 3
    # log_debug("ma cross5 at %dth, %.2f%%", cross5_day, cross5_rate)
    if cross5_rule:
        stars += '*'
        pass


    # ma5, 10, 20, 50 twist
    cross4_rate, cross4_day = wine_ma_twist_4line(k, 7)
    cross4_rule = cross4_rate < 3
    # log_debug("ma cross4 at %dth, %.2f%%", cross4_day, cross4_rate)
    if cross4_rule:
        # XXX: add star
        pass

    # ma5 vs ma10 twisted
    twist_rate, twist_day = wine_ma5_twist_ma10(k, 7)
    twist_rule = twist_rate < 1
    # log_debug("ma5 twist ma10 at: %dth, %.2f%%", twist_day, twist_rate)
    if twist_rule:
        pass
    else:
        log_info("sorry, ma5/ma10 too far: %.2f%%", twist_rate)
        return 0

    # exceed ma200
    exceed_ma200 = ref_close(k) > ref_ma200(k)
    # log_debug("exceed ma200: %s", exceed_ma200)

    # exceed ma50
    exceed_ma50  = ref_close(k) > ref_ma50(k)
    # log_debug("exceed ma50 : %s",  exceed_ma50)

    ma200_rule = near200_rule and exceed_ma200
    ma50_rule  = near50_rule  and exceed_ma50

    if ma200_rule and ma50_rule:
        log_info("both ma200 and ma50 rule mached")
    elif ma200_rule:
        log_info("ma200 rule mached")
    elif ma50_rule:
        log_info("ma50  rule mached")
    else:
        log_info("sorry, need break ma200")
        return 0


    ################################################################
    ################################################################
    ################################################################
    ################################################################

    # recent 3 day

    k = 0

    ## avg(vol(0, 1, 2)   < vol(3)
    avg_vol     = (ref_vol(k) + ref_vol(k+1) + ref_vol(k+2)) / 3
    avg_vr      = 100.00 * avg_vol / ref_vol(k+3)
    avg_vr_rule = avg_vr < 100
    # log_debug("3day: VOLUME: avg: %.2f,\tvr: %.2f%%,\trule: %s", avg_vol, avg_vr, avg_vr_rule)
    if avg_vr_rule:
        pass
    else:
        log_info("sorry, avg(vol) not shink: %.2f%%", avg_vr)
        return 0


    ## avg(price(0, 1, 2) >= price(3)
    avg_price   = (ref_close(k) + ref_close(k+1) + ref_close(k+2)) / 3
    avg_pr      = 100.00 * avg_price / ref_close(k+3)
    avg_pr_rule = avg_pr > 100
    # log_debug("3day: PRICE : avg: %.2f,\tpr: %.2f%%,\trule: %s", avg_price, avg_pr, avg_pr_rule)
    if avg_pr_rule:
        pass
    else:
        log_debug("sorry, avg(price) not high enough: %.2f%%", avg_pr)
        return 0

    ## price ascending
    price_rule_opt  = ref_close(k) >= ref_close(k+1) and ref_close(k+1) >= ref_close(k+2)
    # log_debug("3day: PRICE ascending rule: %s(opt)", price_rule_opt)
    if price_rule_opt:
        stars += '*'
        pass

    ## edge
    max_price   = max(ref_close(k), ref_close(k+1), ref_close(k+2))
    min_price   = min(ref_close(k), ref_close(k+1), ref_close(k+2))
    upper_edge  = 100.00 * (max_price - ref_close(k+3)) / ref_close(k+3)
    lower_edge  = 100.00 * (min_price - ref_close(k+3)) / ref_close(k+3)
    upper_edge_rule = upper_edge < saiobj.g_wine_upper_edge
    lower_edge_rule = lower_edge > saiobj.g_wine_lower_edge
    # log_debug("3day: UPPER-edge: %.2f%%, rule: %s", upper_edge, upper_edge_rule)
    # log_debug("3day: LOWER-edge: %.2f%%, rule: %s", lower_edge, lower_edge_rule)
    if upper_edge_rule and lower_edge_rule:
        pass
    else:
        log_info("sorry, upper_edge(%.2f%%) or lower_edge(%.2f%%) not match", upper_edge, lower_edge)
        return 0

    ## has volume
    v0_rule     = ref_vol(0) >= max(ref_vma10(0), ref_vma50(0))
    v1_rule     = ref_vol(1) >= max(ref_vma10(1), ref_vma50(1))
    v2_rule     = ref_vol(2) >= max(ref_vma10(2), ref_vma50(2))
    # log_debug("3day: VOLUME has: %s, %s, %s", v0_rule, v1_rule, v2_rule)
    if v0_rule and v1_rule and v2_rule:
        pass
    else:
        log_info("sorry, volume too small")
        return 0

    ## sum(rate(0, 1, 2)  < 10%
    total_rate  = 100.00 * (ref_close(0) - ref_close(3)) / ref_close(3)
    total_rate_rule = total_rate < 10
    # log_debug("3day: TOTAL-rate: %.2f%%, rule: %s", total_rate, total_rate_rule)
    if total_rate_rule:
        pass
    else:
        log_info("sorry, total-rate too big")
        return 0

    ## max(rate(0, 1, 2)  < 6%
    k = 0
    rate0 = 100.00 * (ref_close(k) - ref_close(k+1)) / ref_close(k+1)

    k = 1
    rate1 = 100.00 * (ref_close(k) - ref_close(k+1)) / ref_close(k+1)

    k = 2
    rate2 = 100.00 * (ref_close(k) - ref_close(k+1)) / ref_close(k+1)
    # log_debug("3day: rate2: %.2f%%, rate1: %.2f%%, rate0: %.2f%%", rate2, rate1, rate0)

    max_rate = max(rate0, rate1, rate2)
    min_rate = min(rate0, rate1, rate2)
    max_rate_rule = max_rate < 8
    # log_debug("3day: max-rate: %.2f%%, min-rate: %.2f%%, rule: %s", max_rate, min_rate, max_rate_rule)
    if max_rate_rule:
        pass
    else:
        log_info("sorry, max-rate too big")
        return 0

    k = 0
    day0_rule = ref_close(k) > ref_close(k+3) or rate0 > 0
    if day0_rule:
        pass
    else:
        log_info("sorry, day0 not positive")
        return 0

    rate_count = 0
    if rate0 > 0:
        rate_count += 1
    if rate1 > 0:
        rate_count += 1
    if rate2 > 0:
        rate_count += 1
    # log_debug("3day: rate  count: %d", rate_count)

    price_count = 0
    for i in range(3):
        if ref_close(i) > ref_close(3):
            price_count += 1
    # log_debug("3day: price count: %d", price_count)

    if rate_count >=2 or price_count >= 2:
        pass
    else:
        log_info("sorry: not match count-2 rule in the last 3day")
        return 0


    rate0_rule_opt = rate0 > 0 and ref_close(0) > ref_open(0)
    # log_debug("3day: last-day-upper: %s(opt)", rate0_rule_opt)
    if rate0_rule_opt:
        stars += '*'
        pass


    if True:
        saimail_set_subject_prefix(stars)
        log_info('bingo: %s -- %s', stock_id, this_date)
        wine_mail('pile', body)
        return 1

    return 0


saiobj.g_func_map['pile'] = pile_run


if __name__=="__main__":
    sailog_set("pile.log")

    db = db_init()
    saiobj.g_db = db

    sai_load_conf2('wine.cfg')

    # saiobj.g_to_send_mail = True

    one = True
    one = False

    if one:
        pass

        # 腾博股份
        trade_dt = '2019-08-05'
        stock_id = '300363'

        # 汇顶科技
        trade_dt = '2019-02-18'
        stock_id = '603160'

        # 深圳新星
        trade_dt = '2019-07-04'
        stock_id = '603978'

        # 中兴通信
        trade_dt = '2019-02-18'
        stock_id = '000063'


        sai_fmt_set_fetch_len(220)
        df = sai_fmt_simple(stock_id, trade_dt, db)
        pile_run()
    else:
        check_list = [
                # ma200
                ['300363', '2019-08-05', 1],  # 腾博股份
                ['603160', '2019-02-18', 1],  # 汇顶科技
                ['603978', '2019-07-04', 1],  # 深圳新星
                ['000063', '2019-02-18', 1],  # 中兴
                ['002317', '2019-08-08', 1],  # 众生药业
                ['000860', '2018-04-09', 1],  # 顺鑫农业
                ['002384', '2019-07-29', 1],  # 东山精密
                ['600871', '2019-02-28', 1],  # 石化油服
                ########################################################
                ########################################################

                # ma50
                ['300014', '2018-11-30', 1],  # 亿纬锂能
                ['603811', '2019-08-20', 1],  # 诚意药业
                ['603658', '2019-08-14', 1],  # 安图生物
                ['300520', '2017-09-01', 1],  # 科大国创
                ['300107', '2018-01-08', 1],  # 建新股份
                ['300709', '2019-08-14', 0],  # 精研科技 fail TODO

                # anti 反例
                ['000021', '2019-08-27', 0],  # 深科技 bad


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

            rv = pile_run()
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


# pile.py
