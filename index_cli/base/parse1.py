#!/usr/bin/env python
# coding=utf-8
# Stan 2018-06-03

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from sqlalchemy.sql import text

from ..models.slice_dir_file import Slice


def preparing_parse(filename, options, recorder, DIR):
    return {
        '_dirs_id': DIR.id,
        'name': basename,
        'ext': ext,
        'size': size,
        'date': date,
        '_mtime': mtime,
    }


def proceed_parses(options, recorder):
    recorder.time

    SLICE = recorder.get_slice()
    row = recorder.query(Slice).filter_by(name=SLICE.name, active=0, hash=SLICE.hash).\
                  order_by(text('created desc')).first()
    previous = row.id if row else None

    recorder.info("Previous slice id: {0}".format(previous))
    recorder.info("Current slice id: {0}".format(SLICE.id))

    if previous is None:
        recorder.info("Creating parses (previous slice is None)...")
        recorder.execute("""
INSERT INTO parses(id)
  SELECT
    files.id
  FROM
    files
  JOIN slices ON dirs._slices_id = slices.id
  JOIN dirs ON files._dirs_id = dirs.id
  WHERE
    slices.id == {0}
""".format(SLICE.id))

        recorder.info("Creating rs_file_parses (previous slice is None)...")
        recorder.execute("""
INSERT INTO rs_file_parses(_files_id, _parses_id)
  SELECT
    files.id, files.id
  FROM
    files
  JOIN slices ON dirs._slices_id = slices.id
  JOIN dirs ON files._dirs_id = dirs.id
  WHERE
    slices.id == {0}
""".format(SLICE.id))

        recorder.commit()

    else:
        recorder.info("Duplication rs_file_parses for unchanged files...")
        recorder.execute("""
INSERT INTO rs_file_parses(_files_id, _parses_id)

  SELECT current_id, parse_id FROM (

    SELECT * FROM (
      SELECT
--      dirs.name as dirs_name,
--      files.name as files_name,
        max(case when slices.active == 0 then files.id else 0 end) last_id,
        max(case when slices.active == 1 then files.id else 0 end) current_id
      FROM
        files
      JOIN slices ON dirs._slices_id = slices.id
      JOIN dirs ON files._dirs_id = dirs.id
      WHERE
        slices.id == {0} or slices.id == {1}
      GROUP BY
        dirs.name, files.name, size, _mtime
    )
    WHERE last_id <> 0 and current_id <> 0

  ) JOIN (

    SELECT
      files.id as file_id,
      _parses_id as parse_id
    FROM
      files
    JOIN slices ON dirs._slices_id = slices.id
    JOIN dirs ON files._dirs_id = dirs.id
    JOIN rs_file_parses ON rs_file_parses._files_id = files.id
    WHERE
      slices.id == {0}

  )
  ON last_id == file_id
""".format(previous, SLICE.id))

        recorder.commit()

        recorder.info("Creating parses for new files...")
        recorder.execute("""
INSERT INTO parses(id)
  SELECT
    files.id
  FROM
    files
  JOIN slices ON dirs._slices_id = slices.id
  JOIN dirs ON files._dirs_id = dirs.id
  LEFT JOIN rs_file_parses ON rs_file_parses._files_id = files.id
  WHERE
    slices.id == {0} and _parses_id is NULL
""".format(SLICE.id))

        recorder.commit()

        recorder.info("Creating rs_file_parses for new files...")
        recorder.execute("""
INSERT INTO rs_file_parses(_files_id, _parses_id)
  SELECT
    files.id, files.id
  FROM
    files
  JOIN slices ON dirs._slices_id = slices.id
  JOIN dirs ON files._dirs_id = dirs.id
  LEFT JOIN rs_file_parses ON rs_file_parses._files_id = files.id
  WHERE
    slices.id == {0} and _parses_id is NULL
""".format(SLICE.id))

        recorder.commit()

    recorder.info("Preparing time: {0}".format(recorder.time))
