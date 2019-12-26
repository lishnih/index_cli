#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-12

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import sys
import os
import logging
from importlib import import_module

from .core.types23 import *
from .core.db import getDbUri, openDbUri
from .core.recorder import Recorder

from . import __version__ as index_version
from .base import proceed
from .base.parse import parse_files
from .base.models import Base, Error


def main(files=None, profile=None, options={}, recorder=None, **kargs):
    files = files or options.get('files')
    profile = profile or options.get('profile', 'default')
    parser = options.get('parser') or \
        '.file_parsers.{0}'.format(profile) if profile else None

    # Инициализируем recorder и устанавливаем уровень debug_level
    recorder = recorder or Recorder()
    recorder.logging_class = Error
    recorder.set_debug_level(options.get('debug_level', 1))

    # Устанавливаем уровень logging и выводим параметры
    logging_level = options.get('logging_level', 'WARNING')
    logging.basicConfig(level=logging.getLevelName(logging_level))
    logging.debug((index_version, logging_level, logging.root.level, \
        recorder.get_debug_level()))

    # Определяем dburi
    dburi = getDbUri(options)
    if not dburi:
        recorder.warning("Database not specified!")
        return -11

    # Устанавливаем соединение с БД
    engine, session = openDbUri(dburi)
    Base.metadata.create_all(session.bind)

    # Определяем сессию и таблицу для сообщений системы
    recorder.session = session

    if not files:
        recorder.warning("Files not specified!")
        return -1

    # Сканирование файлов
    # (создание записей директорий, файлов и элементов файлов)
    files = os.path.expanduser(files)
    try:
        source_type = proceed(files, options, recorder)

    except Exception as e:
        recorder.exception("Exception during scanning!", target=str(files))
        raise

    if not parser:
        recorder.debug("Parser not specified, exiting!")
        return -2

    # Загружаем парсер
    package = options.get('package', __package__)
    recorder.debug(('Loading of parser', package, parser))
    try:
        mod = import_module(parser, package)

    except Exception as e:
        recorder.exception("Unable to load the parser, exiting!",
            target="{0}{1}".format(package, parser))
        raise

    entry = options.get('entry')
    opening = options.get('opening')
    closing = options.get('closing')
    recorder.debug("Parser loaded with entry '{0}' and auxilaries '{1}'/'{2}'".\
        format(entry, opening, closing),
        target="{0}.{1}".format(package, parser))

    recorder.func = getattr(mod, entry) if entry else None
    opening_func = getattr(mod, opening) if opening else None
    closing_func = getattr(mod, closing) if closing else None

    er = 0
    try:
        if opening_func:
            opening_func(options, recorder)
        if recorder.func:
            er = parse_files(files, source_type, options, recorder)
        if closing_func:
            closing_func(options, recorder)

    except Exception as e:
        recorder.exception("Exception during parsing!", target=str(files))

    return er
