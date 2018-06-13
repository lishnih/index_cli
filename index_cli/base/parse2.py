#!/usr/bin/env python
# coding=utf-8
# Stan 2018-06-05

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os
from Queue import Queue
from threading import Thread
import hashlib

from sqlalchemy.sql import text

from ..models.slice_dir_file import Parse


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


def do_stuff(q, options, recorder):
    while True:
        row = q.get()
        do_stuff_row(row, options, recorder)
        q.task_done()


def do_stuff_row(row, options, recorder):
    filename = os.path.join(row.dir_name, row.file_name)
    if not os.path.isfile(filename):
        recorder.warning("File not found:", filename)
        recorder.query(Parse).filter_by(id=row.parse_id).update({'status': -1})

    else:
        try:
            md5 = get_md5_file(filename) if options.get('md5') else ''
            sha256 = get_sha256_file(filename) if options.get('sha256') else ''
        except MemoryError:
            md5, sha256 = '-1', '-1'

        recorder.debug(filename)
        try:
            if recorder.opening_func:
                recorder.opening_func(options, recorder)
            er = recorder.func(filename, row.parse_id, options, recorder)
            if recorder.closing_func:
                recorder.closing_func(options, recorder)
        except Exception as e:
            recorder.exception(repr(e), parse_id=row.parse_id)
            er = -2

        recorder.query(Parse).filter_by(id=row.parse_id).update({'md5': md5, 'sha256': sha256, 'status': er})

    recorder.commit()


def parse_files(options, recorder):
    recorder.time

    recorder.info("Selection of unparsed files and parsing...")

    SLICE = recorder.get_slice()
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
    row = recorder.execute(sql.format(SLICE.id))
    recorder.info("Files total: {0}".format(row.scalar()))

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
    row = recorder.execute(sql.format(SLICE.id))
    recorder.info("Files parsed: {0}".format(row.scalar()))

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
    row = recorder.execute(sql.format(SLICE.id))
    recorder.info("Files parsed with errors: {0}".format(row.scalar()))

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
    row = recorder.execute(sql.format(SLICE.id))
    recorder.info("Files unparsed: {0}".format(row.scalar()))

    if not recorder.func:
        recorder.info("Primary handler omitted, finish parsing")
        recorder.info("Processing time: {0}".format(recorder.time))
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
        recorder.info("Parsing with {0} threads...".format(threads))

        for i in range(threads):
            worker = Thread(target=do_stuff, args=(q, options, recorder))
            worker.setDaemon(True)
            worker.start()

        empty = False
        while not empty:
            rows = recorder.execute(sql.format(SLICE.id, limit))
            rows = [i for i in rows]

            empty = True
            for bundle in chunks(rows, threads, limit):
                for row in bundle:
                    empty = False
                    q.put(row)

                q.join()

            if not empty:
                recorder.info("Processed {0} files".format(len(bundle)))

    else:
        recorder.info("Parsing without threads...")

        empty = False
        while not empty:
            rows = recorder.execute(sql.format(SLICE.id, limit))
            rows = [i for i in rows]

            empty = True
            for row in rows:
                empty = False
                do_stuff_row(row, options, recorder)

            if not empty:
                recorder.info("Processed {0} files".format(len(rows)))

    recorder.info("Processing time: {0}".format(recorder.time))
