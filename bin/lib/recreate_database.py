#!/usr/bin/env python

import manage

import MySQLdb
from django.conf import settings

from cyder.base.utils import get_cursor


def main():
    print '****************************************************'
    print '**** THIS WILL DROP THE CURRENT CYDER DATABASE! ****'
    print '****************************************************'
    print
    while True:
        response = raw_input('Proceed [y/n]? ')
        if response.lower() == 'y':
            break
        elif response.lower() == 'n':
            return
    print

    cur, conf = get_cursor('default', use=False)
    # We can't use django.db.connection because the database might not exist.
    print 'Dropping Cyder database...'
    try:
        cur.execute('DROP DATABASE `{}`'.format(conf['db']))
    except MySQLdb.OperationalError:
        pass

    print 'Creating Cyder database...'
    cur.execute(
        'CREATE DATABASE `{}` CHARACTER SET utf8 '
        'COLLATE utf8_general_ci'.format(conf['db']))


if __name__ == '__main__':
    main()
