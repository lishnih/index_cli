#!/usr/bin/env python
# coding=utf-8
# Stan 2012-04-08

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os
from datetime import datetime

from ...core.types23 import *     # str


def prepare_file(filename, options, recorder, DIR=None):
    basename = os.path.basename(filename)

    try:
        basename = str(basename)

    except UnicodeDecodeError:
        recorder.warning("Filename encoding is wrong!", target=repr(basename), once="file_1")
        return

    _, ext = os.path.splitext(basename)
    ext = ext.lower()

    try:
        statinfo = os.stat(filename)
        size = statinfo.st_size
        modified = datetime.fromtimestamp(statinfo.st_mtime)

    except:
        recorder.warning("Statinfo unaccessible!", target=filename, once="file_2")
        size = -1
        modified = None

    recorder.file = basename
    return dict(
        provider = recorder.provider,
        dir = DIR,
        name = basename,
#       path = path,
        ext = ext,
        size = size,
        modified = modified,
#       state = state,
        type = 1,
    )
