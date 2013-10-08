# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'VrfKeyValue'
        db.delete_table('vrf_kv')

        # Adding model 'VrfAV'
        db.create_table('vrf_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='attribute', max_length=255)),
            ('vrf', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vrf.Vrf'])),
            ('attribute', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eav.Attribute'])),
        ))
        db.send_create_signal('vrf', ['VrfAV'])

        # Adding unique constraint on 'VrfAV', fields ['vrf', 'attribute']
        db.create_unique('vrf_av', ['vrf_id', 'attribute_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'VrfAV', fields ['vrf', 'attribute']
        db.delete_unique('vrf_av', ['vrf_id', 'attribute_id'])

        # Adding model 'VrfKeyValue'
        db.create_table('vrf_kv', (
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('vrf', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vrf.Vrf'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('vrf', ['VrfKeyValue'])

        # Deleting model 'VrfAV'
        db.delete_table('vrf_av')


    models = {
        'eav.attribute': {
            'Meta': {'object_name': 'Attribute', 'db_table': "'attribute'"},
            'attribute_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value_type': ('cyder.base.eav.fields.AttributeValueTypeField', [], {'attribute_type_field': "'attribute_type'", 'max_length': '20'})
        },
        'vrf.vrf': {
            'Meta': {'object_name': 'Vrf', 'db_table': "'vrf'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'vrf.vrfav': {
            'Meta': {'unique_together': "(('vrf', 'attribute'),)", 'object_name': 'VrfAV', 'db_table': "'vrf_av'"},
            'attribute': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eav.Attribute']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "'attribute'", 'max_length': '255'}),
            'vrf': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vrf.Vrf']"})
        }
    }

    complete_apps = ['vrf']