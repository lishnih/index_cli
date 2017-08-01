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


    def __init__(self, options={}):
        self.dburi = getDbUri(options)
        self.engine = create_engine(self.dburi)
    
        if self.engine.name == "sqlite":
            filename = self.engine.url.database
            if filename:
                dirname = os.path.dirname(filename)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
    
        self.session = scoped_session(sessionmaker())
        self.session.configure(bind=self.engine)

#         import sqlite3
#         self.engine.text_factory = sqlite3.OptimizedUnicode

        self.model_cache = {}
    

    def create_all(self, base):
        self.base = base

        self.base.metadata.drop_all(bind=self.engine)

        self.base.metadata.create_all(self.engine)

        logging.info(["Db", self.engine.url.database])


    def get_model(self, tablename):
        if tablename in self.model_cache:
            return self.model_cache[tablename]

        for c in self.base._decl_class_registry.values():
            if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
                self.model_cache[tablename] = c
                return c


    def required(self, object_dict, required):
        for i in required:
            if i not in object_dict or object_dict[i] is None:
                return False

        return True


    def insert(self, tablename, records):
        t = self.base.metadata.tables.get(tablename)
        if t is None:
            print(self.base.metadata.tables.keys())
            raise Exception("No such table: '{0}'".format(tablename))
        self.engine.execute(t.insert(), records)



    def get_object(self, tablename, record_dict):
        c = self.get_model(tablename)
        if c is None:
            logging.error("Table '{0}' is not exist!".format(tablename))
            return []

        rows = self.session.query(c).filter_by(**record_dict).all()
        if rows:
            l = len(rows)
            if l > 1:
                logging.warning("Найдено {0} одинаковых записей в '{1}'!".format(l, tablename))

            return rows[0]


    def reg_object(self, tablename, record_dict):
        c = self.get_model(tablename)
        if c is None:
            logging.error("Table '{0}' is not exist!".format(tablename))
            return []

        record = c(**record_dict)
        self.session.add(record)
        self.session.commit()

        return record


    def reg_object1(self, tablename, record_dict, required=[]):
        c = self.get_model(tablename)
        if c is None:
            logging.error("Table '{0}' is not exist!".format(tablename))
            return []

        try:
            rows = self.session.query(c).filter_by(**record_dict).all()
            if rows:
                l = len(rows)
                record = rows[0]
                if l > 1:
                    logging.warning("Найдено {0} одинаковых записей в '{1}'!".format(l, tablename))
                return record

        except Exception as e:
            self.exception(record_dict, e.message)

        record = c(**record_dict)
        self.session.add(record)
        self.session.commit()

        return record


    def debug(self, OBJ, msg):
        logging.debug(msg)
    
    
    def info(self, OBJ, msg):
        logging.info(msg)
    
    
    def warning(self, OBJ, msg):
        logging.warning(msg)
    
    
    def error(self, OBJ, msg, *args, **kargs):
        try:    msg = "" + msg
        except: msg = repr(tb_msg)

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
