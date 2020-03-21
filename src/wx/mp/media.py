# -*- coding: utf-8 -*-
# filename: media.py

from basic import Basic
import json

import requests

from common import *


class Media(object):
    def __init__(self):
        log_debug('media() instanced')
        pass
    
    # upload media(image, voice...)
    def upload(self, accessToken, filePath, mediaType):

        openFile = open(filePath, "rb")
        param = {'media': openFile}
        postUrl = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=%s" % (accessToken, mediaType)

        r = requests.post(postUrl, files=param)
        log_debug('upload reply:\n%s', r.content)

        jsonDict = json.loads(r.content)
        mid = jsonDict['media_id']
        created = jsonDict['created_at']
        log_debug('mid: %s', mid)
        log_debug('crt: %s', created)

        return mid, created

    # upload image
    def uploadImage(self, filePath):

        accessToken = Basic.get_access_token()
        # log_debug('accessToken: %s', accessToken)

        mediaType = "image"

        return self.upload(accessToken, filePath, mediaType)


    # download
    def download(self, mid):
        accessToken = Basic.get_access_token()

        postUrl = "https://api.weixin.qq.com/cgi-bin/media/get?access_token=%s&media_id=%s" % (
            accessToken, mid)
        r = requests.get(postUrl)

        log_debug('download header: %s', r.headers)

        headers = r.headers
        if ('Content-Type: application/json\r\n' in headers) or ('Content-Type: text/plain\r\n' in headers):
            jsonDict = json.loads(r.read())
            log_debug('%s', jsonDict)
        else:
            buffer = r.content
            with open('test_media.jpg', 'wb') as f:
                f.write(buffer)
            log_debug("get successful")


if __name__ == '__main__':
    sailog_set("media.log")
    # sailog_set_info()

    filePath = "/home/sai3/project/tmp/000725.png"

    myMedia = Media()
    mid, crt = myMedia.uploadImage(filePath)

    myMedia.download(mid)

# media.py
