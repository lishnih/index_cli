#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-10

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from .backwardcompat import *
from .sheet_funcs import get_value_type


def proceed_sheet(sh, i=None, options={}):
    for y in range(sh.nrows):
        for x in range(sh.ncols):
            value, type = get_value_type(sh, y, x)
            if value:
                yield dict(
                    _sheet_name = sh.name,
                    value = value,
                    type = type,
                    col = x,
                    row = y
                )
