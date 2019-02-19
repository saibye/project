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

    title = ''
    title = '%s: %s#%s' % (subject, stock_id, pub_date)

    content  = ''
    content += _body
    content += saiobj.g_mail_sep
    content += info

    log_debug('mail: %s\n%s', title, content)

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
# X点往前突破天数
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

# pub.py
