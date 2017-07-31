#!/usr/bin/env python
# coding=utf-8
# Stan 2013-09-07, 2017-03-09

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os, logging

from .dir import proceed_dir
from .file import proceed_file


def proceed(filename, options, RECORDER=None):
    if os.path.isdir(filename):
        logging.info(["Processing directory", filename])

        # Dir
        proceed_dir(filename, options, RECORDER)

    elif os.path.isfile(filename):
        logging.info(["Processing file", filename])

        # Dir
        dirname = os.path.dirname(filename)
        dir_dict = dict(name=dirname)
        DIR = RECORDER.reg_object1('dirs', dir_dict)

        # File
        proceed_file(filename, options, RECORDER, DIR)

    else:
        logging.warning(["Directory/file not found", filename])
