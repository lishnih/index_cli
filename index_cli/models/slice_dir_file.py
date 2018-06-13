#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-01

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import sys
from datetime import datetime

from sqlalchemy import Column, Integer, Float, String, Text, DateTime, PickleType, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship


Base = declarative_base()
if sys.version_info >= (3,):
    class aStr():
        def __str__(self):
            return self.__unicode__()
else:
    class aStr():
        def __str__(self):
            return self.__unicode__().encode('utf-8')


# For MySQL
# String = String(length=255)


class Slice(Base, aStr):        # rev. 20180601
    __tablename__ = 'slices'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)                 # Имя обработчика
    created = Column(Integer, nullable=False, default=datetime.utcnow)  # Время создания
    active = Column(Integer, nullable=False, default=1)   # Активная обработка
    hash = Column(String, nullable=False, default='')     # Хэш
    extras = Column(Text, nullable=False, default='')     # Параметры

#   def __init__(self, **kargs):
#       kargs_reg = {key: value for key, value in kargs.items() if hasattr(self, key)}
#       Base.__init__(self, **kargs_reg)

    def __unicode__(self):
        return "<Slice '{0}' (id:{1})>".format(self.name, self.id)


class Dir(Base, aStr):          # rev. 20180601
    __tablename__ = 'dirs'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    _slices_id = Column(Integer, ForeignKey('slices.id', onupdate='CASCADE', ondelete='CASCADE'))
    _slice = relationship(Slice, backref=backref(__tablename__, cascade='all, delete, delete-orphan'))

    name = Column(String, nullable=False)                         # Имя директории
    location = Column(String, nullable=False, server_default='')  # Имя компьютера

#   def __init__(self, **kargs):
#       kargs_reg = {key: value for key, value in kargs.items() if hasattr(self, key)}
#       Base.__init__(self, **kargs_reg)

    def __unicode__(self):
        return "<Directory '{0}' (id:{1})>".format(self.name, self.id)


class File(Base, aStr):         # rev. 20170503
    __tablename__ = 'files'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    _dirs_id = Column(Integer, ForeignKey('dirs.id', onupdate='CASCADE', ondelete='CASCADE'))
    _dir = relationship(Dir, backref=backref(__tablename__, cascade='all, delete, delete-orphan'))
#   _parses = relationship(Parse, secondary=RS_Parse.__table__,
#                                 backref=backref('_files', lazy='dynamic'))

    name = Column(String, nullable=False)                       # Имя файла
    ext = Column(String, nullable=False, server_default='')     # Расширение файла
    size = Column(Integer, nullable=False, server_default='0')  # Размер
    date = Column(String, nullable=False, server_default='')    # Время модификации
    _mtime = Column(Float, nullable=False, server_default='0')  # Время модификации

#   def __init__(self, **kargs):
#       kargs_reg = {key: value for key, value in kargs.items() if hasattr(self, key)}
#       Base.__init__(self, **kargs_reg)

    def __unicode__(self):
        return "<File '{0}' (id:{1})>".format(self.name, self.id)


class Parse(Base, aStr):        # Rev. 2018-06-04
    __tablename__ = 'parses'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)

    md5 = Column(String, nullable=False, server_default='')       # MD5 файла
    sha256 = Column(String, nullable=False, server_default='')    # SHA256 файла
    status = Column(Integer, nullable=False, server_default='0')  # Статус обработки
    last = Column(Integer, nullable=False, server_default='0')    # Предыдущая обработка

    def __unicode__(self):
        return "<Parse (id:{0})>".format(self.id)


class RS_Parse(Base, aStr):     # Rev. 2018-06-03
    __tablename__ = 'rs_file_parses'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    _files_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    _file = relationship(File, backref=backref(__tablename__, cascade='all, delete, delete-orphan'))
    _parses_id = Column(Integer, ForeignKey('parses.id'), nullable=False)
    _parse = relationship(Parse, backref=backref(__tablename__, cascade='all, delete, delete-orphan'))

    def __unicode__(self):
        return "<RS_Parse (file:{0}, parse:{1})>".format(self._files_id, self._parses_id)


File._parses = relationship(Parse, secondary=RS_Parse.__table__,
                            backref=backref('_files', lazy='dynamic'))

# f._parses -> sqlalchemy.orm.collections.InstrumentedList( ...перечень обработок... )
# p._files -> <sqlalchemy.orm.dynamic.AppenderQuery object at 0x03BFEC10>
# p._files.all() -> [ ...перечень файлов... ]
# f._parses.append(p)
# p._files.append(f)


class Error(Base, aStr):        # rev. 20180612
    __tablename__ = 'errors'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    _slices_id = Column(Integer, ForeignKey('slices.id', onupdate='CASCADE', ondelete='CASCADE'))
    _slice = relationship(Slice, backref=backref(__tablename__, cascade='all, delete, delete-orphan'))
    _parses_id = Column(Integer, ForeignKey('parses.id', onupdate="CASCADE", ondelete="CASCADE"))
    _parse = relationship(Parse, backref=backref(__tablename__, cascade='all, delete, delete-orphan'))

    name = Column(String, nullable=False)                         # Сообщение
    type = Column(String, nullable=False, server_default='INFO')  # Тип
    target = Column(String, nullable=False, server_default='')    # Место, где возникла ошибка
    traceback = Column(Text, nullable=False, server_default='')   # Traceback
    created = Column(Integer, nullable=False, default=datetime.utcnow)  # Время создания

    def __init__(self, name, type=None, slice_id=None, parse_id=None, target=None, traceback=None):
        Base.__init__(self, name=name, type=type, _slices_id=slice_id, _parses_id=parse_id, target=target, traceback=traceback)

    def __unicode__(self):
        return "<Error '{0}' '{1}' (id:{2})>".format(self.name, self.type, self.id)
