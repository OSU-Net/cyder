# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'System'
        db.create_table('system', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('department', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('system', ['System'])

        # Adding unique constraint on 'System', fields ['name', 'location', 'department']
        db.create_unique('system', ['name', 'location', 'department'])

        # Adding model 'SystemKeyValue'
        db.create_table('system_key_value', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('system', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['system.System'])),
        ))
        db.send_create_signal('system', ['SystemKeyValue'])

        # Adding unique constraint on 'SystemKeyValue', fields ['key', 'value', 'system']
        db.create_unique('system_key_value', ['key', 'value', 'system_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'SystemKeyValue', fields ['key', 'value', 'system']
        db.delete_unique('system_key_value', ['key', 'value', 'system_id'])

        # Removing unique constraint on 'System', fields ['name', 'location', 'department']
        db.delete_unique('system', ['name', 'location', 'department'])

        # Deleting model 'System'
        db.delete_table('system')

        # Deleting model 'SystemKeyValue'
        db.delete_table('system_key_value')


    models = {
        'system.system': {
            'Meta': {'unique_together': "(('name', 'location', 'department'),)", 'object_name': 'System', 'db_table': "'system'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'department': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
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