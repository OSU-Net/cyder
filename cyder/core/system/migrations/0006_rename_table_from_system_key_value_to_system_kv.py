# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('system_key_value', 'system_kv')

    def backwards(self, orm):
        db.rename_table('system_kv', 'system_key_value')
