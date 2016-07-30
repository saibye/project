#!/usr/bin/python
# -*- encoding: utf8 -*-


import logging
import logging.handlers
import os


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

sai_dft_log = "sai.log"
sai_dft_fmt = "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s"
sai_dft_fmt = "%(asctime)s - %(filename)s:%(lineno)s - %(message)s"
sai_dft_tm  = "%Y-%m-%d %H:%M:%S"
sai_dft_path= os.environ['LOG'] + '/'

rh=logging.handlers.TimedRotatingFileHandler(sai_dft_path+sai_dft_log, 'H')

#fm=logging.Formatter("%(asctime)s  %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
fm=logging.Formatter(sai_dft_fmt, sai_dft_tm)
rh.setFormatter(fm)

logger.addHandler(rh)

log_debug=logger.debug
log_info=logger.info
log_warn=logger.warn
log_error=logger.error
log_critical=logger.critical



def sailog_set(_log_name):

    global logger
    global rh

    global log_debug
    global log_info
    global log_warn
    global log_error
    global log_critical

    # clear previous handler
    logger.removeHandler(rh)

    # full path
    log_path = sai_dft_path + _log_name

    # create new log handler
    rh=logging.handlers.TimedRotatingFileHandler(log_path, 'D')

    # set format
    fm=logging.Formatter(sai_dft_fmt, sai_dft_tm)
    rh.setFormatter(fm)

    logger.addHandler(rh)

    log_debug   = logger.debug
    log_info    = logger.info
    log_warn    = logger.warn
    log_error   = logger.error
    log_critical= logger.critical
    log_info("\n/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/")

    return 



if __name__ == "__main__":
    log_info("hello, log")

    sailog_set("2.log")
    log_warn("warn you %s", "costaxu")
    log_critical("it is critical")

    v = "bbb"
    log_info("ccc: %s", v)
    #df = ts.get_realtime_quotes("000002")
    #log_info("ddd:\n %s", df)  # good
    i = 124
    log_info("ppp:\t %s", i)
    log_info("qqq:\n %d", i)

# sailog.py
