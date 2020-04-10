# -*- coding: utf-8 -*-
# filename: handle.py

import hashlib
import web

import reply
import receive
import business
from basic import Basic

from common  import *

class Handle(object):
    def GET(self):
        try:
            data = web.input()

            print("(GET)webdata is\n%s", data)

            if len(data) == 0:
                return "hello, this is handle view"

            signature = data.signature
            timestamp = data.timestamp
            nonce = data.nonce
            echostr = data.echostr
            token = "495"

            print("timestamp: ", timestamp)
            print("nonce:     ", nonce)
            print("echostr:   ", echostr)
            # print("data:      ", data)


            list = [token, timestamp, nonce]
            list.sort()
            # print('list:', list)

            sha1 = hashlib.sha1()
            sha1.update("".join(list).encode('utf-8'))
            # sha1.update("".join(list))
            hashcode = sha1.hexdigest()
            # print("handle/GET func: hashcode, signature: ", hashcode, signature)

            if hashcode == signature:
                return echostr
            else:
                return ""
        except Exception as Argument:
            return Argument

    def POST(self):
        try:
            webData = web.data()
            log_debug("(POST)webdata is\n%s", webData)

            recMsg = receive.parse_xml(webData)

            if isinstance(recMsg, receive.Msg):
                toUser = recMsg.FromUserName
                fromUser = recMsg.ToUserName
                messageId= recMsg.MsgId
                log_info('message-id: [%s]', messageId)

                # check processed
                key = '%s+%s+%s' % (toUser, fromUser, messageId)
                if Basic.is_processing(key):
                    log_info('again')
                    # return 'success'
                    return reply.TextMsg(toUser,  fromUser, 'wait 5 seconds, and try again').send()
                else:
                    log_info('[%s]: first request', messageId)
                    Basic.set_processing(key)

                if recMsg.MsgType == 'text':
                    log_debug('(handle)text')
                    b = business.Business()

                    # process command
                    # return: message, image-id
                    msg, mid = b.process(recMsg.Content)

                    log_debug('msg: %s', msg)
                    log_info('mid: %s', mid)


                    replyMsg = None

                    if len(mid) == 0:
                        replyMsg = reply.TextMsg(toUser,  fromUser, msg)
                    else:
                        replyMsg = reply.ImageMsg(toUser, fromUser, mid)

                    return replyMsg.send()

                elif recMsg.MsgType == 'image':
                    log_info('(handle)image')
                    mediaId = recMsg.MediaId
                    replyMsg = reply.ImageMsg(toUser, fromUser, mediaId)
                    return replyMsg.send()
                else:
                    return reply.Msg().send()
            else:
                log_error("fatal: error: can't arrive here")
                return reply.Msg().send()
        except Exception as Argment:
            return Argment
