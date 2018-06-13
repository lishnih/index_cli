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
from .core.recorder import Recorder

from .base import proceed
from .models.slice_dir_file import Base, Error


def main(files=None, profile=None, options={}, recorder=None):
    files = files or options.get('files')
    profile = profile or options.get('profile', 'default')
    handler = options.get('handler', '.file_handlers.{0}'.format(profile))

    recorder = recorder or Recorder()

    dburi = getDbUri(options)
    if not dburi:
        msg = "Database not specified!"
        recorder.warning(msg)
        return -1

    # Устанавливаем соединение с БД
    engine, session = openDbUri(dburi)
    Base.metadata.create_all(session.bind)

    # Определяем сессию и таблицу для сообщений системы
    recorder.session = session
    recorder.error_class = Error

    if not files:
        msg = "Files not specified!"
        recorder.warning(msg)
        return -1

    package = options.get('package', __package__)
    entry = options.get('entry', 'proceed')
    opening = options.get('opening')
    closing = options.get('closing')
    recorder.debug("Common handler <{0}><{1}> with entry '{2}' and auxilaries '{3}'/'{4}'".format(package, handler, entry, opening, closing))

    try:
        mod = import_module(handler, package)
        func = getattr(mod, entry)
        opening_func = getattr(mod, opening) if opening else None
        closing_func = getattr(mod, closing) if closing else None
    except Exception as e:
        func = None
        opening_func = None
        closing_func = None
        msg = "Unable to load common handler, skipping!"
        recorder.exception(msg, e)

    # Определяем func, opening_func и closing_func и выполняем
    recorder.func = func
    recorder.opening_func = opening_func
    recorder.closing_func = closing_func
    er = proceed(files, options, recorder)

    return er
