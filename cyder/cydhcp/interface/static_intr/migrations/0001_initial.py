# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'StaticInterface'
        db.create_table('static_interface', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('ip_str', self.gf('django.db.models.fields.CharField')(max_length=39)),
            ('ip_upper', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('ip_lower', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('ip_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['domain.Domain'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=63, null=True, blank=True)),
            ('fqdn', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, null=True, blank=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mac', self.gf('django.db.models.fields.CharField')(max_length=17)),
            ('reverse_domain', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='reverse_staticintr_set', null=True, to=orm['domain.Domain'])),
            ('system', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['system.System'], null=True, blank=True)),
            ('vrf', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vrf.Vrf'], null=True, blank=True)),
            ('workgroup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['workgroup.Workgroup'], null=True, blank=True)),
            ('dhcp_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('dns_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('static_intr', ['StaticInterface'])

        # Adding unique constraint on 'StaticInterface', fields ['ip_upper', 'ip_lower', 'label', 'domain', 'mac']
        db.create_unique('static_interface', ['ip_upper', 'ip_lower', 'label', 'domain_id', 'mac'])

        # Adding M2M table for field views on 'StaticInterface'
        db.create_table('static_interface_views', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('staticinterface', models.ForeignKey(orm['static_intr.staticinterface'], null=False)),
            ('view', models.ForeignKey(orm['view.view'], null=False))
        ))
        db.create_unique('static_interface_views', ['staticinterface_id', 'view_id'])

        # Adding model 'StaticIntrKeyValue'
        db.create_table('static_interface_kv', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_option', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_statement', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_validator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('intr', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['static_intr.StaticInterface'])),
        ))
        db.send_create_signal('static_intr', ['StaticIntrKeyValue'])

        # Adding unique constraint on 'StaticIntrKeyValue', fields ['key', 'value', 'intr']
        db.create_unique('static_interface_kv', ['key', 'value', 'intr_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'StaticIntrKeyValue', fields ['key', 'value', 'intr']
        db.delete_unique('static_interface_kv', ['key', 'value', 'intr_id'])

        # Removing unique constraint on 'StaticInterface', fields ['ip_upper', 'ip_lower', 'label', 'domain', 'mac']
        db.delete_unique('static_interface', ['ip_upper', 'ip_lower', 'label', 'domain_id', 'mac'])

        # Deleting model 'StaticInterface'
        db.delete_table('static_interface')

        # Removing M2M table for field views on 'StaticInterface'
        db.delete_table('static_interface_views')

        # Deleting model 'StaticIntrKeyValue'
        db.delete_table('static_interface_kv')


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
        'network.network': {
            'Meta': {'unique_together': "(('ip_upper', 'ip_lower', 'prefixlen'),)", 'object_name': 'Network', 'db_table': "'network'"},
            'dhcpd_raw_include': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_lower': ('django.db.models.fields.BigIntegerField', [], {'blank': 'True'}),
            'ip_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'ip_upper': ('django.db.models.fields.BigIntegerField', [], {'blank': 'True'}),
            'network_str': ('django.db.models.fields.CharField', [], {'max_length': '49'}),
            'prefixlen': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['site.Site']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'vlan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vlan.Vlan']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'site.site': {
            'Meta': {'unique_together': "(('name', 'parent'),)", 'object_name': 'Site', 'db_table': "'site'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['site.Site']", 'null': 'True', 'blank': 'True'})
        },
        'soa.soa': {
            'Meta': {'unique_together': "(('primary', 'contact', 'description'),)", 'object_name': 'SOA', 'db_table': "'soa'"},
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'dirty': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'expire': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1209600'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_signed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'minimum': ('django.db.models.fields.PositiveIntegerField', [], {'default': '180'}),
            'primary': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'refresh': ('django.db.models.fields.PositiveIntegerField', [], {'default': '180'}),
            'retry': ('django.db.models.fields.PositiveIntegerField', [], {'default': '86400'}),
            'serial': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1368820927'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'})
        },
        'static_intr.staticinterface': {
            'Meta': {'unique_together': "(('ip_upper', 'ip_lower', 'label', 'domain', 'mac'),)", 'object_name': 'StaticInterface', 'db_table': "'static_interface'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'dhcp_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'dns_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['domain.Domain']"}),
            'fqdn': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_lower': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ip_str': ('django.db.models.fields.CharField', [], {'max_length': '39'}),
            'ip_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'ip_upper': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '63', 'null': 'True', 'blank': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '17'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'reverse_domain': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reverse_staticintr_set'", 'null': 'True', 'to': "orm['domain.Domain']"}),
            'system': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['system.System']", 'null': 'True', 'blank': 'True'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'}),
            'views': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['view.View']", 'symmetrical': 'False', 'blank': 'True'}),
            'vrf': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vrf.Vrf']", 'null': 'True', 'blank': 'True'}),
            'workgroup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workgroup.Workgroup']", 'null': 'True', 'blank': 'True'})
        },
        'static_intr.staticintrkeyvalue': {
            'Meta': {'unique_together': "(('key', 'value', 'intr'),)", 'object_name': 'StaticIntrKeyValue', 'db_table': "'static_interface_kv'"},
            'has_validator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['static_intr.StaticInterface']"}),
            'is_option': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_quoted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_statement': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'system.system': {
            'Meta': {'unique_together': "(('name', 'location', 'department'),)", 'object_name': 'System', 'db_table': "'system'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'department': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'view.view': {
            'Meta': {'unique_together': "(('name',),)", 'object_name': 'View', 'db_table': "'view'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'vlan.vlan': {
            'Meta': {'unique_together': "(('name', 'number'),)", 'object_name': 'Vlan', 'db_table': "'vlan'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'vrf.vrf': {
            'Meta': {'object_name': 'Vrf', 'db_table': "'vrf'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'network': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['network.Network']", 'null': 'True'})
        },
        'workgroup.workgroup': {
            'Meta': {'object_name': 'Workgroup', 'db_table': "'workgroup'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        }
    }

    complete_apps = ['static_intr']