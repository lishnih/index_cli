#!/usr/bin/env python
# coding=utf-8
# Stan 2013-04-22


import sys


if sys.version_info >= (3,):
    def cmp(a, b):
        return (a > b) - (a < b)

#   range = range

#   bytes = bytes
    unicode = type    # the trick: any unused type
#   str = str

    string_types = str,
    numeric_types = int, float, complex
    simple_types = int, float, complex, str, bytearray
    collections_types = list, tuple, set, frozenset
    all_types = (int, float, complex, str, bytearray,
                 list, tuple, set, frozenset, dict)

else:
#   cmp = cmp

    range = xrange

    bytes = str
#   unicode = unicode
    str = unicode

    string_types = basestring,
    numeric_types = int, long, float, complex
    simple_types = int, long, float, complex, basestring, bytearray
    collections_types = list, tuple, set, frozenset
    all_types = (int, long, float, complex, basestring, bytearray,
                 list, tuple, set, frozenset, dict)
