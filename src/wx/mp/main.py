# -*- coding: utf-8 -*-
# filename: main.py

import web

from handle import Handle
from basic  import Basic

from common  import *

urls = (
    '/wx', 'Handle',
)


if __name__ == '__main__':
    sailog_set("web.log")
    sailog_set_info()

    # get token by thread
    b = Basic()
    b.setDaemon(True)
    b.start()

    log_info('web start')
    app = web.application(urls, globals())
    app.run()

