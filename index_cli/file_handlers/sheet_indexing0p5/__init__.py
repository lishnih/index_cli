#!/usr/bin/env python
# coding=utf-8
# Stan 2018-06-05

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from .book import proceed_book
from .model_sheet import Sheet, Cell


def do_stuff_file(filename, parse_id, options, status, session):
    for sh_list, p_list in proceed_book(filename, options, status):
        for sh_dict in sh_list:
            sh_dict['_parses_id'] = parse_id

        session.bind.execute(Sheet.__table__.insert(), sh_list)
        session.commit()

        rows = session.query(Sheet).filter_by(_parses_id=parse_id).all()
        sheet_index = {i.name: i.id for i in rows}

        for p_dict in p_list:
            p_dict['_sheets_id'] = sheet_index[p_dict['_sheet_name']]

        session.bind.execute(Cell.__table__.insert(), p_list)
        session.commit()

    return 1
