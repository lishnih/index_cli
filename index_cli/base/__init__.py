#!/usr/bin/env python
# coding=utf-8
# Stan 2013-09-07

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os
import hashlib
import importlib
import json

from .dir_ import preparing_dir, proceed_dirs
from .file import preparing_file, proceed_files
from .parse import proceed_parses

from ..models.slice_dir_file import Slice, Dir, File, Parse, Error


def proceed(filename, options, status, session):
    os.stat_float_times(False)

    check = options.get('check')
    extras = json.dumps(options)
    if check:
        hash = options.get(check)
    else:
        m = hashlib.md5()
        m.update(extras)
        hash = m.hexdigest()

    slice_name = options.get('name', 'none')
    session.query(Slice).filter_by(name=slice_name, active=1, hash=hash).update({"active": 0})

    SLICE = Slice(name=slice_name, hash=hash, extras=extras)
    session.add(SLICE)
    session.commit()

    if os.path.isdir(filename):
        status.info("Processing directory", filename)

        # Dir
        proceed_dirs(filename, options, status, session, SLICE)
        proceed_files(options, status, session, SLICE)
        proceed_parses(options, status, session, SLICE)

    elif os.path.isfile(filename):
        status.info("Processing file", filename)

        # Dir
        dirname = os.path.dirname(filename)
        dir_dict = preparing_dir(dirname, options, status, SLICE)
        DIR = Dir(**dir_dict)
        session.add(DIR)
        session.commit()

        # File
        file_dict = preparing_file(filename, options, status, DIR)
        FILE = File(**file_dict)
        session.add(FILE)
        session.commit()

    else:
        status.warning("Directory/file not found", filename)
        return -1, "Directory/file not found!"

    return 0, "Finished successfully!"
