#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-10, 2017-03-09

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os, time, logging
import xlrd

from .file import proceed_file, preparing_file
from .book import proceed_book
from .data_funcs import filter_match


def preparing_dir(filename, options):
    return dict(
        name = filename,
    )


def proceed_dir(dirname, options, RECORDER):
    dirs_filter = options.get('dirs_filter')
    files_filter = options.get('files_filter')

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

    c = RECORDER.get_model('files')
    cs = RECORDER.get_model('sheets')

    rows = RECORDER.session.query(c).filter_by(ext='.xls').all()
    rows.extend(RECORDER.session.query(c).filter_by(ext='.xlsx').all())
    rows.extend(RECORDER.session.query(c).filter_by(ext='.xlsm').all())
    rows.extend(RECORDER.session.query(c).filter_by(ext='.xlsb').all())
    for row in rows:
        dirname = row._dir.name
        filename = row.name
        filename = os.path.join(dirname, filename)

        logging.info(filename)
        for sh_list, p_list in proceed_book(filename, options, row):
            if sh_list:
                RECORDER.insert('sheets', sh_list)

            if p_list:
                sheet_index = {}
                rows = RECORDER.session.query(cs).filter_by(_files_id=row.id).all()
                for i in rows:
                    sheet_index[i.name] = i.id
                for i in p_list:
                    i['_sheets_id'] = sheet_index[i['_sheet_name']]
                RECORDER.insert('cells', p_list)

    t4 = time.time()
    print("Время выполнения: {0}".format(t4-t3))
