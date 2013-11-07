from django.dispatch import receiver
from django.db.models.signals import post_syncdb
from south.signals import post_migrate


# South doesn't automatically load custom SQL like Django does, and regardless,
# the filename isn't what Django would expect.
def _load_custom_sql():
    from django.db import connection

    cursor = connection.cursor()
    with open('cyder/sql/cyder.sql') as f:
        cursor.execute(f.read())


def _load_fixtures():
    from django.core.management import call_command
    from os import listdir

    for filename in sorted(listdir('cyder/initial_data')):
        call_command('loaddata', 'cyder/initial_data/' + filename)


@receiver(post_syncdb)
def _post_syncdb(**kwargs):
    from cyder.settings import TESTING

    if TESTING and kwargs['sender'].__name__ == 'cyder.models':
        _load_custom_sql()
        _load_fixtures()


@receiver(post_migrate)
def _post_migrate(**kwargs):
    _load_custom_sql()
    _load_fixtures()
