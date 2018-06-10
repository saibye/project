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
        log_debug('++rate(%d): %.2f%%', i, rate)
        # log_debug('++amp (%d): %.2f', i, amp)
        log_debug('++zt  (%d): %.2f', i, zt)
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

    if saiobj.g_to_send_mail:
        log_debug('mail: %s\n%s', title, content)
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
        log_debug('++rate(%d): %.2f%%', i, rate)
        # log_debug('++amp (%d): %.2f', i, amp)
        log_debug('++zt  (%d): %.2f', i, zt)
        log_debug('++st  (%d): %.2f%%', i, stage)
        log_debug('++gp  (%d): %.2f%%', i, gap)
        if zt < ZT and rate < RATE and next_low < ref_low(i) and stage < STAGE:
            log_info('++%s -- ref(%d) matched: zt:%.2f%%, rate:%.2f%%, stage: %.2f%%, gap: %.2f%%', ref_date(i), i, zt, rate, stage, gap)
            return i

    return 0


# pub.py
