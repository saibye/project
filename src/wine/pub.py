#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj

from common import *


def wine_find_previous_green(_start, _width):

    ZT  = saiobj.g_wine_step_zt
    RATE= saiobj.g_wine_step_rate


    if _start - 1 < 0:
        log_error('invalid input: %d', _start)
        return 0

    low_price = ref_low(_start-1)

    for x in range(_width):
        i = x + _start

        if i + 2 >= ref_len():
            log_error('too short: %d < %d', i+2, ref_len())
            return 0

        rate = 100.00 * (ref_close(i) - ref_close(i+1)) / ref_close(i+1)
        amp  = 100.00 * (ref_high(i)  - ref_low(i)) / ref_close(i+1)
        zt   = 100.00 * (ref_close(i) - ref_open(i)) / ref_close(i+1)
        # log_debug('++date(%d): %s', i, ref_date(i))
        # log_debug('++rate(%d): %.2f%%', i, rate)
        # log_debug('++amp (%d): %.2f', i, amp)
        # log_debug('++zt  (%d): %.2f', i, zt)
        if zt < ZT and rate < RATE and low_price < ref_low(i):
            log_info('++%s -- ref(%d) matched: zt:%.2f%%, rate:%.2f%%', ref_date(i), i, zt, rate)
            return i

    return 0


def wine_find_previous_highest(_start, _width):
    highest_price = 0.0
    highest_day   = 0

    for x in range(_width):
        i = x + _start

        if i + 2 >= ref_len():
            log_error('too short: %d < %d', i+2, ref_len())
            return 0
        if ref_high(i) > highest_price:
            highest_price = ref_high(i)
            highest_day   = i

    return highest_day

def wine_find_total_up(_start, _width):

    ZT  = saiobj.g_wine_step_zt
    RATE= saiobj.g_wine_step_rate

    min_close = 9999
    for x in range(_width):
        i = x + _start
        if i + 1 >= ref_len():
            log_error('too short: %d < %d', i+1, ref_len())
            return min_close

        if ref_close(i) < min_close:
            min_close = ref_close(i)

    return min_close


def wine_mail(_case, _body):
    stock_id = ref_id(0)
    pub_date = ref_date(0)

    subject = sai_conf_get2(_case, 'subject')

    info  = ''
    info  = get_basic_info_all(stock_id, saiobj.g_db)

    if len(saiobj.g_subject_prefix) > 0:
        subject = '%s%s' % (saiobj.g_subject_prefix, subject)

    title = ''
    title = '%s: %s#%s' % (subject, stock_id, pub_date)

    content  = ''
    content += _body
    content += saiobj.g_mail_sep
    content += info

    log_info('mail: %s\n%s', title, content)

    if saiobj.g_to_send_mail:
        saimail_dev(title, content)

    return 0



def wine_find_previous_stage(_start, _width):

    ZT      = saiobj.g_wine_step_zt
    RATE    = saiobj.g_wine_step_rate
    STAGE   = saiobj.g_wine_stage
    GAP     = saiobj.g_wine_gap


    if _start - 1 < 0:
        log_error('invalid input: %d', _start)
        return 0

    next_low   = ref_low(_start-1)
    next_close = ref_close(_start-1)

    this_close = ref_close(_start)

    for x in range(_width):
        i = x + _start

        if i + 2 >= ref_len():
            log_error('too short: %d < %d', i+2, ref_len())
            return 0

        rate    = 100.00 * (ref_close(i) - ref_close(i+1)) / ref_close(i+1)
        amp     = 100.00 * (ref_high(i)  - ref_low(i)) / ref_close(i+1)
        zt      = 100.00 * (ref_close(i) - ref_open(i)) / ref_close(i+1)
        stage   = 100.00 * (this_close   - ref_close(i+1)) / ref_close(i+1)
        gap     = 100.00 * (next_close   - ref_close(i))   / ref_close(i)

        if gap > GAP:
            log_error('gap not meed: %.2f', gap)
            return 0

        # log_debug('++date(%d): %s', i, ref_date(i))
        # log_debug('++rate(%d): %.2f%%', i, rate)
        # log_debug('++amp (%d): %.2f', i, amp)
        # log_debug('++zt  (%d): %.2f', i, zt)
        # log_debug('++st  (%d): %.2f%%', i, stage)
        # log_debug('++gp  (%d): %.2f%%', i, gap)
        if zt < ZT and rate < RATE and next_low < ref_low(i) and stage < STAGE:
            log_info('++%s -- ref(%d) matched: zt:%.2f%%, rate:%.2f%%, stage: %.2f%%, gap: %.2f%%', ref_date(i), i, zt, rate, stage, gap)
            return i

    return 0


def wine_continuous_high(_start, _width, _which):

    days = 0

    this_price = 0.0
    last_price = 0.0

    for x in range(_width):
        i = x + _start

        if i + 1 >= ref_len():
            log_error('too short: %d < %d', i+1, ref_len())
            return 0

        rate = 100.00 * (ref_close(i) - ref_close(i+1)) / ref_close(i+1)
        amp  = 100.00 * (ref_high(i)  - ref_low(i)) / ref_close(i+1)
        zt   = 100.00 * (ref_close(i) - ref_open(i)) / ref_close(i+1)

        if _which == 'close':
            this_price = ref_close(i)
        elif _which == 'high':
            this_price = ref_high(i)
        elif _which == 'low':
            this_price = ref_low(i)
        elif _which == 'open':
            this_price = ref_open(i)
        else:
            return 0

        if this_price < last_price:
            days += 1
            # log_debug('%.2f < %.2f ==> days: %d', this_price, last_price, days)

        last_price = this_price

    return days


def wine_find_previous_highest_close(_start, _width):
    highest_price = 0.0
    highest_day   = 0

    for x in range(_width):
        i = x + _start

        if i + 2 >= ref_len():
            log_error('too short: %d < %d', i+2, ref_len())
            return 0

        if ref_close(i) > highest_price:
            highest_price = ref_close(i)
            highest_day   = i

    return highest_day


def wine_find_previous_lowest_close(_start, _width):
    lowest_price = 999999.0
    lowest_day   = 0

    for x in range(_width):
        i = x + _start

        if i + 2 >= ref_len():
            log_error('too short: %d < %d', i+2, ref_len())
            return 0

        if ref_close(i) < lowest_price:
            lowest_price = ref_close(i)
            lowest_day   = i

    return lowest_day


#
# X点往前突破天数(low)
#
#
def wine_break_days(_start, _width):
    days = 0

    sen_low = ref_low(_start)

    for x in range(_width):
        i = x + _start+1

        if i + 2 >= ref_len():
            log_error('too short: %d < %d', i+2, ref_len())
            return days

        if sen_low > ref_high(i):
            days += 1
        else:
            break

    return days


#
# X点往前突破天数(close)
#
#
def wine_close_break_days(_start, _width):
    days = 0

    sen_low = ref_close(_start)

    for x in range(_width):
        i = x + _start+1

        if i + 2 >= ref_len():
            log_error('too short: %d < %d', i+2, ref_len())
            return days

        if sen_low > ref_high(i):
            days += 1
        else:
            break

    return days



#
# start往前，存在点，满足向下跳空
#
#
def wine_island_exist(_start, _width):

    pair_day = -1
    highest = -1
    lowest  = 10000


    for x in range(_width):
        i = x + _start

        if i + 2 >= ref_len():
            log_error('too short: %d < %d', i+2, ref_len())
            return -1, -1

        # log_debug("date: %s, %.2f", ref_date(i), ref_close(i))

        # track extreme: high
        if ref_high(i) > highest:
            highest = ref_high(i)

        # track extreme: low
        if ref_low(i)  < lowest:
            lowest = ref_low(i)

        # find GAP
        if ref_high(i) < ref_low(i+1) and highest < ref_low(i+1):
            pair_day   = i+1
            # log_debug("pair_date: %s", ref_date(pair_day))
            # log_debug("region-high: %.2f", high)
            # log_debug("region-low:  %.2f", low)

            # TODO 检查区间内波动幅度不大

            # TODO 寻找那个收盘价最接近的点

            break


    return pair_day, highest


#
# 从X点开始往前最靠近ma200(close)
#
#
def wine_near_with_ma200(_start, _width):
    min_rate = 100.00
    min_idx  = -1


    for x in range(_width):
        i = x + _start

        if i + 2 >= ref_len():
            log_error('too short: %d < %d', i+2, ref_len())
            return 100.00, -1

        if ref_high(i) >= ref_ma200(i) and ref_low(i) <= ref_ma200(i):
            min_rate = 0.0
            min_idx  = i
            break

        rate = 100.00 * abs(ref_close(i) - ref_ma200(i)) / ref_ma200(i)
        if rate < min_rate:
            min_rate = rate
            min_idx  = i
            # log_debug("min: %d, %.2f", min_idx, min_rate)
        else:
            pass

    return min_rate, min_idx

#
# 从X点开始往前最靠近ma50(close)
#
#
def wine_near_with_ma50(_start, _width):
    min_rate = 100.00
    min_idx  = -1


    for x in range(_width):
        i = x + _start

        if i + 2 >= ref_len():
            log_error('error: too short: %d < %d', i+2, ref_len())
            return 100.00, -1

        if ref_high(i) >= ref_ma50(i) and ref_low(i) <= ref_ma50(i):
            min_rate = 0.0
            min_idx  = i
            break

        rate = 100.00 * abs(ref_close(i) - ref_ma50(i)) / ref_ma50(i)
        if rate < min_rate:
            min_rate = rate
            min_idx  = i
            # log_debug("min: %d, %.2f", min_idx, min_rate)
        else:
            pass

    return min_rate, min_idx


#
# X点往前突破天数(volume)
#
#
def wine_volume_break_days(_start, _width):
    days = 0

    sen_vol = ref_vol(_start)

    for x in range(_width):
        i = x + _start+1

        if i + 2 >= ref_len():
            log_error('too short: %d < %d', i+2, ref_len())
            return days

        if sen_vol > ref_vol(i):
            days += 1
        else:
            break

    return days


#
# X点往前突破天数(close)
#
#
def wine_close_break_days2(_start, _width):
    days = 0

    sen_price = ref_close(_start)

    for x in range(_width):
        i = x + _start+1

        if i + 2 >= ref_len():
            log_error('too short: %d < %d', i+2, ref_len())
            return days

        if sen_price > ref_close(i):
            days += 1
        else:
            break

    return days


#
# X点往前5/10最近(ma)
#
#
def wine_ma5_twist_ma10(_start, _width):
    min_rate = 100.00
    min_idx  = -1


    for x in range(_width):
        i = x + _start+1

        if i + 2 >= ref_len():
            log_error('too short: %d < %d', i+2, ref_len())
            return 100.00, -1

        rate = 100.00 * abs(ref_ma5(i) - ref_ma10(i)) / ref_ma10(i)
        if rate < min_rate:
            min_rate = rate
            min_idx  = i
            # log_debug("min: %d, %.2f", min_idx, min_rate)
        else:
            pass

    return min_rate, min_idx


#
# X点往前均线粘合最紧的(ma)
# ma5, 10, 20, 50, 200
#
def wine_ma_twist_5line(_start, _width):
    min_rate = 100.00
    min_idx  = -1


    for x in range(_width):
        i = x + _start+1

        if i + 2 >= ref_len():
            log_error('too short: %d < %d', i+2, ref_len())
            return 100.00, -1

        maxp = max(ref_ma5(i), ref_ma10(i), ref_ma20(i), ref_ma50(i), ref_ma200(i))
        minp = min(ref_ma5(i), ref_ma10(i), ref_ma20(i), ref_ma50(i), ref_ma200(i))
        rate = 100.00 * abs(maxp - minp) / ref_ma200(i)
        if rate < min_rate:
            min_rate = rate
            min_idx  = i
            # log_debug("min: %d, %.2f", min_idx, min_rate)
        else:
            pass

    return min_rate, min_idx


#
# X点往前均线粘合最紧的(ma)
# ma5, 10, 20, 50
#
def wine_ma_twist_4line(_start, _width):
    min_rate = 100.00
    min_idx  = -1


    for x in range(_width):
        i = x + _start+1

        if i + 2 >= ref_len():
            log_error('too short: %d < %d', i+2, ref_len())
            return 100.00, -1

        maxp = max(ref_ma5(i), ref_ma10(i), ref_ma20(i), ref_ma50(i))
        minp = min(ref_ma5(i), ref_ma10(i), ref_ma20(i), ref_ma50(i))
        rate = 100.00 * abs(maxp - minp) / ref_ma50(i)
        if rate < min_rate:
            min_rate = rate
            min_idx  = i
            # log_debug("min: %d, %.2f", min_idx, min_rate)
        else:
            pass

    return min_rate, min_idx


#
# 从X点开始往前找缺口
#
#
def wine_find_previous_gap(_start, _width):
    idx  = -1
    rate = 0.0


    for x in range(_width):
        i = x + _start+1

        if i + 2 >= ref_len():
            log_error('too short: %d < %d', i+2, ref_len())
            return 0.0, -1

        rule = ref_low(i) > ref_high(i+1)
        if rule:
            rate = 100.00 * (ref_close(i) - ref_close(i+1)) / ref_close(i+1)
            idx  = i
            # log_debug("gap: %d, %.2f, %s", idx, rate, ref_date(i))
            break
        else:
            pass

    return rate, idx


#
# 区间平均值和方差
#
#
def wine_region_calculation(_start, _width):
    idx  = -1
    rate = 0.0


    sum = 0.0

    # avg
    for x in range(_width):
        i = x + _start+1

        if i + 2 >= ref_len():
            log_error('error: too short: %d < %d', i+2, ref_len())
            return 1000.00, 1000.00

        # log_debug("%s", ref_date(i))
        sum = sum + ref_close(i)

    avg = sum / _width
    # log_debug("avg: %.2f", avg)


    # std
    sum = 0.0
    for x in range(_width):
        i = x + _start+1

        if i + 2 >= ref_len():
            log_error('error: too short: %d < %d', i+2, ref_len())
            return days

        sum = sum + (ref_close(i) - avg) * (ref_close(i) - avg)

    std = sum / _width
    # log_debug("std: %.2f", std)
    

    return avg, std


#
# 区间fish
#
#
def wine_find_fish(_start, _width):

    last = 1
    counter = 0

    lst = []

    # avg
    for x in range(_width):
        i = x + _start

        if i + 2 >= ref_len():
            log_error('error: too short: %d < %d', i+2, ref_len())
            return days

        diff = ref_ma5(i) - ref_ma10(i)

        if diff > 0.0:
            if last > 0:
                counter += 1
                # log_debug("%s, %.2f -- POSI-inc", ref_date(i), diff)
            else:
                last = 1
                # save NEGTIVE counter
                lst.append(counter)
                # log_debug("%s, %.2f -- POSI-rev: save %d", ref_date(i), diff, counter)
                counter = 1
        elif diff < 0.0:
            if last > 0:
                last = -1
                # save POSITIVE counter
                lst.append(counter)
                # log_debug("%s, %.2f -- NEG-rev: save %d", ref_date(i), diff, counter)
                counter = -1
            else:
                counter -= 1
                # log_debug("%s, %.2f -- NEG-inc", ref_date(i), diff)
        else:
            # log_debug("it's a zero")
            continue

    lst.append(counter)

    # log_debug("%s", lst)

    return lst


#
# 从X点开始往前最靠近ma20(all)
#
#
def wine_near_with_ma20(_start, _width):
    min_rate = 100.00
    min_idx  = -1


    for x in range(_width):
        i = x + _start+1

        if i + 2 >= ref_len():
            log_error('error, too short: %d < %d', i+2, ref_len())
            return 100.00, -1

        if ref_high(i) >= ref_ma20(i) and ref_low(i) <= ref_ma20(i):
            min_rate = 0.0
            min_idx  = i
            log_debug("touch ma20: %s", ref_date(i))
            break

        rate1= 100.00 * abs(ref_low(i) - ref_ma20(i)) / ref_ma20(i)
        rate2= 100.00 * abs(ref_high(i) - ref_ma20(i)) / ref_ma20(i)
        rate = min(abs(rate1), abs(rate2))

        if rate < min_rate:
            min_rate = rate
            min_idx  = i
            # log_debug("near ma20: %s, %d, %.2f ", ref_ma20(i), min_idx, min_rate)
        else:
            pass

    return min_rate, min_idx



#
# X点往前排名(volume)
#
#
def wine_volume_rank(_start, _width):
    rank = 0

    sen_vol = ref_vol(_start)

    for x in range(_width):
        i = x + _start+1

        if i + 2 >= ref_len():
            log_error('too short: %d < %d', i+2, ref_len())
            return rank

        if ref_vol(i) > sen_vol:
            rank += 1

    return rank

#
# X点往前ma50 > ma200天数
#
def wine_ma50_above_ma200_days(_start, _width):
    days = 0

    for x in range(_width):
        i = x + _start+1

        if i + 2 >= ref_len():
            log_error('too short: %d < %d', i+2, ref_len())
            return days

        if ref_ma50(i) >= ref_ma200(i):
            days += 1
        else:
            break

    return days

#
# X点往前 near(ma50, ma200): rate > x天数
#
def wine_ma50_near_ma200_days(_start, _width, _x):
    days = 0

    for x in range(_width):
        i = x + _start+1

        if i + 2 >= ref_len():
            log_error('error: too short: %d < %d', i+2, ref_len())
            return days

        a = ref_ma50(i)
        b = ref_ma200(i)
        rate = 100.00 * min(a, b) / max(a, b)
        # log_debug('near: %s - %.2f', ref_date(i), rate)
        if rate >= _x:
            days += 1
        # else:
        #     break

    return days


#
# X点往前(ma50 > close > ma200) 天数
#
def wine_ma50_close_ma200_days(_start, _width):
    days = 0

    for x in range(_width):
        i = x + _start+1

        if i + 2 >= ref_len():
            log_error('error: too short: %d < %d', i+2, ref_len())
            return days

        a = ref_ma50(i)
        b = ref_ma200(i)
        rule = ref_close(i) >= min(a, b) and ref_close(i) <= max(a, b)
        if rule:
            days += 1

    return days

#
# ma200 ascending
#
def wine_ma200_ascending_days(_start, _width):
    days = 0

    for x in range(_width):
        i = x + _start+1
        j = i+20

        if j + 2 >= ref_len():
            log_error('error: too short: %d < %d', j+2, ref_len())
            return days

        if ref_ma200(i) >= ref_ma200(j):
            days += 1

    return days


# pub.py
