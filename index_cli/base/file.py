#!/usr/bin/env python
# coding=utf-8
# Stan 2012-04-08

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os
import time

from ..models.slice_dir_file import Slice, Dir, File


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
        size = None
        mtime = None
        date = None
    else:
        size = statinfo.st_size
        mtime = statinfo.st_mtime
        date = time.strftime("%d.%m.%Y", time.gmtime(mtime))

    status.file = basename
    return {
        '_dirs_id': DIR.id,
        'name': basename,
        'ext': ext,
        'size': size,
        'date': date,
        '_mtime': mtime,
    }


def proceed_files(options, status, session, SLICE):
    status.time

    loops = options.get('loops', 1000)

    file_list = []
    rows = session.query(Dir, Slice).join(Slice).filter_by(name=SLICE.name, active=1, hash=SLICE.hash).all()
    for i, j in rows:
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

    session.bind.execute(File.__table__.insert(), file_list)

    status.info("Scan time: {0}, files: {1}".format(status.time, status.file))
