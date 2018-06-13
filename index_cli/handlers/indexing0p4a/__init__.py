#!/usr/bin/env python
# coding=utf-8
# Stan 2013-09-07, 2017-03-09

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os, importlib

from .dir import proceed_dir, post_proceed_dir
from .file import proceed_file, post_proceed_file
from ...recorder import Recorder


def opening(package, options, status):
    dbmodels = options.get('dbmodels', 'dir_file')

    # Загружаем модели
    models = package + '.models.' + dbmodels
#   models = __package__ + '.models.' + dbmodels
    models_module = importlib.import_module(models)

    # Создаём регистратор
    recorder = Recorder(options, base=models_module.Base)
    recorder.drop_all()
    recorder.create_all()

    return dict(recorder=recorder)


def proceed(filename, options, status, recorder):
    if os.path.isdir(filename):
        status.info("Processing directory", filename)

        # Dir
        proceed_dir(filename, options, status, recorder)
        post_proceed_dir(options, status, recorder)

    elif os.path.isfile(filename):
        status.info("Processing file", filename)

        # Dir
        dirname = os.path.dirname(filename)
        dir_dict = dict(name=dirname)
        DIR = recorder.reg_object1('dirs', dir_dict)

        # File
        proceed_file(filename, options, status, recorder, DIR)
        post_proceed_file(options, status, recorder)

    else:
        status.warning("Directory/file not found", filename)


def closing(options, status, recorder):
    status.message = "Finished"
