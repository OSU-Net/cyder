# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'VlanKeyValue', fields ['key', 'value']
        db.delete_unique('vlan_kv', ['key', 'value'])

        # Deleting model 'VlanKeyValue'
        db.delete_table('vlan_kv')

        # Adding model 'VlanAV'
        db.create_table('vlan_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='attribute', max_length=255)),
            ('vlan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vlan.Vlan'])),
            ('attribute', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eav.Attribute'])),
        ))
        db.send_create_signal('vlan', ['VlanAV'])

        # Adding unique constraint on 'VlanAV', fields ['vlan', 'attribute']
        db.create_unique('vlan_av', ['vlan_id', 'attribute_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'VlanAV', fields ['vlan', 'attribute']
        db.delete_unique('vlan_av', ['vlan_id', 'attribute_id'])

        # Adding model 'VlanKeyValue'
        db.create_table('vlan_kv', (
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('vlan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vlan.Vlan'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('vlan', ['VlanKeyValue'])

        # Adding unique constraint on 'VlanKeyValue', fields ['key', 'value']
        db.create_unique('vlan_kv', ['key', 'value'])

        # Deleting model 'VlanAV'
        db.delete_table('vlan_av')


    models = {
        'eav.attribute': {
            'Meta': {'object_name': 'Attribute', 'db_table': "'attribute'"},
            'attribute_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value_type': ('cyder.base.eav.fields.AttributeValueTypeField', [], {'attribute_type_field': "'attribute_type'", 'max_length': '20'})
        },
        'vlan.vlan': {
            'Meta': {'unique_together': "(('name', 'number'),)", 'object_name': 'Vlan', 'db_table': "'vlan'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'vlan.vlanav': {
            'Meta': {'unique_together': "(('vlan', 'attribute'),)", 'object_name': 'VlanAV', 'db_table': "'vlan_av'"},
            'attribute': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eav.Attribute']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "'attribute'", 'max_length': '255'}),
            'vlan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vlan.Vlan']"})
        }
    }

    complete_apps = ['vlan']