#!/usr/bin/env python
# coding=utf-8
# Stan 2012-04-08, 2017-03-09

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os, shutil, logging, traceback

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker, attributes

from .core.backwardcompat import *


class Recorder(object):


    def __init__(self, options={}, metadata=None, base=None, session=None):
        self.metadata = metadata
        self.base = base
        self.session = session

        dburi = getDbUri(options)
        if dburi:
            engine = create_engine(dburi)
            if engine.name == "sqlite":
                filename = engine.url.database
                if filename:
                    dirname = os.path.dirname(filename)
                    if not os.path.exists(dirname):
                        os.makedirs(dirname)

        if not session:
            self.session = scoped_session(sessionmaker())
            self.session.configure(bind=engine)

        self.model_cache = {}


    @property
    def metadata(self):
        if not self._metadata:
            raise Exception("No metadata associated!")

        return self._metadata


    @metadata.setter
    def metadata(self, metadata):
        self._base = None
        self._metadata = metadata


    @property
    def base(self):
        if not self._base:
            raise Exception("No base associated!")

        return self._base


    @base.setter
    def base(self, base):
        if base:
            self._base = base
            self._metadata = base.metadata


    def drop_all(self):
        self.metadata.drop_all(self.session.bind)


    def create_all(self):
        self.metadata.create_all(self.session.bind)


    def commit(self):
        self.session.commit()


    def get_table(self, tablename):
        return self.metadata.tables.get(tablename)


    def get_model(self, tablename):
        if tablename in self.model_cache:
            return self.model_cache[tablename]

        for c in self.base._decl_class_registry.values():
            if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
                return self.model_cache.setdefault(tablename, c)


    def required(self, object_dict, required):
        for i in required:
            if i not in object_dict or object_dict[i] is None:
                return False

        return True


    def insert(self, tablename, records):
        t = self.get_table(tablename)
        if t is None:
            raise Exception("No such table: '{0}'".format(tablename))

        self.session.bind.execute(t.insert(), records)


    def get_object(self, tablename, record_dict):
        t = self.get_table(tablename)
        if t is None:
            raise Exception("No such table: '{0}'".format(tablename))

        rows = self.session.query(t).filter_by(**record_dict).all()
        if rows:
            l = len(rows)
            if l > 1:
                logging.warning("Найдено {0} одинаковых записей в '{1}'!".format(l, tablename))

            return rows[0]


    def reg_object(self, tablename, record_dict):
        c = self.get_model(tablename)
        if c is None:
            raise Exception("No such table: '{0}'".format(tablename))

        record = c(**record_dict)
        self.session.add(record)

        return record


    def reg_object1(self, tablename, record_dict, required=[]):
        c = self.get_model(tablename)
        if c is None:
            raise Exception("No such table: '{0}'".format(tablename))

        if not required:
            required = record_dict.keys()

        clause = {k: v for k, v in d.items() if k in required}
        rows = self.session.query(c).filter_by(**clause).all()
        if rows:
            l = len(rows)
            if l > 1:
                logging.warning("Найдено {0} одинаковых записей в '{1}'!".format(l, tablename))

            return rows[0]

        record = c(**record_dict)
        self.session.add(record)

        return record


    def debug(self, OBJ, msg):
        logging.debug(msg)


    def info(self, OBJ, msg):
        logging.info(msg)


    def warning(self, OBJ, msg):
        logging.warning(msg)


    def error(self, OBJ, msg, *args, **kargs):
        try:    msg = "" + msg
        except: msg = repr(msg)

        msg = """
=====================
    Error '{0}'!
    args: {1!r}
    kargs: {2!r}
=====================\n\n""".format(msg, args, kargs)

        logging.error(msg)


    def exception(self, OBJ, msg, *args, **kargs):
        try:    msg = "" + msg
        except: msg = repr(msg)

        tb_msg = traceback.format_exc()
        try:    tb_msg += "" + tb_msg
        except: tb_msg += repr(tb_msg)

        msg = """
=====================
    Exception '{0}'!
    args: {1!r}
    kargs: {2!r}
    {3}
=====================\n\n""".format(msg, args, kargs, tb_msg)

        logging.exception(msg)



def getDbUri(config={}):
    dbname = config.get('dbname')
    if dbname:
        return "{0}:///{1}/{2}.sqlite".format('sqlite', os.path.expanduser("~"), dbname)


    dburi = config.get("dburi")
    if not dburi:
        dbtype = config.get("dbtype")

        if dbtype == "sqlite":
            dbname = config.get("dbname", os.path.expanduser("~/default.sqlite"))
            dburi = "{0}:///{1}".format(dbtype, dbname)

        elif dbtype == "mysql":
            dbname = config.get("dbname", "default")
            host   = config.get("host",   "localhost")
            user   = config.get("user",   "root")
            passwd = config.get("passwd", "")
            dburi  = "{0}://{1}:{2}@{3}/{4}".format(dbtype, user, passwd, host, dbname)

    if not dburi:
        dburi = "sqlite://"

    return dburi
