# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Attribute'
        db.create_table('attribute', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('attribute_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('value_type', self.gf('cyder.base.eav.fields.AttributeValueTypeField')(attribute_type_field='attribute_type', max_length=20)),
        ))
        db.send_create_signal('eav', ['Attribute'])


    def backwards(self, orm):
        # Deleting model 'Attribute'
        db.delete_table('attribute')


    models = {
        'eav.attribute': {
            'Meta': {'object_name': 'Attribute', 'db_table': "'attribute'"},
            'attribute_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value_type': ('cyder.base.eav.fields.AttributeValueTypeField', [], {'attribute_type_field': "'attribute_type'", 'max_length': '20'})
        }
    }

    complete_apps = ['eav']