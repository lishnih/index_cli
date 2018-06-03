#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-01

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import sys
import os
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


class Slice(Base, aStr):                  # rev. 20180601
    __tablename__ = 'slices'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)

    name = Column(String)                 # Имя обработчика
    created = Column(Integer, default=datetime.utcnow)  # Время создания
    active = Column(Integer, default=1)   # Активная обработка
    hash = Column(String)                 # Хэш
    extras = Column(Text)                 # Параметры

#   def __init__(self, **kargs):
#       kargs_reg = dict((key, value) for key, value in kargs.items() if hasattr(self, key))
#       Base.__init__(self, **kargs_reg)

    def __unicode__(self):
        return "<Slice '{0}' (id:{1})>".format(self.name, self.id)


class Dir(Base, aStr):                    # rev. 20180601
    __tablename__ = 'dirs'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    _slices_id = Column(Integer, ForeignKey('slices.id', onupdate='CASCADE', ondelete='CASCADE'))
    _slice = relationship(Slice, backref=backref(__tablename__, cascade='all, delete, delete-orphan'))

    name = Column(String)                 # Имя директории
    location = Column(String)             # Имя компьютера

#   def __init__(self, **kargs):
#       kargs_reg = dict((key, value) for key, value in kargs.items() if hasattr(self, key))
#       Base.__init__(self, **kargs_reg)

    def __unicode__(self):
        return "<Directory '{0}' (id:{1})>".format(self.name, self.id)


class File(Base, aStr):                   # rev. 20170503
    __tablename__ = 'files'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    _dirs_id = Column(Integer, ForeignKey('dirs.id', onupdate='CASCADE', ondelete='CASCADE'))
    _dir = relationship(Dir, backref=backref(__tablename__, cascade='all, delete, delete-orphan'))
#   _parses = relationship(Parse, secondary=RS_Parse.__table__,
#                                 backref=backref('_files', lazy='dynamic'))

    name = Column(String)                 # Имя файла
    ext = Column(String)                  # Расширение файла
    size = Column(Integer)                # Размер
    date = Column(String)                 # Время модификации
    _mtime = Column(Float)                # Время модификации

#   def __init__(self, **kargs):
#       kargs_reg = dict((key, value) for key, value in kargs.items() if hasattr(self, key))
#       Base.__init__(self, **kargs_reg)

    def __unicode__(self):
        return "<File '{0}' (id:{1})>".format(self.name, self.id)


class Parse(Base, aStr):                  # Rev. 2018-06-03
    __tablename__ = 'parses'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)

    md5 = Column(String)                  # MD5
    sha1 = Column(String)                 # SHA1
    last = Column(Integer)                # Предыдущая обработка

    def __unicode__(self):
        return "<Parse (id:{0})>".format(self.id)


class RS_Parse(Base, aStr):               # Rev. 2018-06-03
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


class Error(Base, aStr):                  # rev. 20180531
    __tablename__ = 'errors'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    _files_id = Column(Integer, ForeignKey('files.id', onupdate="CASCADE", ondelete="CASCADE"))
    _file = relationship(File, backref=backref(__tablename__, cascade='all, delete, delete-orphan'))

    name = Column(String)                 # Сообщение
    type = Column(String)                 # Тип

#   def __init__(self, **kargs):
#       kargs_reg = dict((key, value) for key, value in kargs.items() if hasattr(self, key))
#       Base.__init__(self, **kargs_reg)

    def __unicode__(self):
        return "<Error '{0}' '{1}' (id:{2})>".format(self.name, self.type, self.id)


class Sheet(Base, aStr):                  # rev. 20160424
    __tablename__ = 'sheets'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    _files_id = Column(Integer, ForeignKey('files.id', onupdate="CASCADE", ondelete="CASCADE"))
    _file = relationship(File, backref=backref(__tablename__, cascade='all, delete, delete-orphan'))

    name = Column(String)                 # Имя листа
    seq = Column(Integer)                 # Номер листа в файле
    ncols = Column(Integer)               # Кол-во колонок в листе
    nrows = Column(Integer)               # Кол-во строк в листе
    visible = Column(Integer)             # Видимость листа

#   def __init__(self, **kargs):
#       kargs_reg = dict((key, value) for key, value in kargs.items() if hasattr(self, key))
#       Base.__init__(self, **kargs_reg)

    def __unicode__(self):
        return "<Sheet '{0}' (id:{1})>".format(self.name, self.id)


class Cell(Base, aStr):                   # rev. 20170429
    __tablename__ = 'cells'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    _sheets_id = Column(Integer, ForeignKey('sheets.id', onupdate="CASCADE", ondelete="CASCADE"))
    _sheet = relationship(Sheet, backref=backref(__tablename__, cascade='all, delete, delete-orphan'))

    value = Column(String)                # Значение ячейки
    type = Column(Integer)                # Тип ячейки
    col = Column(Integer)                 # Колонка
    row = Column(Integer)                 # Ряд

#   def __init__(self, **kargs):
#       kargs_reg = dict((key, value) for key, value in kargs.items() if hasattr(self, key))
#       Base.__init__(self, **kargs_reg)

    def __unicode__(self):
        return "<Cell x:{0} y:{1} (id:{2})>".format(self.col, self.row, self.id)
