#!/usr/bin/env python
# coding=utf-8
# Stan 2012-04-06

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import re
import fnmatch

try:
    from .backwardcompat import *
except:
    from backwardcompat import *


def get_list(val):
    if val is None:
        return []
    elif isinstance(val, (list, tuple)):
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


def get_int_sequence(sequence_str, from_list=None):
    from_len = None if from_list is None else len(from_list)

    int_sequence = []
    str_sequence = get_str_sequence(sequence_str)
    for i in str_sequence:
        nosequence = True
        if i.isdigit():
            if not i == '0':
                i = int(i) - 1
                if i not in int_sequence:
                    int_sequence.append(i)
                nosequence = False
        else:
            res = re.match('^(\d*)-(\d*):?(\d*)$', i)
            if res:
                start, stop, step = res.group(1, 2, 3)
                start = int(start) - 1 if start else 0
                stop  = int(stop)      if stop  else from_len
                step  = int(step)      if step  else 1

            else:
                res = re.match('^(\d*):(-?\d*):?(\d*)$', i)
                if res:
                    start, stop, step = res.group(1, 2, 3)
                    start = int(start)    if start else 0
                    stop  = int(stop) + 1 if stop  else from_len
                    step  = int(step)     if step  else 1

                    if stop <= 0:
                        if from_len is None:
                            raise ValueError("Impossible to calculate the count of array! Array is not defined!")
                        stop = from_len - stop - 1

            if res:
                if stop is None:
                    raise ValueError("Impossible to calculate the count of array! Array is not defined!")

                for i in range(start, stop, step):
                    if i not in int_sequence:
                        int_sequence.append(i)
                nosequence = False

        if nosequence:
            raise ValueError("Wrong expression: '{0}'".format(i))

    int_sequence.sort()
    return int_sequence


def filter_match(name, filter_, empty=True, index=None):
    if filter_ is None:
        return empty

    elif isinstance(filter_, string_types):

        # Строка вида [i0, i1] интерпретируется как массив индексов
        res = re.match('^\[(.*)\]$', filter_)
        if res:
            filter_ = res.group(1)
            index_list = get_int_sequence(filter_)

            if index is None:
                assert None, 'index required!'
                return False

            return index in index_list

        # Строка вида (name0, name1) - как массив имён
        res = re.match('^\((.*)\)$', filter_)
        if res:
            filter_ = res.group(1)
            names_list = get_str_sequence(filter_)

            return name in names_list

        # Строка вида /patt/ - как шаблон
        res = re.match('^/(.*)/$', filter_)
        if res:
            filter_ = res.group(1)

            return True if re.match(filter_, name) else False

        # Все остальные строки принимаются как набор шаблонов fnmatch
        # разделённых точкой с запятой
        seq = get_str_sequence(filter_, delimiter=';')
        for i in seq:
            if fnmatch.fnmatch(name, i):
                return True
        return False

    elif isinstance(filter_, (tuple, list)):

        return name in filter_


if __name__ == '__main__':
    print(get_list('string'))
    print(get_str_sequence('"a123", b456'))
    print(get_int_sequence('1-5, 10-20'))
    print(get_int_sequence('1-5, 10-30:2'))
    print(get_int_sequence('1, 2, 3, 4'))
    print(filter_match('string', '[1-4]', 1))
    print(filter_match('name1', '(name1, name2)'))
    print(filter_match('name1', '/name\d/'))
    print(filter_match('file.xls', '*.xls; *.xlsx; *.xlsm'))
    print(filter_match('file.jpg', '*.xls; *.xlsx; *.xlsm'))
