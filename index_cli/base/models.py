#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-01

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import sys

from sqlalchemy import (Table, Column, Index, ForeignKey,
#                       PrimaryKeyConstraint, UniqueConstraint,
                        String, Text, Integer, Float, DateTime, PickleType)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func

from ..core.json_type import JsonType


Base = declarative_base()

# For MySQL
# String = String(length=512)


class Parser(Base):           # Rev. 20191221
    __tablename__ = 'parsers'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    profile = Column(String, nullable=False)
    rev = Column(String, nullable=False, server_default='')
    hash = Column(String, nullable=False, server_default='')
    options = Column(JsonType, nullable=False, server_default='{}')
    created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    Index('parser_', name, rev, hash, unique=True)

    def __init__(self, **kargs):
        kargs_reg = {key: value for key, value in kargs.items() if hasattr(self, key)}
        Base.__init__(self, **kargs_reg)

    def __repr__(self):
        return "<Parser {0} (id:{1})>".format(self.name, self.id)


class Provider(Base):         # Rev. 20181003
    __tablename__ = 'providers'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)
    created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __repr__(self):
        return "<Provider '{0}' (id:{1})>".format(self.name, self.id)


class Dir(Base):              # rev. 20181106
    __tablename__ = 'dirs'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    provider = relationship('Provider', backref=backref(__tablename__))

    id = Column(Integer, primary_key=True)
    _provider_id = Column(Integer, ForeignKey('providers.id'))

    name = Column(String, nullable=False)
    state = Column(Integer, nullable=False, server_default='1')
    path_id = Column(String, nullable=False, server_default='')

    Index('dir_', _provider_id, name, unique=True)

    def __init__(self, **kargs):
        kargs_reg = {key: value for key, value in kargs.items() if hasattr(self, key)}
        Base.__init__(self, **kargs_reg)

    def __repr__(self):
        return "<Directory '{0}' (id:{1})>".format(self.name, self.id)


class File(Base):             # rev. 20191225
    __tablename__ = 'files'
    __table_args__ = (
#       UniqueConstraint(
#           '_provider_id', '_dir_id', 'path', 'name', 'size', 'hash', 'md5', 'sha256'
#       ),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )

    provider = relationship('Provider', backref=backref(__tablename__))
    dir = relationship('Dir', backref=backref(__tablename__,
        cascade='all, delete, delete-orphan'))
    node = relationship('Node', backref=backref(__tablename__), lazy='selectin')

    id = Column(Integer, primary_key=True)
    _provider_id = Column(Integer, ForeignKey('providers.id'))
    _dir_id = Column(Integer, ForeignKey('dirs.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    _node_id = Column(Integer, ForeignKey('nodes.id'))

    name = Column(String, nullable=False, server_default='')
    path = Column(String, nullable=False, server_default='')
    ext = Column(String, nullable=False, server_default='')
    size = Column(Integer, nullable=False, server_default='0')
    modified = Column(DateTime(timezone=True), nullable=False, server_default='2000-01-01 12:00:00')
    state = Column(Integer, nullable=False, server_default='1')
    type = Column(Integer, nullable=False, server_default='1')

    # Дата, закодированная в имени файла
    ref_date = Column(DateTime(timezone=True), nullable=False, server_default='2000-01-01 12:00:00')

    # Аттрибуты облачных объектов
    path_id = Column(String, nullable=False, server_default='')
    url = Column(String, nullable=False, server_default='')
    hash = Column(String, nullable=False, server_default='')
    md5 = Column(String, nullable=False, server_default='')
    sha256 = Column(String, nullable=False, server_default='')
    revision = Column(String, nullable=False, server_default='')
    preview = Column(String, nullable=False, server_default='')

    debug = Column(Text, nullable=False, server_default='')

#   Index('file_', _provider_id, _dir_id, path, name, size, hash, md5, sha256, unique=True)

    def __init__(self, **kargs):
        kargs_reg = {key: value for key, value in kargs.items() if hasattr(self, key)}
        Base.__init__(self, **kargs_reg)

    def __repr__(self):
        return "<File '{0}' (id:{1})>".format(self.name, self.id)


class Node(Base):             # rev. 20190114
    __tablename__ = 'nodes'
    __table_args__ = (
#       UniqueConstraint(
#           'ext', 'size', 'modified', 'hash', 'md5', 'sha256'
#       ),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )

    id = Column(Integer, primary_key=True)

    ext = Column(String, nullable=False, server_default='')
    size = Column(Integer, nullable=False, server_default='0')
    modified = Column(DateTime(timezone=True), nullable=False, server_default='2000-01-01 12:00:00')
    hash = Column(String, nullable=False, server_default='')
    md5 = Column(String, nullable=False, server_default='')
    sha256 = Column(String, nullable=False, server_default='')

    Index('node_', ext, size, modified, hash, md5, sha256, unique=True)

    def __init__(self, **kargs):
        kargs_reg = {key: value for key, value in kargs.items() if hasattr(self, key)}
        Base.__init__(self, **kargs_reg)

    def __repr__(self):
        return "<Node '{0}' (id:{1})>".format(self.ext, self.id)


class Parse(Base):            # Rev. 20190111
    __tablename__ = 'parses'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    parser = relationship('Parser', backref=backref(__tablename__,
        cascade='all, delete, delete-orphan'))
    file = relationship('File', backref=backref(__tablename__,
        cascade='all, delete, delete-orphan'))
    node = relationship('Node', backref=backref(__tablename__,
        cascade='all, delete, delete-orphan'))

    id = Column(Integer, primary_key=True)
    _parser_id = Column(Integer, ForeignKey('parsers.id'))
    _file_id = Column(Integer, ForeignKey('files.id'))
    _node_id = Column(Integer, ForeignKey('nodes.id'))

    status = Column(Integer, nullable=False, server_default='0')
    created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __init__(self, **kargs):
        kargs_reg = {key: value for key, value in kargs.items() if hasattr(self, key)}
        Base.__init__(self, **kargs_reg)

    def __repr__(self):
        return "<Parse (id:{0})>".format(self.id)


class Error(Base):            # rev. 20181106
    __tablename__ = 'errors'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    parser = relationship('Parser', backref=backref(__tablename__,
        cascade='all, delete, delete-orphan'))
    parse = relationship('Parse', backref=backref(__tablename__,
        cascade='all, delete, delete-orphan'))

    id = Column(Integer, primary_key=True)
    _parser_id = Column(Integer, ForeignKey('parsers.id',
        onupdate="CASCADE", ondelete="CASCADE"))
    _parse_id = Column(Integer, ForeignKey('parses.id',
        onupdate="CASCADE", ondelete="CASCADE"))

    name = Column(String, nullable=False)                         # Сообщение
    level = Column(String, nullable=False, server_default='INFO') # Уровень
    target = Column(String, nullable=False, server_default='')    # Ориентир
    args = Column(Text, nullable=False, server_default='')        # args
    kargs = Column(Text, nullable=False, server_default='')       # kargs
    traceback = Column(Text, nullable=False, server_default='')   # Traceback
    created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __init__(self, **kargs):
        kargs_reg = {key: value for key, value in kargs.items() if hasattr(self, key)}
        Base.__init__(self, **kargs_reg)

    def __repr__(self):
        return "<Error '{0}' '{1}' (id:{2})>".format(self.name, self.type, self.id)


class Logging(Base):          # rev. 20181106
    __tablename__ = 'logging'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    parser = relationship('Parser', backref=backref(__tablename__,
        cascade='all, delete, delete-orphan'))
    parse = relationship('Parse', backref=backref(__tablename__,
        cascade='all, delete, delete-orphan'))

    id = Column(Integer, primary_key=True)
    _parser_id = Column(Integer, ForeignKey('parsers.id',
        onupdate="CASCADE", ondelete="CASCADE"))
    _parse_id = Column(Integer, ForeignKey('parses.id',
        onupdate="CASCADE", ondelete="CASCADE"))

    logger = Column(String, nullable=False, server_default='')
    level = Column(String, nullable=False, server_default='INFO')
    trace = Column(String, nullable=False, server_default='')
    message = Column(String, nullable=False, server_default='')

    target = Column(String, nullable=False, server_default='')    # Ориентир
    args = Column(Text, nullable=False, server_default='')        # args
    kargs = Column(Text, nullable=False, server_default='')       # kargs
    created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __repr__(self):
        return "<Log record (id:{0})>".format(self.id)
