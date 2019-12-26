#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-10

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os

from ...core.types23 import *     # str


def prepare_dir(filename, options, recorder):
    try:
        filename = str(filename)

    except UnicodeDecodeError:
        recorder.warning("Filename encoding is wrong!", target=repr(filename), once="dir_1")
        return

    recorder.dir = filename
    return dict(
        provider = recorder.provider,
        name = filename,
    )
