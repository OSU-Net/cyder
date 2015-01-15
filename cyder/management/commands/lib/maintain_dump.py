from subprocess import PIPE, Popen
from sys import stderr
from tempfile import NamedTemporaryFile

import MySQLdb
from django.conf import settings

from cyder.base.utils import get_cursor


def main():
    """
    Drops the current sandbox database and creates it again by copying
    maintain.
    """

    m, m_conf = get_cursor('maintain')
    msb, msb_conf = get_cursor('maintain_sb', use=False)

    try:
        msb.execute('DROP DATABASE `{}`'.format(msb_conf['db']))
    except MySQLdb.OperationalError:
        pass
    msb.execute('CREATE DATABASE `{}`'.format(msb_conf['db']))

    print 'Copying data from {} to {}...'.format(m_conf['db'], msb_conf['db'])

    if (m_conf['host'] == msb_conf['host'] and
            m_conf['user'] == msb_conf['user']):
        m.execute('SHOW TABLES IN `{}`'.format(m_conf['db']))
        for table, in m.fetchall():
            if table in ('bandwidth_usage', 'session', 'host_history'):
                continue

            msb.execute('CREATE TABLE `{0}`.`{2}` LIKE `{1}`.`{2}`'.format(
                msb_conf['db'], m_conf['db'], table))
            msb.execute(
                'INSERT INTO `{0}`.`{2}` SELECT * FROM `{1}`.`{2}`'.format(
                    msb_conf['db'], m_conf['db'], table))
    else:
        with NamedTemporaryFile() as dumper_conf, \
                NamedTemporaryFile() as loader_conf:
            args = [settings.MYSQLDUMP]
            if 'passwd' in m_conf:
                dumper_conf.write('[mysqldump]\n')
                dumper_conf.write('password={}\n'.format(m_conf['passwd']))
                dumper_conf.flush()
                args.append('--defaults-extra-file=' + dumper_conf.name)
            args.extend([
                '--ignore-table={}.bandwidth_usage'.format(m_conf['db']),
                '--ignore-table={}.host_history'.format(m_conf['db']),
                '--ignore-table={}.session'.format(m_conf['db']),
                '--single-transaction',
                '-h', m_conf['host'],
                '-u', m_conf['user'],
                m_conf['db']
            ])
            dumper = Popen(args, stdout=PIPE)

            args = [settings.MYSQL]
            if 'passwd' in msb_conf:
                loader_conf.write('[mysql]\n')
                loader_conf.write('password={}\n'.format(msb_conf['passwd']))
                loader_conf.flush()
                args.append('--defaults-extra-file=' + loader_conf.name)
            args.extend([
                '-h', msb_conf['host'],
                '-u', msb_conf['user'],
                msb_conf['db']
            ])
            loader = Popen(args, stdin=dumper.stdout)

            if loader.wait() != 0:
                stderr.write("Error: Can't load data into {}\n".format(
                    msb_conf['db']))
                exit(1)
            if dumper.wait() != 0:
                stderr.write("Error: Can't dump {}\n".format(m_conf['db']))
                exit(1)
