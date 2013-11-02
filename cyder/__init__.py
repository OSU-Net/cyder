from base.constants import *


from django.dispatch import receiver
from django.db.models.signals import post_syncdb
from south.signals import post_migrate


# South doesn't automatically load custom SQL like Django does.

def _load_custom_sql():
    from django.db import connection

    cursor = connection.cursor()
    with open('cyder/sql/cyder.sql') as f:
        cursor.execute(f.read())


@receiver(post_migrate)
def _post_migrate(**kwargs):
    print '*** ' + kwargs['app']

    _load_custom_sql()


@receiver(post_syncdb)
def _post_syncdb(**kwargs):
    print '*** ' + kwargs['sender'].__name__

    from cyder.settings import TESTING

    if TESTING: # and kwargs['sender'] == 'cyder':
        _load_custom_sql()
