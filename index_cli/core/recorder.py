#!/usr/bin/env python
# coding=utf-8
# Stan 2017-03-09

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from .status_class import Status


class Recorder(Status):
    def __init__(self, status=None, session=None):
        self._status = status
        self._session = session

    @property
    def session(self):
        if not self._session:
            raise Exception("No session associated!")

        return self._session

    @property
    def bind(self):
        return self.session.bind

    def query(self, *args, **kargs):
        if self._session:
            self._session.query(*args, **kargs)

    def add(self):
        if self._session:
            self._session.query(*args, **kargs)

    def execute(self):
        if self._session:
            self._session.query(*args, **kargs)

    def commit(self):
        if self._session:
            self._session.query(*args, **kargs)
