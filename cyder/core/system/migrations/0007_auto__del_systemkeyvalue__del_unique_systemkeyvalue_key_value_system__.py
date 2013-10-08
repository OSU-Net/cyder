# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'SystemKeyValue', fields ['key', 'value', 'system']
        db.delete_unique('system_kv', ['key', 'value', 'system_id'])

        # Deleting model 'SystemKeyValue'
        db.delete_table('system_kv')

        # Adding model 'SystemAV'
        db.create_table('system_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='attribute', max_length=255)),
            ('system', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['system.System'])),
            ('attribute', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eav.Attribute'])),
        ))
        db.send_create_signal('system', ['SystemAV'])

        # Adding unique constraint on 'SystemAV', fields ['system', 'attribute']
        db.create_unique('system_av', ['system_id', 'attribute_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'SystemAV', fields ['system', 'attribute']
        db.delete_unique('system_av', ['system_id', 'attribute_id'])

        # Adding model 'SystemKeyValue'
        db.create_table('system_kv', (
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('system', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['system.System'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('system', ['SystemKeyValue'])

        # Adding unique constraint on 'SystemKeyValue', fields ['key', 'value', 'system']
        db.create_unique('system_kv', ['key', 'value', 'system_id'])

        # Deleting model 'SystemAV'
        db.delete_table('system_av')


    models = {
        'eav.attribute': {
            'Meta': {'object_name': 'Attribute', 'db_table': "'attribute'"},
            'attribute_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value_type': ('cyder.base.eav.fields.AttributeValueTypeField', [], {'attribute_type_field': "'attribute_type'", 'max_length': '20'})
        },
        'system.system': {
            'Meta': {'object_name': 'System', 'db_table': "'system'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'system.systemav': {
            'Meta': {'unique_together': "(('system', 'attribute'),)", 'object_name': 'SystemAV', 'db_table': "'system_av'"},
            'attribute': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eav.Attribute']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'system': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['system.System']"}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "'attribute'", 'max_length': '255'})
        }
    }

    complete_apps = ['system']