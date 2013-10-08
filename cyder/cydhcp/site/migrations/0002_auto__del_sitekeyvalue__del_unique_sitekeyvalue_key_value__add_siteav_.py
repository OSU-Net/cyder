# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'SiteKeyValue', fields ['key', 'value']
        db.delete_unique('site_kv', ['key', 'value'])

        # Deleting model 'SiteKeyValue'
        db.delete_table('site_kv')

        # Adding model 'SiteAV'
        db.create_table('site_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='attribute', max_length=255)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['site.Site'])),
            ('attribute', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eav.Attribute'])),
        ))
        db.send_create_signal('site', ['SiteAV'])

        # Adding unique constraint on 'SiteAV', fields ['site', 'attribute']
        db.create_unique('site_av', ['site_id', 'attribute_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'SiteAV', fields ['site', 'attribute']
        db.delete_unique('site_av', ['site_id', 'attribute_id'])

        # Adding model 'SiteKeyValue'
        db.create_table('site_kv', (
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['site.Site'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('site', ['SiteKeyValue'])

        # Adding unique constraint on 'SiteKeyValue', fields ['key', 'value']
        db.create_unique('site_kv', ['key', 'value'])

        # Deleting model 'SiteAV'
        db.delete_table('site_av')


    models = {
        'eav.attribute': {
            'Meta': {'object_name': 'Attribute', 'db_table': "'attribute'"},
            'attribute_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value_type': ('cyder.base.eav.fields.AttributeValueTypeField', [], {'attribute_type_field': "'attribute_type'", 'max_length': '20'})
        },
        'site.site': {
            'Meta': {'unique_together': "(('name', 'parent'),)", 'object_name': 'Site', 'db_table': "'site'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['site.Site']", 'null': 'True', 'blank': 'True'})
        },
        'site.siteav': {
            'Meta': {'unique_together': "(('site', 'attribute'),)", 'object_name': 'SiteAV', 'db_table': "'site_av'"},
            'attribute': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eav.Attribute']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['site.Site']"}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "'attribute'", 'max_length': '255'})
        }
    }

    complete_apps = ['site']