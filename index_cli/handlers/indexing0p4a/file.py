#!/usr/bin/env python
# coding=utf-8
# Stan 2012-04-08, 2017-04-10

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os, time

from .book import proceed_book


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
        _dirs_id = DIR.id,
        name = basename,
        ext = ext,
        size = size,
        date = date,
        _mtime = mtime,
    )


def proceed_file(filename, options, status, recorder, DIR):
    file_dict = preparing_file(filename, options, status, DIR)

    recorder.insert('files', [file_dict])


def post_proceed_file(options, status, recorder):
    c = recorder.get_model('files')
    cs = recorder.get_model('sheets')

    rows = recorder.session.query(c).filter(c.ext.in_(['.xls', '.xlsx', '.xlsm', '.xlsb'])).all()
    for row in rows:
        dirname = row._dir.name
        filename = row.name
        filename = os.path.join(dirname, filename)

        status.info(filename)
        for sh_list, p_list in proceed_book(filename, options, status, row):
            if sh_list:
                recorder.insert('sheets', sh_list)

            if p_list:
                sheet_index = {}
                rows = recorder.session.query(cs).filter_by(_files_id=row.id).all()
                for i in rows:
                    sheet_index[i.name] = i.id
                for i in p_list:
                    i['_sheets_id'] = sheet_index[i['_sheet_name']]
                recorder.insert('cells', p_list)
