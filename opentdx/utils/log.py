# coding=utf-8

import logging
import os

DEBUG = os.getenv("TDX2_DEBUG", "")
# DEBUG = True

if DEBUG:
    LOGLEVEL = logging.DEBUG
else:
    LOGLEVEL = logging.INFO

log = logging.getLogger("PYTDX2")

log.setLevel(LOGLEVEL)
ch = logging.StreamHandler()
ch.setLevel(LOGLEVEL)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
log.addHandler(ch)