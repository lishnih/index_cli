#!/usr/bin/env python
# coding=utf-8
# Stan 2018-06-05

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os
from itertools import islice
from threading import Thread

from sqlalchemy import select, and_

from .. import *
from ..core.data_funcs import filter_match
from .models import Dir, File, Node, Parser, Parse

# from .proceed_dropbox import download_file_dropbox
# from .proceed_google import download_file_google
# from .proceed.yandex import yandex_download


if PY2:
    from Queue import Queue, Empty
else:
    from queue import Queue, Empty


RUNTIME_ERROR = -100

q = Queue(maxsize=0)


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def do_stuff(q, options, recorder, parse):
    while True:
        filename = q.get()
        do_stuff_row(filename, options, recorder, parse)
        q.task_done()


def do_stuff_row(filename, options, recorder, parse):
    try:
        er = recorder.func(filename, options, recorder, parse.id)
        parse.status = er

    except Exception as e:
        parse.status = RUNTIME_ERROR
        recorder.exception("Error file parsing",
            target=parse.file.name, parse_id=parse.id, once="do_stuff_1")

    recorder.commit()
#   delete_file(filename)


def parse_files(filename, filetype, options, recorder):
    provider = options.get('provider', 'filesystem')
#     if provider == 'yandex':
#         download_file = yandex_download
#     else:     # filesystem
    download_file = None

    recorder.time

    if filetype == 1:
        dirname = os.path.dirname(filename)
        basename = os.path.basename(filename)

        # Node должен быть создан
        FILE, NODE = recorder.query(File, Node).filter_by(name=basename, state=1).\
            join(File.node).join(File.dir).filter_by(name=dirname).first()

        parse_file(FILE, NODE, options, recorder, download_file)

    else:
        dirs_filter = options.get('dirs_filter')
        exclude_dirs_filter = options.get('exclude_dirs_filter')
        dir_depth = options.get('dir_depth')
        files_filter = options.get('files_filter')

        limit = int(options.get('limit', 1000))
        threads = int(options.get('threads', 0))

        if threads:
            recorder.info("Parsing with {0} threads...".format(threads))

            for i in range(threads):
                worker = Thread(target=do_stuff, args=(q, options, recorder, parse))
                worker.setDaemon(True)
                worker.start()

            empty = False
            while not empty:
                rows = recorder.execute(sql.format(SLICE.id, limit))
                rows = [i for i in rows]

                empty = True
                for bundle in chunk(rows, threads):
                    for row in bundle:
                        empty = False
                        q.put(row)

                    q.join()

                if not empty:
                    recorder.debug("Processed {0} files".format(len(bundle)))

        else:
            recorder.info("Parsing without threads...")

            rows = True
            offset = 0
            while rows:
                scoped_dirs_expr = (
                    Dir.provider == recorder.provider,
                    Dir.name.like("{0}%".format(filename)),
                )
                scoped_files_expr = (
                    File._dir_id.in_(select([Dir.id]).where(and_(*scoped_dirs_expr))),
                )

                rows = recorder.query(File, Node).filter(
                    File.state==1,
                    *scoped_files_expr
                ).join(File.node, isouter=True).slice(offset, offset+limit).all()
                offset += limit

                for FILE, NODE in rows:
                    if FILE.type == 1 and filter_match(FILE.name, files_filter):
                        parse_file(FILE, NODE, options, recorder, download_file)

                if rows:
                    recorder.debug("Processed {0} files".format(len(rows)))

    recorder.info("Processing time: {0}".format(recorder.time))


def parse_file(FILE, NODE, options, recorder, download_file):
    provider = options.get('provider', 'filesystem')
    if provider == 'filesystem':
        parse = recorder.query(Parse).filter_by(_parser_id=recorder.parser.id, _file_id=FILE.id).first()
        _link = dict(file=FILE, node=NODE)

    else:
        if NODE is None:
            recorder.warning("Node missed: '{0}'".format(FILE.name))

            return

        parse = recorder.query(Parse).filter_by(_parser_id=recorder.parser.id, _node_id=NODE.id).first()
        _link = dict(file=FILE, node=NODE)

    if parse and parse.status > RUNTIME_ERROR:
        return

    if not parse:
        parse = Parse(parser=recorder.parser, **_link)
        recorder.add(parse)
        recorder.commit()

    filename = "{0}/{1}".format(FILE.dir.name, FILE.name)
    recorder.debug(filename, timer=('filename', 5))

    if download_file:
        tmp_name = "tmp/{0}".format(FILE.name)
        try:
            download_file(filename, tmp_name, recorder)

        except Exception as e:
            recorder.exception("Error file downloading",
                target=FILE.name, parse_id=parse.id, once="download_file_1")

            return

    else:
        tmp_name = filename

    do_stuff_row(tmp_name, options, recorder, parse)
