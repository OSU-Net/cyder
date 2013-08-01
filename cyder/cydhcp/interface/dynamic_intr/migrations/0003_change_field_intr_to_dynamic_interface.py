# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_column('dynamic_interface_kv', 'intr_id',
                         'dynamic_interface_id')

    def backwards(self, orm):
        db.rename_column('dynamic_interface_kv', 'dynamic_interface_id',
                         'intr_id')
