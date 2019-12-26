#!/usr/bin/env python
# coding=utf-8
# Stan 2013-09-07

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os

from sqlalchemy import select, func, distinct, text, and_, not_

from . import regular_state
from .filesystem_dir import prepare_dir
from .filesystem_file import prepare_file
from ..models import Dir, File, Node
from ...core.file_hash import *


def proceed(filename, options, recorder):
    filetype = None

    recorder.time

    # Директория
    if os.path.isdir(filename):
        recorder.info("Processing directory", filename)

        # Файлы участвующие в сканировании
        scoped_dirs_expr = (
            Dir.provider == recorder.provider,
            Dir.name.like("{0}%".format(filename)),
        )
        scoped_files_expr = (
            File._dir_id.in_(select([Dir.id]).where(and_(*scoped_dirs_expr))),
        )

        # Определяем, сколько файлов было отсканировано ранее
#       total = recorder.execute(select([func.count(Dir.id)]).where(and_(*scoped_dirs_expr))).scalar()
        total = recorder.query(func.count(Dir.id)).filter(*scoped_dirs_expr).scalar()
        recorder.info("Dirs have scanned before: {0}".format(total))
        total = recorder.query(func.count(File.id)).filter(*scoped_files_expr).scalar()
        recorder.info("Files have scanned before: {0}".format(total))

        # Перед сканированием помечаем все файлы как удалённые
        recorder.query(Dir).filter(*scoped_dirs_expr).update({"state": 2}, synchronize_session='fetch')
        recorder.commit()
        recorder.query(File).filter(*scoped_files_expr).update({"state": 2}, synchronize_session='fetch')
        recorder.commit()

        # Сканируем файлы
        total = scanned = 0
        for root, dirs, files in os.walk(filename):
            dir_dict = prepare_dir(root, options, recorder)
            DIR = recorder.get_or_create(Dir, func=regular_state, **dir_dict)

            for i in files:
                scanned += 1
                filename = os.path.join(root, i)
                file_dict = prepare_file(filename, options, recorder, DIR)
                if file_dict:
                    FILE = recorder.get_or_create(File, func=regular_state, **file_dict)

            if scanned >= 10000:
                recorder.debug("Scanned {0} files...".format(scanned))
                recorder.commit()
                total += scanned
                scanned = 0

        total += scanned
        recorder.debug("Total {0} files scanned".format(total))
        recorder.commit()
        filetype = 2

    # Файл
    elif os.path.isfile(filename):
        recorder.info("Processing file", filename)

        # Dir
        dirname = os.path.dirname(filename)
        dir_dict = prepare_dir(dirname, options, recorder)
        DIR = recorder.get_or_create(Dir, func=regular_state, **dir_dict)

        # Файлы участвующие в сканировании
        scoped_dirs_expr = (
            Dir.provider == recorder.provider,
            Dir.name.like("{0}%".format(dirname)),
        )
        scoped_files_expr = (
            File._dir_id.in_(recorder.query(Dir.id).filter(*scoped_dirs_expr)),
        )

        # Перед сканированием помечаем все версии файла, как удалённые
        recorder.query(File).filter(*scoped_files_expr).update({"state": 2}, synchronize_session='fetch')
        recorder.commit()

        # File
        file_dict = prepare_file(filename, options, recorder, DIR)
        if file_dict:
            FILE = recorder.get_or_create(File, func=regular_state, **file_dict)

        recorder.commit()
        filetype = 1

    else:
        recorder.warning("Directory/file not found!", target=filename)
        return None

    recorder.info("Scan time: {0} (dirs: {1}, files: {2} scanned)".\
        format(recorder.time, recorder.ndirs, recorder.nfiles))

    # Для filesystem мы не имеем информации о контрольных суммах файлов по умоляанию
    # Соответственно, node создаём для каждого расположения файла с заданными параметрами:
    # имя директории, имя файла, размер, время модификации

    # Создаём nodes
    node_unique_constraint = Node.ext, Node.size, Node.modified, Node.hash, File.md5, File.sha256
    if 0:
        file_unique_constraint = File.ext, File.size, File.modified, File.hash, File.md5, File.sha256
        sel = recorder.query(File).with_entities(*file_unique_constraint).distinct().filter(*scoped_files_expr)
        inserter = Node.__table__.insert().prefix_with("OR IGNORE").from_select(file_unique_constraint, sel)

    else:
        # Здесь используем уловку:
        # Подменяаем Node.hash значением File.id - так мы будем уверены, что все файлв будут обработаны
        file_unique_constraint = File.ext, File.size, File.modified, File.id, File.md5, File.sha256
        sel = recorder.query(File).with_entities(*file_unique_constraint).distinct().filter(*scoped_files_expr)
        inserter = Node.__table__.insert().prefix_with("OR IGNORE").from_select(node_unique_constraint, sel)

    recorder.debug(str(inserter), once='insert_nodes')
    recorder.bind.execute(inserter)
#   recorder.bind.execute("""INSERT OR IGNORE INTO nodes(ext, size, modified, hash, md5, sha256)
# SELECT DISTINCT ext, size, modified, hash, md5, sha256
# FROM files""")

    # Связываем files и nodes
    constraint = [i1==i2 for i1, i2 in zip(file_unique_constraint, node_unique_constraint)]
    sel = select([Node.id]).where(and_(*constraint))
    updater = File.__table__.update().values(
        _node_id = sel
    ).where(and_(File._node_id.is_(None), *scoped_files_expr))
    recorder.bind.execute(updater)
#   recorder.bind.execute("""UPDATE files
# SET _node_id = (SELECT id FROM nodes WHERE files.ext = nodes.ext AND files.size = nodes.size AND
# files.hash = nodes.hash AND files.md5 = nodes.md5 AND files.sha256 = nodes.sha256)""")

    recorder.info("Nodes time: {0}".format(recorder.time))

    return filetype
