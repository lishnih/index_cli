#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-12, 2017-03-09

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import sys, os, importlib, logging

from .lib.backwardcompat import *
from .recorder import Recorder


def main(files, profile=None, options=None):
    if not profile:
        profile = 'default'
    if not options:
        options = {}


    # Загружаем структуру БД
    dbmodels = options.get('dbmodels', 'dir_file')
    models = __package__ + '.models.' + dbmodels
    try:
        models_module = importlib.import_module(models)
    except Exception as e:
        logging.exception(["Error in the module", models])
        return


    # Загружаем регистратор
    RECORDER = Recorder(options)
    RECORDER.create_all(models_module.Base)


    # Загружаем обработчик
    handler = __package__ + '.handlers.' + profile
    try:
        handler_module = importlib.import_module(handler)
    except Exception as e:
        logging.exception(["Error in the handler", handler])
        return

    # Обработчик имеет точку входа 'proceed'
    if not hasattr(handler_module, 'proceed'):
        logging.error(["Function 'proceed' is missing in the handler", handler])
        return


    # Обработка
    if not isinstance(files, collections_types):
        files = [files]

    for i in files:
        i = os.path.abspath(i)
        try:
            handler_module.proceed(i, options, RECORDER)
        except Exception as e:
            logging.exception(["Error during handle file", i])

    if not files:
        logging.warning("Files not specified!")
