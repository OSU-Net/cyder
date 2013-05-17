# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Workgroup'
        db.create_table('workgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal('workgroup', ['Workgroup'])

        # Adding model 'WorkgroupKeyValue'
        db.create_table('workgroup_kv', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_option', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_statement', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_validator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('workgroup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['workgroup.Workgroup'])),
        ))
        db.send_create_signal('workgroup', ['WorkgroupKeyValue'])

        # Adding unique constraint on 'WorkgroupKeyValue', fields ['key', 'value', 'workgroup']
        db.create_unique('workgroup_kv', ['key', 'value', 'workgroup_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'WorkgroupKeyValue', fields ['key', 'value', 'workgroup']
        db.delete_unique('workgroup_kv', ['key', 'value', 'workgroup_id'])

        # Deleting model 'Workgroup'
        db.delete_table('workgroup')

        # Deleting model 'WorkgroupKeyValue'
        db.delete_table('workgroup_kv')


    models = {
        'workgroup.workgroup': {
            'Meta': {'object_name': 'Workgroup', 'db_table': "'workgroup'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'workgroup.workgroupkeyvalue': {
            'Meta': {'unique_together': "(('key', 'value', 'workgroup'),)", 'object_name': 'WorkgroupKeyValue', 'db_table': "'workgroup_kv'"},
            'has_validator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_option': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_quoted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_statement': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'workgroup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workgroup.Workgroup']"})
        }
    }

    complete_apps = ['workgroup']