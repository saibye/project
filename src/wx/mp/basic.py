# -*- coding: utf-8 -*-
# filename: Basic.py

import urllib
import time
import json

from threading import Thread

from common  import *

class Basic(Thread):

    __accessToken   = ''
    __leftTime      = 0

    __appId     = sai_conf_get_wx_appid()
    __appSecret = sai_conf_get_wx_appsecret()

    uniq_dict = dict()


    @classmethod
    def __real_get_access_token(cls):
        postUrl = ("https://api.weixin.qq.com/cgi-bin/token?grant_type="
                   "client_credential&appid=%s&secret=%s" % (cls.__appId, cls.__appSecret))

        log_debug('real get: %s', postUrl)

        urlResp = urllib.request.urlopen(postUrl)
        urlResp = json.loads(urlResp.read())

        # log_info('real get: %s', urlResp)

        cls.__accessToken = urlResp['access_token']
        cls.__leftTime    = urlResp['expires_in']

        log_debug('real got: %s', cls.__accessToken)


    @classmethod
    def get_access_token(cls):
        if cls.__leftTime < 10:
            # log_debug('token-leftTime: %d', cls.__leftTime)
            cls.__real_get_access_token()
        else:
            # log_debug('directly return')
            pass

        return cls.__accessToken


    @classmethod
    def run(cls):
        log_info('token thread started')
        while(True):
            if cls.__leftTime > 10:
                time.sleep(2)
                cls.__leftTime -= 2
                # log_debug('leftTime -= 2: %d\n%s', cls.__leftTime, cls.__accessToken)
            else:
                cls.__real_get_access_token()
                # log_debug('real get access token: %s', cls.__accessToken)

    @classmethod
    def is_processing(cls, _key):
        rv = _key in cls.uniq_dict
        return rv

    @classmethod
    def set_processing(cls, _key):
        cls.uniq_dict[_key] = '0'


if __name__ == '__main__':
    sailog_set("basic.log")

    '''
    b = Basic()
    b.setDaemon(True)
    b.start()
    time.sleep(5)
    '''


    id = Basic.get_access_token()
    log_info('token1: %s', id)
    id = Basic.get_access_token()
    log_info('token2: %s', id)

# basic.py
