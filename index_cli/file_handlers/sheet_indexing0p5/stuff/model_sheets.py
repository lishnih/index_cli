#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-01

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import sys

from sqlalchemy import Column, Integer, Float, String, Text, DateTime, PickleType, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

from ...models.slice_dir_file import Base, aStr, Parse, String


class Sheet(Base, aStr):        # rev. 20180605
    __tablename__ = 'sheets'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    _parses_id = Column(Integer, ForeignKey('parses.id', onupdate="CASCADE", ondelete="CASCADE"))
    _parse = relationship(Parse, backref=backref(__tablename__, cascade='all, delete, delete-orphan'))

    name = Column(String, nullable=False)                           # Имя листа
    seq = Column(Integer, nullable=False, server_default='-1')      # Номер листа в файле
    ncols = Column(Integer, nullable=False, server_default='-1')    # Кол-во колонок в листе
    nrows = Column(Integer, nullable=False, server_default='-1')    # Кол-во строк в листе
    visible = Column(Integer, nullable=False, server_default='-1')  # Видимость листа

#   def __init__(self, **kargs):
#       kargs_reg = {key: value for key, value in kargs.items() if hasattr(self, key)}
#       Base.__init__(self, **kargs_reg)

    def __unicode__(self):
        return "<Sheet '{0}' (id:{1})>".format(self.name, self.id)


class Cell(Base, aStr):         # rev. 20170429
    __tablename__ = 'cells'
    __table_args__ = {'mysql_engine': 'MyISAM', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    _sheets_id = Column(Integer, ForeignKey('sheets.id', onupdate="CASCADE", ondelete="CASCADE"))
    _sheet = relationship(Sheet, backref=backref(__tablename__, cascade='all, delete, delete-orphan'))

    value = Column(String, nullable=False, server_default='')     # Значение ячейки
    type = Column(Integer, nullable=False, server_default='-1')   # Тип ячейки
    col = Column(Integer, nullable=False, server_default='-1')    # Колонка
    row = Column(Integer, nullable=False, server_default='-1')    # Ряд

#   def __init__(self, **kargs):
#       kargs_reg = {key: value for key, value in kargs.items() if hasattr(self, key)}
#       Base.__init__(self, **kargs_reg)

    def __unicode__(self):
        return "<Cell x:{0} y:{1} (id:{2})>".format(self.col, self.row, self.id)
