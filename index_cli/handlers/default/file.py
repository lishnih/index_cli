#!/usr/bin/env python
# coding=utf-8
# Stan 2012-04-08, 2017-04-10

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os, time


def preparing_file(filename, options, DIR):
    basename = os.path.basename(filename)
    _, ext = os.path.splitext(basename)
    statinfo = os.stat(filename)
    size  = statinfo.st_size
    mtime = statinfo.st_mtime
    date = time.strftime("%d.%m.%Y", time.gmtime(mtime))

    return dict(
        _dirs_id = DIR.id,
        name = basename,
        ext = ext,
        size = size,
        date = date,
        _mtime = mtime,
    )


def proceed_file(filename, options, DIR, RECORDER):
    file_dict = preparing_file(filename, options, DIR)

    RECORDER.insert('files', [file_dict])
