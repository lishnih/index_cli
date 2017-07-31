#!/usr/bin/env python
# coding=utf-8
# Stan 2013-09-15

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import sys, os, argparse, logging
import ConfigParser as configparser

from index.main import main
from index.lib.argparse_funcs import readable_file_or_dir_list, readable_file


def run(files, profile, **options):
    if isinstance(files, str):
        pass

    logging.debug(["[0]:", files])
    logging.debug(["[1]:", profile])
    logging.debug(["[2]:", options])
    sys.exit(main(files, profile, options))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description="Indexing files and directories.")
    parser.add_argument('files', action=readable_file_or_dir_list, nargs='*',
                        help="files and directories to proceed")
    parser.add_argument('-p', '--profile',
                        help='specify the profile')
    parser.add_argument('-v', '--var',
                        help='specify the auxiliary argument')
    parser.add_argument('-n', '--dbname',
                        help='specify the name of the DB')
    parser.add_argument('-m', '--dbmodels',
                        help='specify the profile of the DB')
    parser.add_argument('-c', '--config', action=readable_file,
                        help='specify the config file')
    parser.add_argument('-s', '--section', default='default',
                        help='specify the section name in the config file')

    if sys.version_info >= (3,):
        argv = sys.argv
    else:
        fse = sys.getfilesystemencoding()
        argv = [i.decode(fse) for i in sys.argv]

    args = parser.parse_args(argv[1:])

    if not args.config and args.files and len(args.files) == 1:
        x, ext = os.path.splitext(args.files[0])
        if ext == '.cfg':
            args.config = args.files[0]
            args.files = []

    options = {}
    if args.config:
        logging.debug(["config file:", args.config])
        c = configparser.ConfigParser()
        c.read(args.config)

        for i in ('files', 'profile', 'var', 'dbname', 'dbmodels'):
            if args.__contains__(i) and args.__getattribute__(i):
                c.set(args.section, i, args.__getattribute__(i))

        options = dict(c.items(args.section))

    options.setdefault('files')
    options.setdefault('profile')
    run(**options)
