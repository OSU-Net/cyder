# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Vrf.network'
        db.delete_column('vrf', 'network_id')


    def backwards(self, orm):
        # Adding field 'Vrf.network'
        db.add_column('vrf', 'network',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['network.Network'], null=True),
                      keep_default=False)


    models = {
        'vrf.vrf': {
            'Meta': {'object_name': 'Vrf', 'db_table': "'vrf'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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