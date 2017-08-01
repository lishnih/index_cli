#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-10, 2017-03-09

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os, time, logging

from .file import preparing_file


def preparing_dir(filename, options):
    try:
        dir_dict = dict(name=filename)
    except Exception, e:
        logging.warning(filename)
        dir_dict = dict(name=dirname.decode('cp1251'))

    return dir_dict


def proceed_dir(dirname, options, RECORDER):
    t1 = time.time()

    dir_list = []
    ndirs = 0

    for dirname, dirs, files in os.walk(dirname):
        dir_dict = preparing_dir(dirname, options)
        dir_list.append(dir_dict)
        ndirs += 1

    RECORDER.insert('dirs', dir_list)

    t2 = time.time()
    print("Время выполнения: {0}, кол-во директорий: {1}".format(t2-t1, ndirs))

    c = RECORDER.get_model('dirs')
    rows = RECORDER.session.query(c).all()

    file_list = []
    nfiles = 0

    for i in rows:
        dirname = i.name
        try:
            ldir = os.listdir(dirname)
        except Exception as e:
            logging.warning(["Access denied", dirname])
            continue

        for basename in sorted(ldir):
            filename = os.path.join(dirname, basename)
            if os.path.isfile(filename):
                file_dict = preparing_file(filename, options, i)
                if file_dict:
                    file_list.append(file_dict)
                    nfiles += 1

    RECORDER.insert('files', file_list)

    t3 = time.time()
    print("Время выполнения: {0}, кол-во файлов: {1}".format(t3-t2, nfiles))
