#!/usr/bin/env python
# coding=utf-8
# Stan 2018-11-06

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os
import hashlib


def get_file_md5(filename):
    if os.path.isfile(filename):
        md5 = hashlib.md5()
        md5.update(open(filename, 'rb').read())

        return md5.hexdigest()


def get_file_sha256(filename):
    if os.path.isfile(filename):
        sha256 = hashlib.sha256()
        sha256.update(open(filename, 'rb').read())

        return sha256.hexdigest()


def get_file_md5_sha256(filename):
    if os.path.isfile(filename):
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()

        content = open(filename, 'rb').read()
        md5.update(content)
        sha256.update(content)

        return md5.hexdigest(), sha256.hexdigest()

    return None, None
