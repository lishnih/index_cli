#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-10

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import re

from .stuff.sheet_funcs import float_normalize, get_sequence, get_date


def remove_ws(sentence, func=None):
    if hasattr(sentence, 'split'):
        sentence = ''.join(sentence.split())

        if func:
            return func(sentence)

    return sentence


def proceed_sheet(sh, recorder, i=None, options={}):
    table_items = options.get('table_items', [])
#   split_column = options.get('split_column')
    date_column = options.get('date_column', 'date')
    check_column = options.get('check_column')

    check_with_row = options.get('check_with_row')
    if check_with_row is not None:
        indexes_items = sh.row_values(check_with_row)
        indexes_items = [str(int(i)) if isinstance(i, float) else i for i in indexes_items]
#       items_len = len(indexes_items)

        if check_column not in indexes_items:
            check_column = None

    else:
        indexes_items = None
        items_len = len(table_items)

        if check_column not in table_items:
            check_column = None

    recorder.debug({
        'check_column': check_column,
        'table_items': table_items,
        'date_column': date_column,
        'check_with_row': check_with_row,
        'indexes_items': indexes_items,
    }, _level=3)

    for y in range(sh.nrows):
        values_y = sh.row_values(y)
        if values_y:
            recorder.debug(y, _level=5)
            recorder.debug(values_y, _level=5)

            values_y = [float_normalize(i) if isinstance(i, float) else i for i in values_y]
            y1 = y + 1

            if indexes_items:
                d = dict(zip(indexes_items, values_y))

            else:
                d = dict(zip(table_items, values_y[:items_len]))

            recorder.debug(d, _level=5)

            # Строки с пустой контрольной ячейкой пропускаются
            if check_column and not d.get(check_column):
                recorder.debug("Omitted: {0!r} ({1})".format(d, y1), _level=4)
                continue

            # Выводим первую строки для сверки
            if not y:
                recorder.debug("======= Sheet: {0!r} ({1}) =======".format(sh.name, y1), _level=3)
                for i, kv in enumerate(d.items(), 1):
                    k, v = kv
                    recorder.debug("{0:3} {1:16}: {2}".format(i, k, v), _level=3)

            # Определяемся с датой
            date_str = ''
            date = d.get(date_column)
            if date:
                _, date_str = get_date(date)
            d['date_str'] = date_str

            recorder.debug("Saved: ({0})".format(y1), _level=4)
            yield dict(
                _sheet_name = sh.name,
                y = y1,
                **d
            )
