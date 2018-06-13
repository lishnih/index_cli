#!/usr/bin/env python
# coding=utf-8
# Stan 2018-06-05

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from .stuff.model_sheets import Base, Sheet, Cell
from .book import proceed_book


def opening(options, recorder):
    Base.metadata.create_all(recorder.bind)


def proceed(filename, parse_id, options, recorder):
    for sh_list, p_list in proceed_book(filename, options, recorder):
        for sh_dict in sh_list:
            sh_dict['_parses_id'] = parse_id

        recorder.bind.execute(Sheet.__table__.insert(), sh_list)
        recorder.commit()

        rows = recorder.query(Sheet).filter_by(_parses_id=parse_id).all()
        sheet_index = {i.name: i.id for i in rows}

        for p_dict in p_list:
            p_dict['_sheets_id'] = sheet_index[p_dict['_sheet_name']]

        recorder.bind.execute(Cell.__table__.insert(), p_list)
        recorder.commit()

    return 1
