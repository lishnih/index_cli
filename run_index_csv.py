#!/usr/bin/env python
# coding=utf-8
# Stan 2013-09-15

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import sys, argparse, logging
import ConfigParser as configparser

from index.import_csv import main
from index.lib.argparse_funcs import readable_file_or_dir_list, readable_file


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Indexing files and directories.")
    parser.add_argument('-d', '--dbname',
                        help='specify the dbname')
    parser.add_argument('-c', '--config', action=readable_file,
                        help='specify the config file')

    if sys.version_info >= (3,):
        argv = sys.argv
    else:
        fse = sys.getfilesystemencoding()
        argv = [i.decode(fse) for i in sys.argv]

    args = parser.parse_args(argv[1:])

    options = {}
    if args.config:
        config = configparser.ConfigParser()
        config.read(args.config)
        options = dict(config.items('general'))

    if args.dbname:
        options['dbname'] = args.dbname

    sys.exit(main(options))
