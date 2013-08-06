# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('soa_soakeyvalue', 'soa_kv')

    def backwards(self, orm):
        db.rename_table('soa_kv', 'soa_soakeyvalue')


