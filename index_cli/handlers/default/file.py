#!/usr/bin/env python
# coding=utf-8
# Stan 2012-04-08, 2017-04-10

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os, time


def preparing_file(filename, options, status, DIR):
    filenames_encoding = options.get('filenames_encoding', 'cp1251')
    basename = os.path.basename(filename)

    try:
        basename = unicode(basename)
    except UnicodeDecodeError:
        try:
            basename = basename.decode(filenames_encoding)
        except UnicodeDecodeError:
            basename = unicode(basename, errors='replace')

    _, ext = os.path.splitext(basename)

    try:
        statinfo = os.stat(filename)
    except:
        size  = None
        mtime = None
        date  = None
    else:
        size  = statinfo.st_size
        mtime = statinfo.st_mtime
        date  = time.strftime("%d.%m.%Y", time.gmtime(mtime))

    status.file = basename
    return dict(
        _dir = DIR,
        name = basename,
        ext = ext,
        size = size,
        date = date,
        _mtime = mtime,
    )


def proceed_file(filename, options, status, recorder, DIR):
    file_dict = preparing_file(filename, options, status, DIR)

    FILE = recorder.reg_object('files', file_dict)
