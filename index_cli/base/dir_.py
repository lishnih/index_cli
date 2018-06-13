#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-10

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os

from ..core.backwardcompat import *
from ..core.data_funcs import filter_match
from ..models.slice_dir_file import Dir


def preparing_dir(filename, options, recorder):
    filenames_encoding = options.get('filenames_encoding', 'cp1251')

    try:
        filename = unicode(filename)
    except UnicodeDecodeError:
        try:
            filename = filename.decode(filenames_encoding)
        except UnicodeDecodeError:
            recorder.warning("Filenames encoding is wrong", once="dir1")
            filename = unicode(filename, errors='replace')

    recorder.dir = filename
    SLICE = recorder.get_slice()
    return {
        '_slices_id': SLICE.id,
        'name': filename,
    }


def proceed_dirs(dirname, options, recorder):
    recorder.time

    dirs_filter = options.get('dirs_filter')
    exclude_dirs_filter = options.get('exclude_dirs_filter')
    followlinks = options.get('followlinks')
    loops = options.get('loops', 10000)

    dir_list = []
    amount = 0

    for dirname, dirs, files in os.walk(dirname, followlinks=followlinks):
        basename = os.path.basename(dirname)
        if filter_match(basename, dirs_filter):
            if filter_match(basename, exclude_dirs_filter, False):
                continue

            if amount == loops:
                recorder.bind.execute(Dir.__table__.insert(), dir_list)
                dir_list = []
                amount = 0

            dir_dict = preparing_dir(dirname, options, recorder)
            dir_list.append(dir_dict)
            amount += 1

    recorder.bind.execute(Dir.__table__.insert(), dir_list)
    dir_list = []  # Release memory

    recorder.info("Scan time: {0}, dirs: {1}".format(recorder.time, recorder.dir))
