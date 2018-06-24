#!/usr/bin/env python
# coding=utf-8
# Stan 2017-08-02

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import time
import logging
import traceback


class Logging(object):
    buffer = []
    timer = {}

    def debug(self, *msg, **kargs):
        timer = kargs.get('timer')
        if timer:
            label, duration = timer
            current = int(time.time())
            if self.timer.has_key(label):
                last = self.timer[label]
                if current - last < duration:
                    return

            self.timer[label] = current

        for i in msg:
            logging.debug(i)

    def info(self, *msg, **kargs):
        for i in msg:
            logging.info(i)

    def warning(self, *msg, **kargs):
        once = kargs.get('once')
        if once:
            if once in self.buffer:
                return
            self.buffer.append(once)

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
