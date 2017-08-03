#!/usr/bin/env python
# coding=utf-8
# Stan 2012-03-12, 2017-03-09

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import sys, os, importlib

from .core.backwardcompat import *
from .core.status1 import status1


def main(files, profile='default', options={}, status=status1):
    status.reset()
    options['profile'] = profile


    if not files:
        status.warning("Files not specified!")
        return


    # Загружаем обработчик (handler)
    handler = __package__ + '.handlers.' + profile
    try:
        handler_module = importlib.import_module(handler)

    except Exception as e:
        status.exception("Error in the handler", profile, e)
        return


    # Обработчик имеет точку входа 'proceed'
    if not hasattr(handler_module, 'proceed'):
        status.error("Function 'proceed' is missing in the handler", profile)
        return


    if hasattr(handler_module, 'opening'):
        try:
            runtime = handler_module.opening(__package__, options, status)

        except Exception as e:
            status.exception("Error during opening", profile, e)
            return

    else:
        runtime = {}
        status.debug("Function 'opening' is missing in the handler", profile)


    # Обработка
    if not isinstance(files, collections_types):
        files = [files]

    for i in files:
        try:
            handler_module.proceed(i, options, status, **runtime)
        except Exception as e:
            status.exception("Error during handle the file", profile, e)


    if hasattr(handler_module, 'closing'):
        handler_module.closing(options, status, **runtime)
    else:
        status.debug("Function 'closing' is missing in the handler", profile)
