#!/usr/bin/env python
# coding=utf-8
# Stan 2017-03-09

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import traceback

from sqlalchemy.engine.reflection import Inspector

from .status_class import Status


class Recorder(Status):
    _cash = {}
    _unique_constraints = {}

    def __init__(self, session=None, logging_class=None):
        Status.__init__(self)
        self._session = session
        self._logging_class = logging_class

    # === Session ===

    @property
    def session(self):
        if not self._session:
            raise Exception("No session associated!")

        return self._session

    @session.setter
    def session(self, session):
        self._session = session
        self._insp = Inspector.from_engine(self._session.bind)

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

    def merge(self, *args, **kargs):
        return self.session.merge(*args, **kargs)

    def flush(self):
        self.session.flush()

    def commit(self):
        self.session.commit()

    def get_unique_constraints(self, table):
        if table in self._unique_constraints:
            return self._unique_constraints[table]

        res = self._insp.get_unique_constraints(table)
        column_names = res[0].get('column_names') if res else []
        return self._unique_constraints.setdefault(table, column_names)

    def get_or_create(self, model, func=None, defaults=None, **kwargs):
        params = {k: v for k, v in kwargs.items() if v is not None}
#         column_names = self.get_unique_constraints(model.__table__.name)
#         if column_names:
#             params = {k: v for k, v in params.items() if k in column_names}

        instance = self.query(model).filter_by(**params).first()
        if instance:
            if func:
                func(instance)

        else:
            if defaults:
                kwargs.update(defaults)

            instance = model(**kwargs)
            self.add(instance)

        return instance

    # === Utilities ===

    def get_current(self, tablename, default=None):
        return self._cash.get(tablename, default)

    # === Error Class ===

    @property
    def logging_class(self):
        if not self._logging_class:
            raise Exception("No logging_class associated!")

        return self._logging_class

    @logging_class.setter
    def logging_class(self, logging_class):
        self._logging_class = logging_class

    # === Debug ===

    def debug(self, *msg, **kargs):
        Status.debug(self, *msg, **kargs)

    def info(self, *msg, **kargs):
        Status.info(self, *msg, **kargs)

        if self._logging_class:
            PARSER = self.parser if hasattr(self, 'parser') else None
            parse_id = kargs.pop('parse_id', None)
            for i in msg:
                ERR = self._logging_class(name=i, level='INFO',
                    parser=PARSER, _parse_id=parse_id, **kargs)
                self.session.add(ERR)
            self.session.commit()

    def warning(self, *msg, **kargs):
        Status.warning(self, *msg, **kargs)

        if self._logging_class:
            PARSER = self.parser if hasattr(self, 'parser') else None
            parse_id = kargs.pop('parse_id', None)
            for i in msg:
                ERR = self._logging_class(name=i, level='WARNING',
                    parser=PARSER, _parse_id=parse_id, **kargs)
                self.session.add(ERR)
            self.session.commit()

    def error(self, msg, *args, **kargs):
        Status.error(self, msg, *args, **kargs)

        if self._logging_class:
            PARSER = self.parser if hasattr(self, 'parser') else None
            parse_id = kargs.pop('parse_id', None)
            ERR = self._logging_class(name=msg, level='ERROR',
                parser=PARSER, _parse_id=parse_id, args=repr(args), kargs=repr(kargs))
            self.session.add(ERR)
            self.session.commit()

    def exception(self, msg, *args, **kargs):
        Status.exception(self, msg, *args, **kargs)

        if self._logging_class:
            PARSER = self.parser if hasattr(self, 'parser') else None
            parse_id = kargs.pop('parse_id', None)
            ERR = self._logging_class(name=msg, level='EXCEPTION',
                parser=PARSER, _parse_id=parse_id, args=repr(args), kargs=repr(kargs),
                traceback=traceback.format_exc())
            self.session.add(ERR)
            self.session.commit()
