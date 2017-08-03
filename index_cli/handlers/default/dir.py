#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-10, 2017-03-09

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os

from .file import proceed_file


def preparing_dir(filename, options, status):
    filenames_encoding = options.get('filenames_encoding', 'cp1251')

    try:
        filename = unicode(filename)
    except UnicodeDecodeError:
        try:
            filename = filename.decode(filenames_encoding)
        except UnicodeDecodeError:
            filename = unicode(filename, errors='replace')

    status.dir = filename
    return dict(name=filename)


def proceed_dir(dirname, options, status, recorder):
    dirs_filter = options.get('dirs_filter')
    files_filter = options.get('files_filter')

    status.time

    for dirname, dirs, files in os.walk(dirname):
        dir_dict = preparing_dir(dirname, options, status)
        DIR = recorder.reg_object('dirs', dir_dict)

        for i in files:
            filename = os.path.join(dirname, i)
            FILE = proceed_file(filename, options, status, recorder, DIR)

    status.info("Processing time: {0}, dirs: {1}, files: {2}".format(status.time, status.dir, status.file))
