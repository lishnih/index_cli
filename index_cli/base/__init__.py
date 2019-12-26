#!/usr/bin/env python
# coding=utf-8
# Stan 2013-09-07

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import json
import hashlib
from importlib import import_module

from .models import Provider, Parser


def proceed(filename, options, recorder):
    path = options.get('path', '') or filename
    path_id = options.get('path_id', '')

    provider = options.get('provider', 'filesystem')
    PROVIDER = recorder.query(Provider).filter_by(name=provider).first()
    if not PROVIDER:
        PROVIDER = Provider(
            name = provider,
        )
        recorder.add(PROVIDER)
        recorder.commit()

    profile = options.get('profile', '')
    name = options.get('name', profile)
    options_ = {k: v for k, v in options.items() if k != 'access_token'}
    extras = json.dumps(options_, ensure_ascii=False).encode('utf8')

    check = options.get('check')
    if check:
        hash = options.get(check, '')

    else:
        m = hashlib.md5()
        m.update(extras)
        hash = m.hexdigest()

    PARSER = recorder.query(Parser).filter_by(name=name, profile=profile, hash=hash).first()
    if not PARSER:
        PARSER = Parser(
            name = name,
            profile = profile,
            hash = hash,
            options = options,
        )
        recorder.add(PARSER)
        recorder.commit()

    recorder.provider = PROVIDER
    recorder.parser = PARSER
    recorder.source = path

    modname = "{0}.{1}.{2}".format(__name__, 'proceed', provider)
    recorder.debug(modname)
    try:
        mod = import_module(modname)

    except Exception as e:
        recorder.exception("Error loading the module!", target=modname)
        raise

    try:
        filetype = mod.proceed(filename, options, recorder)

    except Exception as e:
        recorder.exception("Error proceed the module!", target=filename)
        raise

    return filetype
