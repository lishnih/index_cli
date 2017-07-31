#!/usr/bin/env python
# coding=utf-8
# Stan 2017-04-02

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import sys, os, importlib, time, csv, codecs, cStringIO, logging
import xlrd

from .lib.backwardcompat import *
from .lib.dump_html import plain
from .recorder import Recorder


def main(options):


    # Загружаем структуру БД
    dbmodels = options.get('dbmodels', 'dir_file')
    models = __package__ + '.models.' + dbmodels
    try:
        models_module = importlib.import_module(models)
    except Exception as e:
        logging.exception(["Error in the module", models])
        return


    # Загружаем регистратор
    RECORDER = Recorder(options)
    RECORDER.base = models_module.Base


    t1 = time.time()

    c1 = RECORDER.get_model('cells')
    c2 = RECORDER.get_model('sheets')
    c3 = RECORDER.get_model('files')
    c4 = RECORDER.get_model('dirs')

    count = RECORDER.session.query(c1, c2, c3, c4).join(c2).join(c3).join(c4).count()
    logging.info("Records: {0}".format(count))

    offset = 0
    limit = 200000

    filename = "{0}.csv".format(options.get('output', 'output'))
    with open(filename, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=b';')
        writer.writerow(["value", "row", "col", "sheet", "file", "dir"])

        while offset < count:
            rows = RECORDER.session.query(c1, c2, c3, c4).join(c2).join(c3).join(c4).slice(offset, offset+limit).all()
            logging.info([offset, limit, len(rows)])
            for i in rows:
                cell, sheet, file, dir = i
                row = [cell.value, cell.row, cell.col, sheet.name, file.name, dir.name]
                row = [s.encode("utf-8") if isinstance(s, string_types) else s for s in row]
                writer.writerow(row)

            offset += limit


    t2 = time.time()
    print("Время выполнения: {0}".format(t2-t1))
