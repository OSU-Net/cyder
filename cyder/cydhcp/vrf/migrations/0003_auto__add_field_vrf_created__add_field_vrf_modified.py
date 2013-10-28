# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Vrf.created'
        db.add_column('vrf', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Vrf.modified'
        db.add_column('vrf', 'modified',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Vrf.created'
        db.delete_column('vrf', 'created')

        # Deleting field 'Vrf.modified'
        db.delete_column('vrf', 'modified')


    models = {
        'vrf.vrf': {
            'Meta': {'object_name': 'Vrf', 'db_table': "'vrf'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'vrf.vrfkeyvalue': {
            'Meta': {'object_name': 'VrfKeyValue', 'db_table': "'vrf_kv'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_quoted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'vrf': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vrf.Vrf']"})
        }
    }

    complete_apps = ['vrf']