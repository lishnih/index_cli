#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-10, 2017-03-09

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os

from .file import preparing_file, post_proceed_file


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

    dir_list = []
    for dirname, dirs, files in os.walk(dirname):
        dir_dict = preparing_dir(dirname, options, status)
        dir_list.append(dir_dict)

    recorder.insert('dirs', dir_list)

    status.info("Scan time: {0}, dirs: {1}".format(status.time, status.dir))


def post_proceed_dir(options, status, recorder):
    c = recorder.get_model('dirs')
    rows = recorder.session.query(c).all()

    status.time

    file_list = []
    for i in rows:
        dirname = i.name
        try:
            ldir = os.listdir(dirname)
        except OSError:
            status.warning("Access denied", dirname)
        else:
            for basename in sorted(ldir):
                filename = os.path.join(dirname, basename)
                if os.path.isfile(filename):
                    file_dict = preparing_file(filename, options, status, i)
                    file_list.append(file_dict)

    recorder.insert('files', file_list)

    status.info("Scan time: {0}, files: {1}".format(status.time, status.file))

    status.time

    post_proceed_file(options, status, recorder)

    status.info("Processing time: {0}".format(status.time))
