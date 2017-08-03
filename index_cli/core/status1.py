#!/usr/bin/env python
# coding=utf-8
# Stan 2015-06-05, 2017-08-02

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import time

from .backwardcompat import *
from .logging_class import Logging


class Status(Logging):
    def __init__(self):
        self.reset()


    def reset(self, text=''):
        self.ndirs = self.nfiles = 0
        self.last_dir = ''
        self.last_file = ''
        self.break_required = None
        self.message = text
        self._time = time.time()


    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, message):
        if isinstance(message, (list, tuple)):
            if not len(message):
                message = ''
            elif len(message) == 1:
                message = message[0]
            else:
                message = "{0} и др. значения".format(message[0])
        self._message = message


    @property
    def time(self):
        t = self._time
        self._time = time.time()
        return self._time - t


    @property
    def dir(self):
        return self.ndirs

    @dir.setter
    def dir(self, filename):
        self.last_dir = filename
        self.ndirs += 1


    @property
    def file(self):
        return self.nfiles

    @file.setter
    def file(self, filename):
        self.last_file = filename
        self.nfiles += 1


status1 = Status()
