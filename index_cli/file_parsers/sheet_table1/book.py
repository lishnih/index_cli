#!/usr/bin/env python
# coding=utf-8
# Stan 2012-04-08

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os
import xlrd

from .stuff.data_funcs import filter_match
from .sheet import proceed_sheet


def proceed_book(filename, options, recorder, parse_id):
    sh_list = []
    p_list = []
    count = 0
    max = 500000

    basename = os.path.basename(filename)
    root, ext = os.path.splitext(basename)
    ext = ext.lower()

    if ext in ['.xls', '.xlsx', '.xlsm', '.xlsb']:
        try:
            if ext == '.xls':
                book = xlrd.open_workbook(filename, on_demand=True, formatting_info=True)
            else:
                book = xlrd.open_workbook(filename, on_demand=True)

        except Exception as e:
            recorder.exception("Some issue during proceed_book",
                target=filename,
                parse_id = parse_id,
                once="sheet_indexing_book_1")

        else:
            sheets = book.sheet_names()
            sheets_filter = options.get('sheets_filter')
            sheets_list = [i for i in sheets if filter_match(i, sheets_filter)]

            for name in sheets_list:
                sh = book.sheet_by_name(name)
                seq = sheets.index(name)

                sh_dict = dict(
                    _parse_id = parse_id,
                    name = sh.name,
                    seq = seq,
                    ncols = sh.ncols,
                    nrows = sh.nrows,
                    visible = sh.visibility,
                )
                sh_list.append(sh_dict)

                # Cells
                for p_dict in proceed_sheet(sh, recorder, seq, options):
                    p_list.append(p_dict)
                    count += 1

                    if count >= max:
                        recorder.debug("Flushing...", _debug=2)
                        yield sh_list, p_list

                        sh_list = []
                        p_list = []
                        count = 0

                book.unload_sheet(name)

            yield sh_list, p_list
