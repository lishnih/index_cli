#!/usr/bin/env python
# coding=utf-8
# Stan 2018-06-05

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os
from Queue import Queue
from threading import Thread
import hashlib
import traceback

from sqlalchemy.sql import text

from ..models.slice_dir_file import Parse, Error


q = Queue(maxsize=0)


def get_sha256_file(filename):
    sha256 = hashlib.sha256()
    sha256.update(open(filename, 'rb').read())

    return sha256.hexdigest()


def get_md5_file(filename):
    md5 = hashlib.md5()
    md5.update(open(filename, 'rb').read())

    return md5.hexdigest()


def chunks(lst, chunk_size, lenght=None):
    if lenght is None:
        lenght = len(lst)
    return [lst[i:i+chunk_size] for i in range(0, lenght, chunk_size)]


def do_stuff(q, options, status, session, func):
    while True:
        row = q.get()
        do_stuff_row(row, options, status, session, func)
        q.task_done()


def do_stuff_row(row, options, status, session, func):
    filename = os.path.join(row.dir_name, row.file_name)
    if not os.path.isfile(filename):
        status.warning("File not found:", filename)
        session.query(Parse).filter_by(id=row.parse_id).update({'status': -1})

    else:
        try:
            md5 = get_md5_file(filename) if options.get('md5') else ''
            sha256 = get_sha256_file(filename) if options.get('sha256') else ''
        except MemoryError:
            md5, sha256 = '-1', '-1'

        status.debug("Proceed file:", filename)
        try:
            er = func(filename, row.parse_id, options, status, session)
        except Exception as e:
            session.add(Error(repr(e), 'EXCEPTION', row.file_id, traceback.format_exc()))
            er = -2

        session.query(Parse).filter_by(id=row.parse_id).update({'md5': md5, 'sha256': sha256, 'status': er})

    session.commit()


def parse_files(options, status, session, SLICE, func=None):
    status.time

    status.debug("Выборка необработанных файлов и их обработка")

    sql = """
SELECT
  count(*)
FROM
  slices
JOIN dirs ON dirs._slices_id = slices.id
JOIN files ON files._dirs_id = dirs.id
JOIN rs_file_parses ON rs_file_parses._files_id = files.id
JOIN parses ON rs_file_parses._parses_id = parses.id
WHERE
  slices.id == {0}
""".format(SLICE.id)
    row = session.execute(sql.format(SLICE.id))
    status.info("Всего файлов: {0}".format(row.scalar()))

    sql = """
SELECT
  count(*)
FROM
  slices
JOIN dirs ON dirs._slices_id = slices.id
JOIN files ON files._dirs_id = dirs.id
JOIN rs_file_parses ON rs_file_parses._files_id = files.id
JOIN parses ON rs_file_parses._parses_id = parses.id
WHERE
  slices.id == {0} and status > 0
""".format(SLICE.id)
    row = session.execute(sql.format(SLICE.id))
    status.info("Обработанных файлов: {0}".format(row.scalar()))

    sql = """
SELECT
  count(*)
FROM
  slices
JOIN dirs ON dirs._slices_id = slices.id
JOIN files ON files._dirs_id = dirs.id
JOIN rs_file_parses ON rs_file_parses._files_id = files.id
JOIN parses ON rs_file_parses._parses_id = parses.id
WHERE
  slices.id == {0} and status < 0
""".format(SLICE.id)
    row = session.execute(sql.format(SLICE.id))
    status.info("Обработанных файлов с ошибками: {0}".format(row.scalar()))

    sql = """
SELECT
  count(*)
FROM
  slices
JOIN dirs ON dirs._slices_id = slices.id
JOIN files ON files._dirs_id = dirs.id
JOIN rs_file_parses ON rs_file_parses._files_id = files.id
JOIN parses ON rs_file_parses._parses_id = parses.id
WHERE
  slices.id == {0} and status == 0
""".format(SLICE.id)
    row = session.execute(sql.format(SLICE.id))
    status.info("Необработанных файлов: {0}".format(row.scalar()))

    if not func:
        status.info("Основной обработчик не указан, завершаем обработку")
        status.info("Processing time: {0}".format(status.time))
        return

    sql = """
SELECT
  dirs.name as dir_name,
  files.id as file_id,
  files.name as file_name,
  parses.id as parse_id,
  parses.status
FROM
  slices
JOIN dirs ON dirs._slices_id = slices.id
JOIN files ON files._dirs_id = dirs.id
JOIN rs_file_parses ON rs_file_parses._files_id = files.id
JOIN parses ON rs_file_parses._parses_id = parses.id
WHERE
  slices.id == {0} and status == 0
LIMIT 0, {1}
"""

    limit = int(options.get('limit', 1000))
    threads = int(options.get('threads', 0))

    if threads:
        status.debug("Threads: {0}".format(threads))

        for i in range(threads):
            worker = Thread(target=do_stuff, args=(q, options, status, session, func))
            worker.setDaemon(True)
            worker.start()

        empty = False
        while not empty:
            rows = session.execute(sql.format(SLICE.id, limit))
            rows = [i for i in rows]

            empty = True
            for bundle in chunks(rows, threads, limit):
                for row in bundle:
                    empty = False
                    q.put(row)

                q.join()

            if not empty:
                status.debug("Processed {0} files".format(len(bundle)))

    else:
        status.debug("No threads")

        empty = False
        while not empty:
            rows = session.execute(sql.format(SLICE.id, limit))
            rows = [i for i in rows]

            empty = True
            for row in rows:
                empty = False
                do_stuff_row(row, options, status, session, func)

            if not empty:
                status.info("Processed {0} files".format(len(rows)))

    status.info("Processing time: {0}".format(status.time))
