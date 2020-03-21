# -*- coding: utf-8 -*-
# filename: business.py

import time

from basic import Basic
from media import Media

import saiobj

from common  import *


class Business(object):
    db = db_init()
    life = 86400 * 3 - 10

    def __init__(self):
        self.__dict = dict()
        self.__dict['name'] = 'wang'

        log_debug("business instanced")

    def plot(self, stock_id, pub_date):

        sai_fmt_set_fetch_len(700)
        saiobj.g_plot_len = 500
        saiobj.g_photo_suffix = '.png'

        uid  = 'fei'
        ma_list = [20, 50, 200]

        path = sai_plot(pub_date, uid, stock_id, ma_list, Business.db)
        self.__dict['PATH'] = path

        log_info('path: %s', path)

        return path



    def processGet(self, cmdList):
        log_debug('this is function processGet')

        msg = 'wait 8 seconds, and try again'
        mid = ''

        for one in cmdList:
            log_info('iter: [%s]', one)

        stock_id = '000725'
        # pub_date => '2020-03-21'
        pub_date = get_date_by(0)


        if len(cmdList) == 2:
            stock_id = cmdList[1]
        if len(cmdList) == 3:
            stock_id = cmdList[1]
            pub_date = cmdList[2]

        if len(pub_date) == 8:
            pub_date = pub_date[0:4] + '-' + pub_date[4:6] + '-' + pub_date[6:8]

        log_info('stock_id: %s', stock_id)
        log_info('put_date: %s', pub_date)

        to_generate = False

        mid, crt = sai_query_mid(stock_id, pub_date, Business.db)
        if len(mid) > 0:
            # check time
            curr = int(time.time())
            diff = curr - crt
            log_info('curr(%d) - crt(%d) =  diff(%d)', curr, crt, diff)
            if diff > Business.life:
                log_info('warn: exceeds: (diff)%d > (life)%d, delete it', diff, Business.life)
                sai_delete_mid(stock_id, pub_date, Business.db)
                mid = ''
                to_generate = True
            else:
                log_info('bingo, mid still alive: %s', mid)
                to_generate = False
        else:
            to_generate = True
            log_info('not found [%s, %s] in db', stock_id, pub_date)

        if to_generate:
            path = self.plot(stock_id, pub_date)

            myMedia = Media()
            mid, crt = myMedia.uploadImage(path)

            log_debug('mid: %s', mid)
            log_debug('crt: %s', crt)
            sai_save_mid(stock_id, pub_date, mid, crt, Business.db)


        return msg, mid

    def processHelp(self, cmdList):
        log_debug('this is function processHelp')
        msg = ''
        mid = ''

        msg += 'name zhangsan\r\n'
        msg += 'reg 000002'

        return msg, mid

    def processReg(self, cmdList):
        log_debug('this is function processReg')
        msg = ''
        mid = ''

        msg = 'reg X'

        return msg, mid

    def processName(self, cmdList):
        log_debug('this is function processName')
        msg = ''
        mid = ''

        msg = 'name X'
        return msg, mid

    def process(self, cmd):
        msg = ''
        mid = ''

        log_info("(business)cmd: [%s]", cmd)

        cmdList = cmd.split(' ')
        if len(cmdList) >= 1:
            action = cmdList[0]
            log_info('action: [%s]', action)

            if action == 'get':
                msg, mid = self.processGet(cmdList)
            elif action == 'help':
                msg, mid = self.processHelp(cmdList)
            elif action == 'name':
                msg, mid = self.processName(cmdList)
            elif action == 'reg':
                msg, mid = self.processReg(cmdList)
            else:
                msg = '0'
                mid = ''
                log_info(msg)
        else:
            msg = '1'
            mid = ''
            log_info(msg)


        return msg, mid



if __name__ == '__main__':
    sailog_set("business.log")
    sailog_set_info()

    saiobj.g_to_send_mail = True

    b = Business()
    # b.process('get 000725')
    # b.process('get 000002')
    # b.process('get')
    # b.process('get 000725 2019-11-01')
    b.process('get 000725 20191201')

#
