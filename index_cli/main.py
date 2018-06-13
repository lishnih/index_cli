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
from .core.status_class import Status

from .base import proceed
from .models.slice_dir_file import Base


def main(files=None, profile=None, options={}, status=None):
    files = files or options.get('files')
    profile = profile or options.get('profile', 'default')
    handler = options.get('handler', '.file_handlers.{0}'.format(profile))

    status = status or Status()
    status.reset()

    if not files:
        msg = "Files not specified!"
        status.warning(msg)
        return -1

    dburi = getDbUri(options)
    if not dburi:
        msg = "Database not specified!"
        status.warning(msg)
        return -1

    engine, session = openDbUri(dburi)
    Base.metadata.create_all(session.bind)

    package = options.get('package', __package__)
    entry = options.get('entry', 'main')
    status.debug("Common handler <{0}><{1}> with entry '{2}'".format(package, handler, entry))
    try:
        mod = import_module(handler, package)
        func = getattr(mod, entry)
    except Exception as e:
        func = None
        msg = "Unable to load common handler, skipping!"
        status.exception(msg, e)

    # Выполняем
    er = proceed(files, options, status, session, func)

    return er
