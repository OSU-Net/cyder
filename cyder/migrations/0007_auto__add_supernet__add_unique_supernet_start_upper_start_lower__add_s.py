# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Network', fields ['ip_upper', 'ip_lower', 'prefixlen']
        db.delete_unique('network', ['ip_upper', 'ip_lower', 'prefixlen'])

        # Adding model 'Supernet'
        db.create_table('supernet', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ip_type', self.gf('django.db.models.fields.CharField')(default='4', max_length=1)),
            ('start_upper', self.gf('django.db.models.fields.BigIntegerField')(blank=True)),
            ('start_lower', self.gf('django.db.models.fields.BigIntegerField')(blank=True)),
            ('end_upper', self.gf('django.db.models.fields.BigIntegerField')(blank=True)),
            ('end_lower', self.gf('django.db.models.fields.BigIntegerField')(blank=True)),
            ('network_str', self.gf('django.db.models.fields.CharField')(max_length=49)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
        ))
        db.send_create_signal('cyder', ['Supernet'])

        # Adding unique constraint on 'Supernet', fields ['start_upper', 'start_lower']
        db.create_unique('supernet', ['start_upper', 'start_lower'])

        # Adding model 'SupernetAV'
        db.create_table('supernet_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Supernet'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['SupernetAV'])

        # Adding unique constraint on 'SupernetAV', fields ['entity', 'attribute']
        db.create_unique('supernet_av', ['entity_id', 'attribute_id'])

        # Deleting field 'Network.ip_upper'
        db.delete_column('network', 'ip_upper')

        # Deleting field 'Network.prefixlen'
        db.delete_column('network', 'prefixlen')

        # Deleting field 'Network.ip_lower'
        db.delete_column('network', 'ip_lower')

        # Adding field 'Network.start_upper'
        db.add_column('network', 'start_upper',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0, blank=True),
                      keep_default=False)

        # Adding field 'Network.start_lower'
        db.add_column('network', 'start_lower',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0, blank=True),
                      keep_default=False)

        # Adding field 'Network.end_upper'
        db.add_column('network', 'end_upper',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0, blank=True),
                      keep_default=False)

        # Adding field 'Network.end_lower'
        db.add_column('network', 'end_lower',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Removing unique constraint on 'SupernetAV', fields ['entity', 'attribute']
        db.delete_unique('supernet_av', ['entity_id', 'attribute_id'])

        # Removing unique constraint on 'Supernet', fields ['start_upper', 'start_lower']
        db.delete_unique('supernet', ['start_upper', 'start_lower'])

        # Deleting model 'Supernet'
        db.delete_table('supernet')

        # Deleting model 'SupernetAV'
        db.delete_table('supernet_av')

        # Adding field 'Network.ip_upper'
        db.add_column('network', 'ip_upper',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0, blank=True),
                      keep_default=False)

        # Adding field 'Network.prefixlen'
        db.add_column('network', 'prefixlen',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Network.ip_lower'
        db.add_column('network', 'ip_lower',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0, blank=True),
                      keep_default=False)

        # Deleting field 'Network.start_upper'
        db.delete_column('network', 'start_upper')

        # Deleting field 'Network.start_lower'
        db.delete_column('network', 'start_lower')

        # Deleting field 'Network.end_upper'
        db.delete_column('network', 'end_upper')

        # Deleting field 'Network.end_lower'
        db.delete_column('network', 'end_lower')

        # Adding unique constraint on 'Network', fields ['ip_upper', 'ip_lower', 'prefixlen']
        db.create_unique('network', ['ip_upper', 'ip_lower', 'prefixlen'])


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'cyder.addressrecord': {
            'Meta': {'unique_together': "(('label', 'domain', 'fqdn', 'ip_upper', 'ip_lower', 'ip_type'),)", 'object_name': 'AddressRecord', 'db_table': "'address_record'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'ctnr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Ctnr']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Domain']"}),
            'fqdn': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_lower': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ip_str': ('django.db.models.fields.CharField', [], {'max_length': '39'}),
            'ip_type': ('django.db.models.fields.CharField', [], {'default': "'4'", 'max_length': '1'}),
            'ip_upper': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '63', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'}),
            'views': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cyder.View']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'cyder.attribute': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Attribute', 'db_table': "'attribute'"},
            'attribute_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value_type': ('cyder.base.eav.fields.AttributeValueTypeField', [], {'attribute_type_field': "''", 'max_length': '20'})
        },
        'cyder.buildmanifest': {
            'Meta': {'object_name': 'BuildManifest'},
            'build_run': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.DNSBuildRun']"}),
            'files': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'zhash': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'zname': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'cyder.cname': {
            'Meta': {'unique_together': "(('label', 'domain', 'target'),)", 'object_name': 'CNAME', 'db_table': "'cname'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'ctnr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Ctnr']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Domain']"}),
            'fqdn': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '63', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'target': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'}),
            'views': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cyder.View']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'cyder.ctnr': {
            'Meta': {'object_name': 'Ctnr', 'db_table': "'ctnr'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'domains': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cyder.Domain']", 'symmetrical': 'False', 'blank': 'True'}),
            'email_contact': ('django.db.models.fields.CharField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'ranges': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cyder.Range']", 'symmetrical': 'False', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'ctnrs'", 'blank': 'True', 'through': "orm['cyder.CtnrUser']", 'to': "orm['auth.User']"}),
            'workgroups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cyder.Workgroup']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'cyder.ctnruser': {
            'Meta': {'unique_together': "(('ctnr', 'user'),)", 'object_name': 'CtnrUser', 'db_table': "'ctnr_users'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'ctnr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Ctnr']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'cyder.dnsbuildrun': {
            'Meta': {'object_name': 'DNSBuildRun'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log': ('django.db.models.fields.TextField', [], {})
        },
        'cyder.domain': {
            'Meta': {'object_name': 'Domain', 'db_table': "'domain'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'delegated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dirty': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_reverse': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'master_domain': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['cyder.Domain']", 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'purgeable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'soa': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['cyder.SOA']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'cyder.dynamicinterface': {
            'Meta': {'unique_together': "(('range', 'mac'),)", 'object_name': 'DynamicInterface', 'db_table': "'dynamic_interface'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'dhcp_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'expire': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'mac': ('cyder.base.fields.MacAddrField', [], {'max_length': '17', 'null': 'True', 'dhcp_enabled': "'dhcp_enabled'"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'range': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Range']"}),
            'system': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.System']"}),
            'workgroup': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['cyder.Workgroup']"})
        },
        'cyder.mx': {
            'Meta': {'unique_together': "(('domain', 'label', 'server'),)", 'object_name': 'MX', 'db_table': "'mx'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'ctnr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Ctnr']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Domain']"}),
            'fqdn': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '63', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'server': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'}),
            'views': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cyder.View']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'cyder.nameserver': {
            'Meta': {'unique_together': "(('domain', 'server'),)", 'object_name': 'Nameserver', 'db_table': "'nameserver'"},
            'addr_glue': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'nameserver_set'", 'null': 'True', 'to': "orm['cyder.AddressRecord']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intr_glue': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'nameserver_set'", 'null': 'True', 'to': "orm['cyder.StaticInterface']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'server': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'}),
            'views': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cyder.View']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'cyder.network': {
            'Meta': {'object_name': 'Network', 'db_table': "'network'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'dhcpd_raw_include': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'end_lower': ('django.db.models.fields.BigIntegerField', [], {'blank': 'True'}),
            'end_upper': ('django.db.models.fields.BigIntegerField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_type': ('django.db.models.fields.CharField', [], {'default': "'4'", 'max_length': '1'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'network_str': ('django.db.models.fields.CharField', [], {'max_length': '49'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Site']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'start_lower': ('django.db.models.fields.BigIntegerField', [], {'blank': 'True'}),
            'start_upper': ('django.db.models.fields.BigIntegerField', [], {'blank': 'True'}),
            'vlan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Vlan']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'vrf': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['cyder.Vrf']"})
        },
        'cyder.networkav': {
            'Meta': {'ordering': "('attribute__name',)", 'unique_together': "(('entity', 'attribute'),)", 'object_name': 'NetworkAV', 'db_table': "'network_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Network']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "''", 'max_length': '255'})
        },
        'cyder.ptr': {
            'Meta': {'unique_together': "(('ip_str', 'ip_type', 'fqdn'),)", 'object_name': 'PTR', 'db_table': "'ptr'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'ctnr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Ctnr']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'fqdn': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_lower': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ip_str': ('django.db.models.fields.CharField', [], {'max_length': '39'}),
            'ip_type': ('django.db.models.fields.CharField', [], {'default': "'4'", 'max_length': '1'}),
            'ip_upper': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'reverse_domain': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reverse_ptr_set'", 'blank': 'True', 'to': "orm['cyder.Domain']"}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'}),
            'views': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cyder.View']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'cyder.range': {
            'Meta': {'unique_together': "(('start_upper', 'start_lower', 'end_upper', 'end_lower'),)", 'object_name': 'Range', 'db_table': "'range'"},
            'allow': ('django.db.models.fields.CharField', [], {'default': "'l'", 'max_length': '1'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dhcp_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'dhcpd_raw_include': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Domain']", 'null': 'True', 'blank': 'True'}),
            'end_lower': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'end_str': ('django.db.models.fields.CharField', [], {'max_length': '39'}),
            'end_upper': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_type': ('django.db.models.fields.CharField', [], {'default': "'4'", 'max_length': '1'}),
            'is_reserved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'network': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Network']"}),
            'range_type': ('django.db.models.fields.CharField', [], {'default': "'st'", 'max_length': '2'}),
            'range_usage': ('django.db.models.fields.IntegerField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'start_lower': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'start_str': ('django.db.models.fields.CharField', [], {'max_length': '39'}),
            'start_upper': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'views': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cyder.View']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'cyder.rangeav': {
            'Meta': {'ordering': "('attribute__name',)", 'unique_together': "(('entity', 'attribute'),)", 'object_name': 'RangeAV', 'db_table': "'range_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Range']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "''", 'max_length': '255'})
        },
        'cyder.site': {
            'Meta': {'unique_together': "(('name', 'parent'),)", 'object_name': 'Site', 'db_table': "'site'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Site']", 'null': 'True', 'blank': 'True'})
        },
        'cyder.siteav': {
            'Meta': {'ordering': "('attribute__name',)", 'unique_together': "(('entity', 'attribute'),)", 'object_name': 'SiteAV', 'db_table': "'site_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Site']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "''", 'max_length': '255'})
        },
        'cyder.soa': {
            'Meta': {'object_name': 'SOA', 'db_table': "'soa'"},
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'dirty': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dns_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'expire': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1209600'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_signed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'minimum': ('django.db.models.fields.PositiveIntegerField', [], {'default': '180'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'primary': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'refresh': ('django.db.models.fields.PositiveIntegerField', [], {'default': '180'}),
            'retry': ('django.db.models.fields.PositiveIntegerField', [], {'default': '86400'}),
            'root_domain': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'root_of_soa'", 'unique': 'True', 'to': "orm['cyder.Domain']"}),
            'serial': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1435079005'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'})
        },
        'cyder.soaav': {
            'Meta': {'ordering': "('attribute__name',)", 'unique_together': "(('entity', 'attribute'),)", 'object_name': 'SOAAV', 'db_table': "'soa_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.SOA']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "''", 'max_length': '255'})
        },
        'cyder.srv': {
            'Meta': {'unique_together': "(('label', 'domain', 'target', 'port'),)", 'object_name': 'SRV', 'db_table': "'srv'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'ctnr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Ctnr']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Domain']"}),
            'fqdn': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '63', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'port': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'priority': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'target': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'}),
            'views': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cyder.View']", 'symmetrical': 'False', 'blank': 'True'}),
            'weight': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'cyder.sshfp': {
            'Meta': {'unique_together': "(('domain', 'label'),)", 'object_name': 'SSHFP', 'db_table': "'sshfp'"},
            'algorithm_number': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'ctnr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Ctnr']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Domain']"}),
            'fingerprint_type': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'fqdn': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '63', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'}),
            'views': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cyder.View']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'cyder.staticinterface': {
            'Meta': {'unique_together': "(('ip_upper', 'ip_lower'), ('label', 'domain'))", 'object_name': 'StaticInterface', 'db_table': "'static_interface'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'dhcp_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'dns_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Domain']"}),
            'expire': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'fqdn': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_lower': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ip_str': ('django.db.models.fields.CharField', [], {'max_length': '39'}),
            'ip_type': ('django.db.models.fields.CharField', [], {'default': "'4'", 'max_length': '1'}),
            'ip_upper': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '63', 'blank': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'mac': ('cyder.base.fields.MacAddrField', [], {'max_length': '17', 'null': 'True', 'dhcp_enabled': "'dhcp_enabled'"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'reverse_domain': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reverse_staticintr_set'", 'null': 'True', 'to': "orm['cyder.Domain']"}),
            'system': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.System']"}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'}),
            'views': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cyder.View']", 'symmetrical': 'False', 'blank': 'True'}),
            'workgroup': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['cyder.Workgroup']"})
        },
        'cyder.supernet': {
            'Meta': {'unique_together': "(('start_upper', 'start_lower'),)", 'object_name': 'Supernet', 'db_table': "'supernet'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'end_lower': ('django.db.models.fields.BigIntegerField', [], {'blank': 'True'}),
            'end_upper': ('django.db.models.fields.BigIntegerField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_type': ('django.db.models.fields.CharField', [], {'default': "'4'", 'max_length': '1'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'network_str': ('django.db.models.fields.CharField', [], {'max_length': '49'}),
            'start_lower': ('django.db.models.fields.BigIntegerField', [], {'blank': 'True'}),
            'start_upper': ('django.db.models.fields.BigIntegerField', [], {'blank': 'True'})
        },
        'cyder.supernetav': {
            'Meta': {'ordering': "('attribute__name',)", 'unique_together': "(('entity', 'attribute'),)", 'object_name': 'SupernetAV', 'db_table': "'supernet_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Supernet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "''", 'max_length': '255'})
        },
        'cyder.system': {
            'Meta': {'object_name': 'System', 'db_table': "'system'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'ctnr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Ctnr']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'cyder.systemav': {
            'Meta': {'ordering': "('attribute__name',)", 'unique_together': "(('entity', 'attribute'),)", 'object_name': 'SystemAV', 'db_table': "'system_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.System']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "''", 'max_length': '255'})
        },
        'cyder.task': {
            'Meta': {'ordering': "['task']", 'object_name': 'Task', 'db_table': "u'task'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ttype': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'cyder.token': {
            'Meta': {'object_name': 'Token'},
            'can_write': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'purpose': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'cyder.txt': {
            'Meta': {'object_name': 'TXT', 'db_table': "'txt'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'ctnr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Ctnr']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Domain']"}),
            'fqdn': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '63', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'}),
            'txt_data': ('django.db.models.fields.TextField', [], {}),
            'views': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cyder.View']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'cyder.userprofile': {
            'Meta': {'object_name': 'UserProfile', 'db_table': "'auth_user_profile'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'default_ctnr': ('django.db.models.fields.related.ForeignKey', [], {'default': '2', 'to': "orm['cyder.Ctnr']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'cyder.view': {
            'Meta': {'unique_together': "(('name',),)", 'object_name': 'View', 'db_table': "'view'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'cyder.vlan': {
            'Meta': {'unique_together': "(('name', 'number'),)", 'object_name': 'Vlan', 'db_table': "'vlan'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'cyder.vlanav': {
            'Meta': {'ordering': "('attribute__name',)", 'unique_together': "(('entity', 'attribute'),)", 'object_name': 'VlanAV', 'db_table': "'vlan_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Vlan']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "''", 'max_length': '255'})
        },
        'cyder.vrf': {
            'Meta': {'object_name': 'Vrf', 'db_table': "'vrf'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'cyder.vrfav': {
            'Meta': {'ordering': "('attribute__name',)", 'unique_together': "(('entity', 'attribute'),)", 'object_name': 'VrfAV', 'db_table': "'vrf_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Vrf']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "''", 'max_length': '255'})
        },
        'cyder.workgroup': {
            'Meta': {'object_name': 'Workgroup', 'db_table': "'workgroup'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'cyder.workgroupav': {
            'Meta': {'ordering': "('attribute__name',)", 'unique_together': "(('entity', 'attribute'),)", 'object_name': 'WorkgroupAV', 'db_table': "'workgroup_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Workgroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "''", 'max_length': '255'})
        }
    }

    complete_apps = ['cyder']