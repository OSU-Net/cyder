# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

class Migration(SchemaMigration):

    def forwards(self, orm):
        date = datetime.date.today()
        # Adding field 'PTR.created'
        db.add_column('ptr', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=date, blank=True),
                      keep_default=False)

        # Adding field 'PTR.modified'
        db.add_column('ptr', 'modified',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=date, blank=True),
                      keep_default=False)

        # Adding field 'PTR.label'
        db.add_column('ptr', 'label',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=63, blank=True),
                      keep_default=False)

        # Adding field 'PTR.fqdn'
        db.add_column('ptr', 'fqdn',
                      self.gf('django.db.models.fields.CharField')(db_index=True, default='', max_length=255, blank=True),
                      keep_default=False)

        if not db.dry_run:
            nulldom, _ = orm['domain.Domain'].objects.get_or_create(name="null")
            # Adding field 'PTR.domain'
            db.add_column('ptr', 'domain',
                          self.gf('django.db.models.fields.related.ForeignKey')(default=nulldom.pk, to=orm['domain.Domain']),
                          keep_default=False)

            for ptr in orm.PTR.objects.all():
                ptr.fqdn = ptr.name
                try:
                    dom = orm['domain.Domain'].objects.get(name=ptr.name)
                    ptr.domain = dom
                except ObjectDoesNotExist:
                    pass
                ptr.save()


    def backwards(self, orm):
        # Deleting field 'PTR.created'
        db.delete_column('ptr', 'created')

        # Deleting field 'PTR.modified'
        db.delete_column('ptr', 'modified')

        # Deleting field 'PTR.domain'
        db.delete_column('ptr', 'domain_id')

        # Deleting field 'PTR.label'
        db.delete_column('ptr', 'label')

        # Deleting field 'PTR.fqdn'
        db.delete_column('ptr', 'fqdn')


    models = {
        'domain.domain': {
            'Meta': {'object_name': 'Domain', 'db_table': "'domain'"},
            'delegated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dirty': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_reverse': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'master_domain': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['domain.Domain']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'purgeable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'soa': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['soa.SOA']", 'null': 'True', 'blank': 'True'})
        },
        'ptr.ptr': {
            'Meta': {'unique_together': "(('ip_str', 'ip_type', 'name'),)", 'object_name': 'PTR', 'db_table': "'ptr'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['domain.Domain']"}),
            'fqdn': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_lower': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ip_str': ('django.db.models.fields.CharField', [], {'max_length': '39'}),
            'ip_type': ('django.db.models.fields.CharField', [], {'default': "'4'", 'max_length': '1'}),
            'ip_upper': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '63', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'reverse_domain': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reverse'", 'blank': 'True', 'to': "orm['domain.Domain']"}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'}),
            'views': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['view.View']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'soa.soa': {
            'Meta': {'unique_together': "(('primary', 'contact', 'description'),)", 'object_name': 'SOA', 'db_table': "'soa'"},
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'dirty': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'expire': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1209600'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_signed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'minimum': ('django.db.models.fields.PositiveIntegerField', [], {'default': '180'}),
            'primary': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'refresh': ('django.db.models.fields.PositiveIntegerField', [], {'default': '180'}),
            'retry': ('django.db.models.fields.PositiveIntegerField', [], {'default': '86400'}),
            'serial': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1376448443'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'})
        },
        'view.view': {
            'Meta': {'unique_together': "(('name',),)", 'object_name': 'View', 'db_table': "'view'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['ptr']
