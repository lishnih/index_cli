#!/usr/bin/env python
# coding=utf-8
# Stan 2012-04-08

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .types23 import *


def getDbUri(config={}):
    dbhome = os.path.expanduser(config.get("dbhome", "~"))
    dbname = config.get("dbname", "default")
    if dbname:
        return "{0}:///{1}/{2}.sqlite".format('sqlite', dbhome, dbname)

    dburi = config.get("dburi")
    if not dburi:
        dbtype = config.get("dbtype")

        if dbtype == "sqlite":
            name = config.get("name", "default")
            dburi = "{0}:///{1}/{2}.sqlite".format(dbtype, dbhome, name)

        elif dbtype == "mysql":
            name = config.get("name", "default")
            host = config.get("host", "localhost")
            user = config.get("user", "root")
            passwd = config.get("passwd", "")
            dburi = "{0}://{1}:{2}@{3}/{4}".format(dbtype, user, passwd, host, name)

    if not dburi:
        dburi = "sqlite://"

    return dburi


def openDbUri(dburi, session=None):
    engine = create_engine(dburi)
    if engine.name == "sqlite":
        filename = engine.url.database
        if filename:
            dirname = os.path.dirname(filename)
            if dirname and not os.path.exists(dirname):
                os.makedirs(dirname)

    if not session:
        session = scoped_session(sessionmaker(bind=engine))

    return engine, session
