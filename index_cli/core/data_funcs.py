#!/usr/bin/env python
# coding=utf-8
# Stan 2012-04-06

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import re
import fnmatch

if __name__ == '__main__':
    from types23 import *
else:
    from .types23 import *


def get_list(val):
    if val is None:
        return []
    elif isinstance(val, collections_types):
        return val
    else:
        return [val]


def get_str_sequence(sequence_str, delimiter=','):
    str_sequence = []

    sequence_list = re.findall('(")?(?(1)(.*?)|([^"{0}]+))((?(1)"))[{0} ]*'.format(delimiter), sequence_str)
    for q1, i1, i2, q2 in sequence_list:
        i = i2.strip() if i2 else i1
        str_sequence.append(i)

    return str_sequence


def get_int_sequence(sequence_str, from_list=None, machine=False, delimiter=',', default=None):
    int_sequence = []
    for i in get_str_sequence(sequence_str, delimiter):
        nosequence = True

        if i.isdigit():
            i = int(i)
            if i not in int_sequence:
                int_sequence.append(i)

            nosequence = False

        else:
            res = re.match('^(\d*)-(\d*):?(-?\d*)$', i)
            if res:
                start, stop, step = res.group(1, 2, 3)
                start = int(start) if start else 1
                stop = int(stop) if stop else None
                step = int(step) if step else 1

            else:
                res = re.match('^(-?\d*):(-?\d*):?(-?\d*)$', i)
                if res:
                    start, stop, step = res.group(1, 2, 3)
                    start = int(start) if start else 1
                    stop = int(stop) if stop else None
                    step = int(step) if step else 1

            if res:
                if stop is None:
                    if default:
                        stop = default

                    elif from_list:
                        stop = max(from_list)

                    else:
                        raise ValueError("Impossible to calculate the count of array! Array 'from_list' is not defined!")

                if stop >= 0:
                    stop += 1

                else:
                    stop -= 1

                    if step > 0:
                        step = -step

                for i in range(start, stop, step):
                    if i not in int_sequence:
                        int_sequence.append(i)

                nosequence = False

        if nosequence:
            raise ValueError("Wrong expression: '{0}'".format(i))

    if from_list:
        int_sequence = [i for i in int_sequence if i in from_list]

    int_sequence.sort()

    if machine:
        int_sequence = [i-1 for i in int_sequence if i]

    return int_sequence


def filter_match(name, filter_, empty=True, delimiter=','):
    if not filter_:
        return empty

    elif isinstance(filter_, string_types):

        # Строка вида [i0, i1] интерпретируется как массив индексов
        res = re.match('^\[(.*)\]$', filter_)
        if res:
            if isinstance(name, string_types) and name.isdigit():
                index = int(name)

            elif isinstance(name, int):
                index = name

            else:
                raise ValueError("Integer required: '{0!r}'!".format(name))

            filter_ = res.group(1)
            index_list = get_int_sequence(filter_, delimiter=delimiter, default=index)

            return index in index_list

        # Строка вида (name0, name1) - как массив имён
        res = re.match('^\((.*)\)$', filter_)
        if res:
            filter_ = res.group(1)
            names_list = get_str_sequence(filter_, delimiter)

            return name in names_list

        # Строка вида /patt/ - как шаблон
        res = re.match('^/(.*)/$', filter_)
        if res:
            filter_ = res.group(1)

            return True if re.match(filter_, name) else False

        # Все остальные строки принимаются как набор шаблонов fnmatch
        # разделённых точкой с запятой
        seq = get_str_sequence(filter_, ';')
        for i in seq:
            if fnmatch.fnmatch(name, i):
                return True

        return False

    elif isinstance(filter_, (tuple, list)):
        return name in filter_


if __name__ == '__main__':
    l = [
        (get_list, 'string'),
        (get_list, ['string1', 'string2']),
        (get_str_sequence, '"a123", b456'),
        (get_str_sequence, '"a123"; b456', ';'),
        (get_int_sequence, '1-5, 10-', [0, 1, 2, 5, 10, 13, 20]),
        (get_int_sequence, '1-5; 10-20', None, True, ';'),
        (get_int_sequence, '1-5; 10-', [0, 1, 2, 5, 10, 13, 20], True, ';'),
        (get_int_sequence, '1-5, 10-31:3'),
        (get_int_sequence, '5-:5', [10, 15, 20, 30, 40, 41, 42]),
        (get_int_sequence, '-:5', [10, 15, 20, 30, 40, 41, 42]),
        (get_int_sequence, '10-1:-3'),
        (get_int_sequence, '-1:-7:3'),
        (get_int_sequence, '-1:-7:-3'),
        (get_int_sequence, '1, 2, 3, 4'),
        (get_int_sequence, '1, 2, 3, 4', None, True),
        (filter_match, '3', '[1-4]'),
        (filter_match, 5, '[1-4]'),
        (filter_match, '3', '[1-]'),
        (filter_match, 5, '[1-]'),
        (filter_match, '3', '[4-]'),
        (filter_match, 5, '[-4]'),
        (filter_match, 'name1', '(name1, name2)'),
        (filter_match, 'name1', '/name\d/'),
        (filter_match, 'file.xls', '*.xls; *.xlsx; *.xlsm'),
        (filter_match, 'file.jpg', '*.xls; *.xlsx; *.xlsm'),
    ]

#   for f, *v in l:
    for i in l:
        f, v = i[0], i[1:]
        print(f.__name__, v, ':::', f(*v))
