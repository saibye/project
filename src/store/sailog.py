#!/usr/bin/python
# -*- encoding: utf8 -*-


import logging
import logging.handlers

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

sai_dft_log = "sai.log"
sai_dft_fmt = "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s"
sai_dft_fmt = "%(asctime)s - %(filename)s:%(lineno)s - %(message)s"
sai_dft_tm  = "%Y-%m-%d %H:%M:%S"

rh=logging.handlers.TimedRotatingFileHandler(sai_dft_log, 'D')

#fm=logging.Formatter("%(asctime)s  %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
fm=logging.Formatter(sai_dft_fmt, sai_dft_tm)
rh.setFormatter(fm)

logger.addHandler(rh)

debug=logger.debug
info=logger.info
warn=logger.warn
error=logger.error
critical=logger.critical



def sailog_set(_log_name):

    global logger
    global rh

    global debug
    global info
    global warn
    global error
    global critical

    # clear previous handler
    logger.removeHandler(rh)

    # create new log handler
    rh=logging.handlers.TimedRotatingFileHandler(_log_name, 'D')

    # set format
    fm=logging.Formatter(sai_dft_fmt, sai_dft_tm)
    rh.setFormatter(fm)

    logger.addHandler(rh)

    debug   = logger.debug
    info    = logger.info
    warn    = logger.warn
    error   = logger.error
    critical= logger.critical

    return 



if __name__ == "__main__":
    info("hello, log")
    sailog_set("2.log")
    warn("warn you %s", "costaxu")
    critical("it is critical")

# sailog.py
