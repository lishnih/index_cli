#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-12

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import sys
import os
from importlib import import_module

from .core.backwardcompat import *
from .core.db import getDbUri, openDbUri
from .core.status1 import status1
from .base import proceed
from .models.slice_dir_file import Base


def main(files='', profile='default', options={}, status=status1):
    status.reset()

    files = files or options.get('files')
    profile = profile or options.get('profile')

    if not files:
        msg = "Files not specified!"
        status.warning(msg)
        return -1, msg

    dburi = getDbUri(options)
    if not dburi:
        msg = "Database not specified!"
        status.warning(msg)
        return -1, msg

    engine, session = openDbUri(dburi)
    Base.metadata.create_all(session.bind)

    # Выполняем
    code, msg = proceed(files, options, status, session)

    status.message = "Finished!"
    return code, msg
