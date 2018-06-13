#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-10

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os

from ..core.backwardcompat import *
from ..models.slice_dir_file import Dir


def preparing_dir(filename, options, status, SLICE):
    filenames_encoding = options.get('filenames_encoding', 'cp1251')

    try:
        filename = unicode(filename)
    except UnicodeDecodeError:
        try:
            filename = filename.decode(filenames_encoding)
        except UnicodeDecodeError:
            status.warning("Filenames encoding is wrong", once="dir1")
            filename = unicode(filename, errors='replace')

    status.dir = filename
    return {
        '_slices_id': SLICE.id,
        'name': filename,
    }


def proceed_dirs(dirname, options, status, session, SLICE):
    status.time

    dirs_filter = options.get('dirs_filter')
    loops = options.get('loops', 10000)

    dir_list = []
    amount = 0

    for dirname, dirs, files in os.walk(dirname):
        if amount == loops:
            session.bind.execute(Dir.__table__.insert(), dir_list)
            dir_list = []
            amount = 0

        dir_dict = preparing_dir(dirname, options, status, SLICE)
        dir_list.append(dir_dict)
        amount += 1

    session.bind.execute(Dir.__table__.insert(), dir_list)
    dir_list = []

    status.info("Scan time: {0}, dirs: {1}".format(status.time, status.dir))
