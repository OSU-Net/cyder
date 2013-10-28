# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'WorkgroupKeyValue', fields ['key', 'value', 'workgroup']
        db.delete_unique('workgroup_kv', ['key', 'value', 'workgroup_id'])

        # Deleting model 'WorkgroupKeyValue'
        db.delete_table('workgroup_kv')

        # Adding model 'WorkgroupAV'
        db.create_table('workgroup_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['workgroup.Workgroup'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['eav.Attribute'])),
        ))
        db.send_create_signal('workgroup', ['WorkgroupAV'])

        # Adding unique constraint on 'WorkgroupAV', fields ['entity', 'attribute']
        db.create_unique('workgroup_av', ['entity_id', 'attribute_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'WorkgroupAV', fields ['entity', 'attribute']
        db.delete_unique('workgroup_av', ['entity_id', 'attribute_id'])

        # Adding model 'WorkgroupKeyValue'
        db.create_table('workgroup_kv', (
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_option', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_validator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_statement', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('workgroup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['workgroup.Workgroup'])),
        ))
        db.send_create_signal('workgroup', ['WorkgroupKeyValue'])

        # Adding unique constraint on 'WorkgroupKeyValue', fields ['key', 'value', 'workgroup']
        db.create_unique('workgroup_kv', ['key', 'value', 'workgroup_id'])

        # Deleting model 'WorkgroupAV'
        db.delete_table('workgroup_av')


    models = {
        'eav.attribute': {
            'Meta': {'object_name': 'Attribute', 'db_table': "'attribute'"},
            'attribute_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value_type': ('cyder.base.eav.fields.AttributeValueTypeField', [], {'attribute_type_field': "''", 'max_length': '20'})
        },
        'workgroup.workgroup': {
            'Meta': {'object_name': 'Workgroup', 'db_table': "'workgroup'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'workgroup.workgroupav': {
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'WorkgroupAV', 'db_table': "'workgroup_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['eav.Attribute']"}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workgroup.Workgroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "''", 'max_length': '255'})
        }
    }

    complete_apps = ['workgroup']