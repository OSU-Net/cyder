# -*- coding: utf-8 -*-
from south.v2 import DataMigration

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F

def root_domain(soa):
    try:
        return soa.domain_set.get(~Q(master_domain__soa=F('soa')),
                                   soa__isnull=False)
    except ObjectDoesNotExist:
        return None

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        seen = []
        for soa in orm.SOA.objects.all():
            dom = root_domain(soa)
            assert dom
            assert dom not in seen
            seen.append(dom)
            soa.root_domain = dom
            soa.save()

    def backwards(self, orm):
        "Write your backwards methods here."

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
        'soa.soa': {
            'Meta': {'object_name': 'SOA', 'db_table': "'soa'"},
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'dirty': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dns_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'expire': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1209600'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_signed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'minimum': ('django.db.models.fields.PositiveIntegerField', [], {'default': '180'}),
            'primary': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'refresh': ('django.db.models.fields.PositiveIntegerField', [], {'default': '180'}),
            'retry': ('django.db.models.fields.PositiveIntegerField', [], {'default': '86400'}),
            'root_domain': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'root_soa'", 'unique': 'True', 'to': "orm['domain.Domain']"}),
            'serial': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1380835484'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'})
        },
        'soa.soakeyvalue': {
            'Meta': {'object_name': 'SOAKeyValue', 'db_table': "'soa_kv'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_quoted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'soa': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'keyvalue_set'", 'to': "orm['soa.SOA']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['soa']
    symmetrical = True
