import MySQLdb
from django.conf import settings

from cyder.base.utils import get_cursor


def main():
    """
    Drops the current sandbox database and creates it again by copying
    maintain.
    """

    m_db = settings.OTHER_DATABASES['maintain']['db']
    msb, msb_db = get_cursor('maintain_sb', use=False)

    try:
        msb.execute('DROP DATABASE `{}`'.format(msb_db))
    except MySQLdb.OperationalError:
        pass
    msb.execute('CREATE DATABASE `{}`'.format(msb_db))
    msb.execute('SHOW TABLES IN `{}`'.format(m_db))

    for table, in msb.fetchall():
        if table in ('bandwidth_usage', 'session', 'host_history'):
            continue
        print "Creating %s..." % table

        msb.execute('CREATE TABLE `{0}`.`{2}` LIKE `{1}`.`{2}`'.format(
            msb_db, m_db, table))
        msb.execute('INSERT INTO `{0}`.`{2}` SELECT * FROM `{1}`.`{2}`'.format(
            msb_db, m_db, table))
