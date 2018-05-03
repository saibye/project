#!/usr/bin/env python
# -*- encoding: utf8 -*-


import saiobj
from common import *


def wine_find_previous_green(_start, _width):

    ZT  = saiobj.g_wine_step_zt
    RATE= saiobj.g_wine_step_rate

    for x in range(_width):
        i = x + _start

        if i + 2 >= ref_len():
            log_error('too short: %d < %d', i+2, ref_len())
            return 0

        rate = 100.00 * (ref_close(i) - ref_close(i+1)) / ref_close(i+1)
        amp  = 100.00 * (ref_high(i)  - ref_low(i)) / ref_close(i+1)
        zt   = 100.00 * (ref_close(i) - ref_open(i)) / ref_close(i+1)
        log_debug('++date(%d): %s', i, ref_date(i))
        log_debug('++rate(%d): %.2f', i, rate)
        log_debug('++amp (%d): %.2f', i, amp)
        log_debug('++zt  (%d): %.2f', i, zt)
        if zt < ZT:
            log_info('++%s -- ref(%d) matched: zt:%.2f%%', ref_date(i), i, zt)
            return i

    return 0


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



# pub.py
