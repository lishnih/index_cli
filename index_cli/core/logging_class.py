#!/usr/bin/env python
# coding=utf-8
# Stan 2017-08-02

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import logging, traceback

from .backwardcompat import *


class Logging(object):


    def debug(self, *msg):
        for i in msg:
            logging.debug(i)


    def info(self, *msg):
        for i in msg:
            logging.info(i)


    def warning(self, *msg):
        for i in msg:
            logging.warning(i)


    def error(self, msg, *args, **kargs):
        logging.error(msg)
        logging.error("args: {0!r}".format(args))
        logging.error("kargs: {0!r}".format(kargs))


    def exception(self, msg, *args, **kargs):
        logging.error(msg)
        logging.error("args: {0!r}".format(args))
        logging.error("kargs: {0!r}".format(kargs))
        logging.error(traceback.format_exc())