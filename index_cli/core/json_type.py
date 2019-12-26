#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-27

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import json

from sqlalchemy.types import UserDefinedType, TypeDecorator, Text


class JsonType(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        return json.dumps(value, ensure_ascii=False)

    def process_result_value(self, value, dialect):
        return json.loads(value)


# class JsonType(UserDefinedType):
#     def get_col_spec(self, **kw):
#         return "JSON"
#
#     def bind_processor(self, dialect):
#         def process(value):
#             return json.dumps(value, ensure_ascii=False).encode('utf8')
#
#         return process
#
#     def result_processor(self, dialect, coltype):
#         def process(value):
#             return json.loads(value)
#
#         return process
