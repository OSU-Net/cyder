# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'System.location'
        db.alter_column('system', 'location', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'System.department'
        db.alter_column('system', 'department', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

    def backwards(self, orm):

        # Changing field 'System.location'
        db.alter_column('system', 'location', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'System.department'
        db.alter_column('system', 'department', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

    models = {
        'system.system': {
            'Meta': {'unique_together': "(('name', 'location', 'department'),)", 'object_name': 'System', 'db_table': "'system'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'department': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'system.systemkeyvalue': {
            'Meta': {'unique_together': "(('key', 'value', 'system'),)", 'object_name': 'SystemKeyValue', 'db_table': "'system_key_value'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_quoted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'system': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['system.System']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['system']