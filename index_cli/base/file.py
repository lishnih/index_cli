#!/usr/bin/env python
# coding=utf-8
# Stan 2012-04-08

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os
import time

from ..core.backwardcompat import *
from ..core.data_funcs import filter_match
from ..models.slice_dir_file import Slice, Dir, File


def preparing_file(filename, options, recorder, DIR):
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
        size = None
        mtime = None
        date = None
    else:
        size = statinfo.st_size
        mtime = statinfo.st_mtime
        date = time.strftime("%d.%m.%Y", time.gmtime(mtime))

    recorder.file = basename
    return {
        '_dirs_id': DIR.id,
        'name': basename,
        'ext': ext,
        'size': size,
        'date': date,
        '_mtime': mtime,
    }


def proceed_files(options, recorder):
    recorder.time

    files_filter = options.get('files_filter')
    loops = options.get('loops', 10000)

    file_list = []
    amount = 0

    SLICE = recorder.get_slice()
    rows = recorder.query(Dir, Slice).join(Slice).filter_by(name=SLICE.name, active=1, hash=SLICE.hash).all()
    for DIR, SLICE in rows:
        dirname = DIR.name
        try:
            ldir = os.listdir(dirname)
        except OSError:
            recorder.warning("Access denied", dirname)
        else:
            for basename in sorted(ldir):
                if filter_match(basename, files_filter):
                    if amount == loops:
                        recorder.bind.execute(File.__table__.insert(), file_list)
                        file_list = []
                        amount = 0

                    filename = os.path.join(dirname, basename)
                    file_dict = preparing_file(filename, options, recorder, DIR)
                    file_list.append(file_dict)
                    amount += 1

    recorder.bind.execute(File.__table__.insert(), file_list)
    file_list = []  # Release memory

    recorder.info("Scan time: {0}, files: {1}".format(recorder.time, recorder.file))
