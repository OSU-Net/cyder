# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_column('soa_soakeyvalue', 'obj_id', 'soa_id')

    def backwards(self, orm):
        db.rename_column('soa_soakeyvalue', 'soa_id', 'obj_id')


