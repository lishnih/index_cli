#!/usr/bin/env python
# coding=utf-8
# Stan 2018-06-05

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from sqlalchemy import Table, Column, MetaData, Integer, String, Date, Float
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Insert

from .stuff.model_sheets import Base, Sheet
from .book import proceed_book


@compiles(Insert)
def append_string(insert, compiler, **kw):
    s = compiler.visit_insert(insert, **kw)
    if 'append_string' in insert.kwargs:
        return s + " " + insert.kwargs['append_string']
    return s


def opening(options, recorder):
    table_name = options.get('table_name', 'table1')
    table_items = options.get('table_items', [])
    table_items_sys = options.get('table_items_sys', [])

    table = Table(table_name, Base.metadata,
        Column('id', Integer, primary_key=True),
        Column('_sheet_id', Integer),
        Column('y', Integer, nullable=False, server_default='0'),
        *[Column(i, String, nullable=False, server_default='') for i in table_items + table_items_sys]
    )
    recorder._table = table
#   table.create(recorder.bind)
#   metadata.create_all(recorder.bind)

    Base.metadata.create_all(recorder.bind)


def proceed(filename, options, recorder, parse_id):
    for sh_list, p_list in proceed_book(filename, options, recorder, parse_id):
        if sh_list:
            recorder.bind.execute(Sheet.__table__.insert(), sh_list)
            recorder.commit()

        rows = recorder.query(Sheet).filter_by(_parse_id=parse_id).all()
        sheet_index = {i.name: i.id for i in rows}

#         j_set = set()

        for p_dict in p_list:
            p_dict['_sheet_id'] = sheet_index[p_dict['_sheet_name']]

        recorder.bind.execute(recorder._table.insert(), p_list)

        recorder.commit()

    return 1
