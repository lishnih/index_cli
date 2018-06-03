#!/usr/bin/env python
# coding=utf-8
# Stan 2012-04-08

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .backwardcompat import *


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
            host = config.get("host",   "localhost")
            user = config.get("user",   "root")
            passwd = config.get("passwd", "")
            dburi = "{0}://{1}:{2}@{3}/{4}".format(dbtype, user, passwd, host, dbname)

    if not dburi:
        dburi = "sqlite://"

    return dburi


def openDbUri(dburi, session=None):
    engine = create_engine(dburi)
    if engine.name == "sqlite":
        filename = engine.url.database
        if filename:
            dirname = os.path.dirname(filename)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

    if not session:
        session = scoped_session(sessionmaker())
        session.configure(bind=engine)

    return engine, session
