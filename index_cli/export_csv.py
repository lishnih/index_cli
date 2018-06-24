#!/usr/bin/env python
# coding=utf-8
# Stan 2017-04-02

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import csv
import codecs
import cStringIO
from importlib import import_module

from sqlalchemy import func
from sqlalchemy.sql import select, text

from .core.backwardcompat import *
from .core.db import getDbUri, openDbUri
from .core.status_class import Status


def main(options):
    status = Status()

    dburi = getDbUri(options)
    if not dburi:
        msg = "Database not specified!"
        status.warning(msg)
        return -1

    # Устанавливаем соединение с БД
    engine, session = openDbUri(dburi)

    sql = options.get('sql')
    offset = int(options.get('offset', 0))
    limit = int(options.get('limit', 200000))

    if sql:
        status.time

        output = options.get('output', 'output')
        filename = "{0}.csv".format(output)
        with open(filename, 'wb') as csvfile:
            writer = UnicodeWriter(csvfile, delimiter=b';')

            while 1:
                names, rows, total, shown, s = get_rows_plain(session, sql, options=options, offset=offset, limit=limit)

                if not offset:
                    status.info("Records: {0}".format(total))
                    writer.writerow(names)

                if not shown:
                    break

                status.debug("Flushing {0} rows...".format(shown))
                writer.writerows(rows)

                offset += limit

        status.info("Proceed time: {0}".format(status.time))
        status.debug(s)


def get_rows_plain(session, sql, options={}, offset=0, limit=None):
    s = select(['*']).select_from(text("({0})".format(sql)))
    s_count = select([func.count()]).select_from(text("({0})".format(sql)))
    total = session.execute(s_count, options).scalar()

    if offset:
        s = s.offset(offset)
    if limit:
        s = s.limit(limit)

    res = session.execute(s, options)
    names = res.keys()

    rows = [[j for j in i] for i in res.fetchall()]

    shown = len(rows)

    return names, rows, total, shown, s


class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") if isinstance(s, string_types) else s for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
