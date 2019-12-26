#!/usr/bin/env python
# coding=utf-8
# Stan 2017-04-02

from __future__ import division, absolute_import, print_function

import csv

from sqlalchemy import func, select, text

from .core.types23 import *
from .core.db import getDbUri, openDbUri
from .core.status_class import Status


def dumb_python(s):
    return s.encode('utf-8') if isinstance(s, unicode) else s


def main(options):
    status = Status()

    dburi = getDbUri(options)
    if not dburi:
        msg = "Database not specified!"
        status.warning(msg)
        return -1

    # Устанавливаем соединение с БД
    engine, session = openDbUri(dburi)
    status.info(engine)

    sql = options.get('sql')
    offset = int(options.get('offset', 0))
    limit = int(options.get('limit', 200000))

    if sql:
        status.time

        output = options.get('output', 'output')
        filename = "{0}.csv".format(output)

        with open(filename, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', lineterminator='\n')

            shown = True
            while shown:
                names, rows, total, shown, s = get_rows_plain(session, sql, options=options, offset=offset, limit=limit)

                if not offset:
                    status.info("Records: {0}".format(total))
                    row = [dumb_python(s) for s in names]
                    writer.writerow(row)

                status.debug("Flushing {0} rows...".format(shown))
                for row in rows:
                    row = [dumb_python(s) for s in row]
                    writer.writerow(row)

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
