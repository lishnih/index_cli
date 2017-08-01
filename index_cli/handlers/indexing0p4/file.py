#!/usr/bin/env python
# coding=utf-8
# Stan 2012-04-08, 2017-04-10

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os, time, logging

from .book import proceed_book


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


def proceed_file(filename, options, RECORDER, DIR):
    file_dict = preparing_file(filename, options, DIR)

    RECORDER.insert('files', [file_dict])

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
