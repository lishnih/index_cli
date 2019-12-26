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
    debug_level = 1

    def set_debug_level(self, debug_level=1):
        if isinstance(debug_level, int):
            self.debug_level = debug_level

        elif debug_level.isnumeric():
            self.debug_level = int(debug_level)

    def get_debug_level(self):
        return self.debug_level

    def debug(self, *msg, **kargs):
        debug_level = kargs.get('_level', 1)
        if debug_level > self.debug_level:
            return

        timer = kargs.get('timer')
        if timer:
            label, duration = timer
            current = int(time.time())
            if current - self.timer.get(label, 0) < duration:
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
            logging.info("This warning is displayed once")

        for i in msg:
            logging.warning(i)

    def error(self, msg, *args, **kargs):
        once = kargs.pop('once')
        if once:
            if once in self.buffer:
                return

            self.buffer.append(once)
            logging.info("This error is displayed once")

        logging.error(msg)
        logging.error("args: {0!r}".format(args))
        logging.error("kargs: {0!r}".format(kargs))

    def exception(self, msg, *args, **kargs):
        once = kargs.pop('once', '')
        if once:
            if once in self.buffer:
                return

            self.buffer.append(once)
            logging.info("This exception is displayed once")

        logging.error(msg)
        logging.error("args: {0!r}".format(args))
        logging.error("kargs: {0!r}".format(kargs))
        logging.error(traceback.format_exc())
