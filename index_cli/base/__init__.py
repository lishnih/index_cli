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
from .parse1 import proceed_parses
from .parse2 import parse_files

from ..models.slice_dir_file import Slice, Dir, File, Parse


def proceed(filename, options, recorder):
    os.stat_float_times(False)

    check = options.get('check')
    extras = json.dumps(options)
    if check:
        hash = options.get(check, '')
    else:
        m = hashlib.md5()
        m.update(extras)
        hash = m.hexdigest()

    slice_name = options.get('name', 'none')
    recorder.query(Slice).filter_by(name=slice_name, active=1, hash=hash).update({"active": 0})

    SLICE = Slice(name=slice_name, hash=hash, extras=extras)
    recorder.add(SLICE)   # При добавлении объекта с помощью add, объект кешируется в recorder
    recorder.commit()

    if os.path.isdir(filename):
        recorder.info("Processing directory", filename)

        # Dirs / files / parses
        proceed_dirs(filename, options, recorder)
        proceed_files(options, recorder)
        proceed_parses(options, recorder)
        parse_files(options, recorder)

    elif os.path.isfile(filename):
        recorder.info("Processing file", filename)

        # Dir
        dirname = os.path.dirname(filename)
        dir_dict = preparing_dir(dirname, options, recorder)
        DIR = Dir(**dir_dict)
        recorder.add(DIR)
        recorder.commit()

        # File
        file_dict = preparing_file(filename, options, recorder)
        FILE = File(**file_dict)
        recorder.add(FILE)
        recorder.commit()

        # Parse
        proceed_parses(options, recorder)
        parse_files(options, recorder)

    else:
        recorder.warning("Directory/file not found", filename)
        return -1

    return 0
