#!/usr/bin/env python
# -*- encoding: utf8 -*-

import matplotlib.pyplot as plt

from sailog  import *
from saidb   import *
from saisql  import *
from saifmt  import *

import saiobj



def sai_plot(_date, _uid, _stock_id, _ma_list, _db):
    log_info('trace_plot: begin')

    table = ''

    # => /home/sai/project/tmp/000725.svg
    # photo_path = '%s/%s.svg' % (saiobj.g_photo_dir, _stock_id)
    photo_path = '%s/%s%s' % (saiobj.g_photo_dir, _stock_id, saiobj.g_photo_suffix)

    till_date = _date

    df = sai_fmt_simple(_stock_id, till_date, _db)
    if df is None or df.empty or len(df) < 10:
        log_info('error: sai_fmt_simple invalid:\n%s', df)
        return ''

    # log_debug("simple: \n%s", df)

    # real till date
    till_date = df['pub_date'][0]
    log_info('real till date: [%s] -> [%s]', _date, till_date)


    # html-table
    html_table = """\
<table width="500" border="1" bordercolor="red" cellspacing="1">
<tr>
  <td><strong>日期</strong></td>
  <td><strong>收盘价</strong></td>
  <td><strong>涨幅</strong></td>
</tr>"""
    # <td><strong>开盘价</strong></td>

    for idx, row in df.iterrows():
        if idx >= 3:
            break

        curr = df['close_price'][idx]
        # open = df['open_price'][idx]
        last = df['close_price'][idx+1]
        rate = (curr - last) / last * 100.0
        # log_debug("rate: [%s]", rate)

        one = "\n<tr>\
<td> %s </td>\
<td> %.2f </td>\
<td> %.2f%% </td>\
</tr>" % (row['pub_date'], curr, rate)

        html_table += one


    html_table += "</table>"

    # log_debug("table:\n%s", html_table)


    ###################################################################
    ###################################################################
    ###################################################################
    # sort in-asc-order
    df = df.set_index('pub_date').sort_index(ascending=True)
    # log_info("new: \n%s", df)

    # MA
    df['MA20'] 	= df['close_price'].rolling(20).mean()
    df['MA50']	= df['close_price'].rolling(50).mean()
    df['MA200'] = df['close_price'].rolling(200).mean()



    """
    log_info("ma-list1: %s", _ma_list)
    for ma in _ma_list:
        ma_name = 'MA%d' % (ma)
        df[ma_name] = df['close_price'].rolling(ma).mean()
    """


    #---------------------------------------------------------#
    #---------------------------------------------------------#
    #---------------------------------------------------------#
    # plot
    df = df.tail(saiobj.g_plot_len)

    length = len(df)
    # log_debug("after plot, df-len: %d", length)

    # start date
    start_date = df.index[0]
    # log_debug('start date: [%s]', start_date)


    ########################################################################
    #                                                                      #
    #                                                                      #
    #                                                                      #
    ########################################################################

    stock_name = get_basic_name(_stock_id, _db)

    plot_title = '%s, %s' % (till_date, _stock_id)


    # This can clear context
    fig = plt.figure()

    # AX1
    left, bottom, width, height = 0.05, 0.05, 0.9, 0.9
    ax1 = fig.add_axes([left, bottom, width, height])
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)

    # 1.1 CLOSE
    # df['close_price'].plot(label='close price', title=_stock_id, ls='-', lw=0.8, color = 'black', figsize=(10,5))
    df['close_price'].plot(color='black', title=plot_title, ls='-', lw=1.2,  figsize=(10, 5))


    # 1.3. MA
    """
    lw = 0.4
    for ma in _ma_list:
        ma_name = 'MA%d' % (ma)
        df[ma_name].plot(label=ma_name, lw=lw)
        lw += 0.2
        log_info('plot: %s', ma_name)
    """
    df['MA20'].plot(color='red', lw=0.4)
    df['MA50'].plot(color='blue', lw=0.6)
    df['MA200'].plot(color='m', lw=0.8)


    # 1.2. LINE
    # close-price series
    cs = df['close_price']
    cp_max = cs.max()
    cp_min = cs.min()
    cp_mid = (cp_max + cp_min) / 2.0
    
    cp_cur = cs[len(cs)-1]
    rate   = (cp_max - cp_cur) / (cp_max - cp_min) * 100.00


    fontsize = 8
    style = 'italic'
    xsc   = 2
    text_color = 'green'
    line_color = 'green'
    lw = 0.2

    txt = '%.2f' % (cp_max)
    plt.axhline(y=cp_max, color=line_color, ls='-.', lw=lw)
    ax1.text(xsc, cp_max, txt, color=text_color, fontsize=fontsize, style=style)

    txt = '%.2f' % (cp_min)
    plt.axhline(y=cp_min, color=line_color, ls='-.', lw=lw)
    ax1.text(xsc, cp_min, txt, color=text_color, fontsize=fontsize, style=style)

    txt = '%.2f' % (cp_mid)
    plt.axhline(y=cp_mid, color=line_color, ls='-.', lw=lw)
    ax1.text(xsc, cp_mid, txt, color=text_color, fontsize=fontsize, style=style)

    xsc   = 2
    lw    = 0.4
    txt = '%.2f, %.2f%%' % (cp_cur, rate)
    plt.axhline(y=cp_cur, color='black', lw=lw)
    ax1.text(xsc, cp_cur+0.1, txt, color=text_color, fontsize=fontsize, style=style)


    ########################################################################
    #                                                                      #
    #                                                                      #
    #                                                                      #
    ########################################################################


    # AX2
    left, bottom, width, height = 0.15, 0.55, 0.3, 0.3
    ax2 = fig.add_axes([left, bottom, width, height])

    ax2.get_xaxis().set_visible(False)
    ax2.tick_params(axis='both', which='major', labelsize=6)
    #ax2.xaxis.set_ticklabels([])
    ax2.spines['right'].set_linewidth(0.2)
    ax2.spines['top'].set_linewidth(0.2)
    ax2.spines['left'].set_linewidth(0.2)
    ax2.spines['bottom'].set_linewidth(0.2)
    ax2.spines['right'].set_linestyle('-')
    ax2.spines['top'].set_linestyle('-')
    ax2.spines['left'].set_linestyle('-')
    ax2.spines['bottom'].set_linestyle('-')

    df2 = df.tail(50)

    df2['close_price'].plot(color='black', lw=0.8)
    df2['MA20'].plot(color='red', lw=0.4)
    df2['MA50'].plot(color='blue', lw=0.4)
    df2['MA200'].plot(color='m', lw=0.4)

    plt.savefig(photo_path, dpi=300)

    # plt.show()

    # email
    subject = 'T: %s#%s' % (stock_name, till_date)
    body = '%s<br>[%s, %s](%d)<br>%s' % (_stock_id, start_date, till_date, length, html_table)
    # log_info('body:\n%s', body)

    if saiobj.g_to_send_mail:
        log_info("(P) -- mail")
        saimail_photo(subject, body, photo_path)
        #_thread.start_new_thread(saimail_photo, (subject, body, photo_path) )

    log_info('trace_plot: end')

    return photo_path



if __name__=="__main__":
    sailog_set("saiplot.log")

    log_info("plot begin")

    sai_fmt_set_fetch_len(700)
    saiobj.g_plot_len = 500
    saiobj.g_photo_suffix = '.svg'

    db = db_init()

    date = '2020-03-16'
    uid  = 'fei'
    stock_id = '000100'
    stock_id = '000002'
    ma_list = [20, 50, 200]

    pp = sai_plot(date, uid, stock_id, ma_list, db)
    log_info('path: %s', pp)

    db_end(db)
    log_info("plot bye!")


# saiplot.py
