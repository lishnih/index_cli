#!/usr/bin/env python
# coding=utf-8
# Stan 2017-03-09

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import traceback

from .status_class import Status


class Recorder(Status):
    def __init__(self, session=None, func=None, error_class=None):
        Status.__init__(self)
        self._session = session
        self._func = func
        self._error_class = error_class
        self._cash = {}

    # === session ===

    @property
    def session(self):
        if not self._session:
            raise Exception("No session associated!")

        return self._session

    @session.setter
    def session(self, session):
        self._session = session

    @property
    def bind(self):
        return self.session.bind

    def query(self, *args, **kargs):
        return self.session.query(*args, **kargs)

    def add(self, OBJ):
        self.session.add(OBJ)
        self._cash[OBJ.__table__.name] = OBJ

    def execute(self, *args, **kargs):
        return self.session.execute(*args, **kargs)

    def commit(self):
        self.session.commit()

    # === func ===

    @session.setter
    def func(self, func):
        self._func = func

    def func(self, *args, **kargs):
        if self._func:
            self._func(*args, **kargs)

    # === error_class ===

    @property
    def error_class(self):
        if not self._error_class:
            raise Exception("No error_class associated!")

        return self._error_class

    @error_class.setter
    def error_class(self, error_class):
        self._error_class = error_class

    # === Utilities ===

    def get_current(self, tablename, default=None):
        return self._cash.get(tablename, default)

    def get_slice(self):
        return self.get_current('slices')

    # === Debug ===

    def debug(self, *msg, **kargs):
        Status.debug(self, *msg, **kargs)

    def info(self, *msg, **kargs):
        if self._error_class:
            SLICE = self.get_slice()
            slice_id = SLICE.id if SLICE else None
            parse_id = kargs.pop('parse_id', None)
            target = kargs.pop('target', None)
            for i in msg:
                ERR = self._error_class(i, 'INFO', slice_id=slice_id, parse_id=parse_id, target=target)
                self.session.add(ERR)
            self.session.commit()

        Status.info(self, *msg, **kargs)

    def warning(self, *msg, **kargs):
        once = kargs.pop('once')
        if once:
            if once in self.buffer:
                return
            self.buffer.append(once)

        if self._error_class:
            SLICE = self.get_slice()
            slice_id = SLICE.id if SLICE else None
            parse_id = kargs.pop('parse_id', None)
            target = kargs.pop('target', None)
            for i in msg:
                ERR = self._error_class(i, 'WARNING', slice_id=slice_id, parse_id=parse_id, target=target)
                self.session.add(ERR)
            self.session.commit()

        Status.debug(self, *msg, **kargs)

    def error(self, msg, *args, **kargs):
        if self._error_class:
            SLICE = self.get_slice()
            slice_id = SLICE.id if SLICE else None
            parse_id = kargs.pop('parse_id', None)
            target = kargs.pop('target', None)
            ERR = self._error_class(msg, 'ERROR', slice_id=slice_id, parse_id=parse_id, target=target)
            self.session.add(ERR)
            self.session.commit()

        Status.error(self, msg, *args, **kargs)

    def exception(self, msg, *args, **kargs):
        if self._error_class:
            SLICE = self.get_slice()
            slice_id = SLICE.id if SLICE else None
            parse_id = kargs.pop('parse_id', None)
            target = kargs.pop('target', None)
            ERR = self._error_class(msg, 'EXCEPTION', slice_id=slice_id, parse_id=parse_id, target=target, traceback=traceback.format_exc())
            self.session.add(ERR)
            self.session.commit()

        Status.exception(self, msg, *args, **kargs)
