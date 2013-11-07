# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'RangeKeyValue', fields ['key', 'value', 'range']
        db.delete_unique('range_kv', ['key', 'value', 'range_id'])

        # Removing unique constraint on 'WorkgroupKeyValue', fields ['key', 'value', 'workgroup']
        db.delete_unique('workgroup_kv', ['key', 'value', 'workgroup_id'])

        # Removing unique constraint on 'NetworkKeyValue', fields ['key', 'value', 'network']
        db.delete_unique('network_kv', ['key', 'value', 'network_id'])

        # Removing unique constraint on 'SystemKeyValue', fields ['key', 'value', 'system']
        db.delete_unique('system_kv', ['key', 'value', 'system_id'])

        # Removing unique constraint on 'StaticIntrKeyValue', fields ['key', 'value', 'static_interface']
        db.delete_unique('static_interface_kv', ['key', 'value', 'static_interface_id'])

        # Removing unique constraint on 'VlanKeyValue', fields ['key', 'value']
        db.delete_unique('vlan_kv', ['key', 'value'])

        # Removing unique constraint on 'SiteKeyValue', fields ['key', 'value']
        db.delete_unique('site_kv', ['key', 'value'])

        # Removing unique constraint on 'DynamicIntrKeyValue', fields ['key', 'value', 'dynamic_interface']
        db.delete_unique('dynamic_interface_kv', ['key', 'value', 'dynamic_interface_id'])

        # Deleting model 'DynamicIntrKeyValue'
        db.delete_table('dynamic_interface_kv')

        # Deleting model 'SOAKeyValue'
        db.delete_table('soa_kv')

        # Deleting model 'SiteKeyValue'
        db.delete_table('site_kv')

        # Deleting model 'VlanKeyValue'
        db.delete_table('vlan_kv')

        # Deleting model 'VrfKeyValue'
        db.delete_table('vrf_kv')

        # Deleting model 'StaticIntrKeyValue'
        db.delete_table('static_interface_kv')

        # Deleting model 'SystemKeyValue'
        db.delete_table('system_kv')

        # Deleting model 'NetworkKeyValue'
        db.delete_table('network_kv')

        # Deleting model 'WorkgroupKeyValue'
        db.delete_table('workgroup_kv')

        # Deleting model 'RangeKeyValue'
        db.delete_table('range_kv')

        # Adding model 'DynamicInterfaceAV'
        db.create_table('dynamic_interface_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.DynamicInterface'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['DynamicInterfaceAV'])

        # Adding unique constraint on 'DynamicInterfaceAV', fields ['entity', 'attribute']
        db.create_unique('dynamic_interface_av', ['entity_id', 'attribute_id'])

        # Adding model 'VlanAV'
        db.create_table('vlan_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Vlan'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['VlanAV'])

        # Adding unique constraint on 'VlanAV', fields ['entity', 'attribute']
        db.create_unique('vlan_av', ['entity_id', 'attribute_id'])

        # Adding model 'SiteAV'
        db.create_table('site_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Site'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['SiteAV'])

        # Adding unique constraint on 'SiteAV', fields ['entity', 'attribute']
        db.create_unique('site_av', ['entity_id', 'attribute_id'])

        # Adding model 'StaticInterfaceAV'
        db.create_table('static_interface_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.StaticInterface'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['StaticInterfaceAV'])

        # Adding unique constraint on 'StaticInterfaceAV', fields ['entity', 'attribute']
        db.create_unique('static_interface_av', ['entity_id', 'attribute_id'])

        # Adding model 'WorkgroupAV'
        db.create_table('workgroup_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Workgroup'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['WorkgroupAV'])

        # Adding unique constraint on 'WorkgroupAV', fields ['entity', 'attribute']
        db.create_unique('workgroup_av', ['entity_id', 'attribute_id'])

        # Adding model 'VrfAV'
        db.create_table('vrf_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Vrf'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['VrfAV'])

        # Adding unique constraint on 'VrfAV', fields ['entity', 'attribute']
        db.create_unique('vrf_av', ['entity_id', 'attribute_id'])

        # Adding model 'NetworkAV'
        db.create_table('network_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Network'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['NetworkAV'])

        # Adding unique constraint on 'NetworkAV', fields ['entity', 'attribute']
        db.create_unique('network_av', ['entity_id', 'attribute_id'])

        # Adding model 'Attribute'
        db.create_table('attribute', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('attribute_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('value_type', self.gf('cyder.base.eav.fields.AttributeValueTypeField')(attribute_type_field='', max_length=20)),
        ))
        db.send_create_signal('cyder', ['Attribute'])

        # Adding model 'SOAAV'
        db.create_table('soa_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.SOA'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['SOAAV'])

        # Adding unique constraint on 'SOAAV', fields ['entity', 'attribute']
        db.create_unique('soa_av', ['entity_id', 'attribute_id'])

        # Adding model 'RangeAV'
        db.create_table('range_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Range'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['RangeAV'])

        # Adding unique constraint on 'RangeAV', fields ['entity', 'attribute']
        db.create_unique('range_av', ['entity_id', 'attribute_id'])

        # Adding model 'SystemAV'
        db.create_table('system_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.System'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['SystemAV'])

        # Adding unique constraint on 'SystemAV', fields ['entity', 'attribute']
        db.create_unique('system_av', ['entity_id', 'attribute_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'SystemAV', fields ['entity', 'attribute']
        db.delete_unique('system_av', ['entity_id', 'attribute_id'])

        # Removing unique constraint on 'RangeAV', fields ['entity', 'attribute']
        db.delete_unique('range_av', ['entity_id', 'attribute_id'])

        # Removing unique constraint on 'SOAAV', fields ['entity', 'attribute']
        db.delete_unique('soa_av', ['entity_id', 'attribute_id'])

        # Removing unique constraint on 'NetworkAV', fields ['entity', 'attribute']
        db.delete_unique('network_av', ['entity_id', 'attribute_id'])

        # Removing unique constraint on 'VrfAV', fields ['entity', 'attribute']
        db.delete_unique('vrf_av', ['entity_id', 'attribute_id'])

        # Removing unique constraint on 'WorkgroupAV', fields ['entity', 'attribute']
        db.delete_unique('workgroup_av', ['entity_id', 'attribute_id'])

        # Removing unique constraint on 'StaticInterfaceAV', fields ['entity', 'attribute']
        db.delete_unique('static_interface_av', ['entity_id', 'attribute_id'])

        # Removing unique constraint on 'SiteAV', fields ['entity', 'attribute']
        db.delete_unique('site_av', ['entity_id', 'attribute_id'])

        # Removing unique constraint on 'VlanAV', fields ['entity', 'attribute']
        db.delete_unique('vlan_av', ['entity_id', 'attribute_id'])

        # Removing unique constraint on 'DynamicInterfaceAV', fields ['entity', 'attribute']
        db.delete_unique('dynamic_interface_av', ['entity_id', 'attribute_id'])

        # Adding model 'DynamicIntrKeyValue'
        db.create_table('dynamic_interface_kv', (
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_option', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_validator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('dynamic_interface', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.DynamicInterface'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_statement', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('cyder', ['DynamicIntrKeyValue'])

        # Adding unique constraint on 'DynamicIntrKeyValue', fields ['key', 'value', 'dynamic_interface']
        db.create_unique('dynamic_interface_kv', ['key', 'value', 'dynamic_interface_id'])

        # Adding model 'SOAKeyValue'
        db.create_table('soa_kv', (
            ('soa', self.gf('django.db.models.fields.related.ForeignKey')(related_name='keyvalue_set', to=orm['cyder.SOA'])),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('cyder', ['SOAKeyValue'])

        # Adding model 'SiteKeyValue'
        db.create_table('site_kv', (
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Site'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('cyder', ['SiteKeyValue'])

        # Adding unique constraint on 'SiteKeyValue', fields ['key', 'value']
        db.create_unique('site_kv', ['key', 'value'])

        # Adding model 'VlanKeyValue'
        db.create_table('vlan_kv', (
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('vlan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Vlan'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('cyder', ['VlanKeyValue'])

        # Adding unique constraint on 'VlanKeyValue', fields ['key', 'value']
        db.create_unique('vlan_kv', ['key', 'value'])

        # Adding model 'VrfKeyValue'
        db.create_table('vrf_kv', (
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('vrf', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Vrf'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('cyder', ['VrfKeyValue'])

        # Adding model 'StaticIntrKeyValue'
        db.create_table('static_interface_kv', (
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_option', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_validator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('static_interface', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.StaticInterface'])),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_statement', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('cyder', ['StaticIntrKeyValue'])

        # Adding unique constraint on 'StaticIntrKeyValue', fields ['key', 'value', 'static_interface']
        db.create_unique('static_interface_kv', ['key', 'value', 'static_interface_id'])

        # Adding model 'SystemKeyValue'
        db.create_table('system_kv', (
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('system', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.System'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('cyder', ['SystemKeyValue'])

        # Adding unique constraint on 'SystemKeyValue', fields ['key', 'value', 'system']
        db.create_unique('system_kv', ['key', 'value', 'system_id'])

        # Adding model 'NetworkKeyValue'
        db.create_table('network_kv', (
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_option', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_validator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_statement', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('network', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Network'])),
        ))
        db.send_create_signal('cyder', ['NetworkKeyValue'])

        # Adding unique constraint on 'NetworkKeyValue', fields ['key', 'value', 'network']
        db.create_unique('network_kv', ['key', 'value', 'network_id'])

        # Adding model 'WorkgroupKeyValue'
        db.create_table('workgroup_kv', (
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_option', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_validator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_statement', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('workgroup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Workgroup'])),
        ))
        db.send_create_signal('cyder', ['WorkgroupKeyValue'])

        # Adding unique constraint on 'WorkgroupKeyValue', fields ['key', 'value', 'workgroup']
        db.create_unique('workgroup_kv', ['key', 'value', 'workgroup_id'])

        # Adding model 'RangeKeyValue'
        db.create_table('range_kv', (
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('range', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Range'])),
            ('is_option', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_validator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_statement', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('cyder', ['RangeKeyValue'])

        # Adding unique constraint on 'RangeKeyValue', fields ['key', 'value', 'range']
        db.create_unique('range_kv', ['key', 'value', 'range_id'])

        # Deleting model 'DynamicInterfaceAV'
        db.delete_table('dynamic_interface_av')

        # Deleting model 'VlanAV'
        db.delete_table('vlan_av')

        # Deleting model 'SiteAV'
        db.delete_table('site_av')

        # Deleting model 'StaticInterfaceAV'
        db.delete_table('static_interface_av')

        # Deleting model 'WorkgroupAV'
        db.delete_table('workgroup_av')

        # Deleting model 'VrfAV'
        db.delete_table('vrf_av')

        # Deleting model 'NetworkAV'
        db.delete_table('network_av')

        # Deleting model 'Attribute'
        db.delete_table('attribute')

        # Deleting model 'SOAAV'
        db.delete_table('soa_av')

        # Deleting model 'RangeAV'
        db.delete_table('range_av')

        # Deleting model 'SystemAV'
        db.delete_table('system_av')


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
            'Meta': {'object_name': 'Attribute', 'db_table': "'attribute'"},
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
            'Meta': {'unique_together': "(('domain', 'label', 'target'),)", 'object_name': 'CNAME', 'db_table': "'cname'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
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
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'users'", 'blank': 'True', 'through': "orm['cyder.CtnrUser']", 'to': "orm['auth.User']"}),
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
            'soa': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['cyder.SOA']", 'null': 'True', 'blank': 'True'})
        },
        'cyder.dynamicinterface': {
            'Meta': {'object_name': 'DynamicInterface', 'db_table': "'dynamic_interface'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'ctnr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Ctnr']"}),
            'dhcp_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Domain']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'max_length': '11', 'blank': 'True'}),
            'mac': ('cyder.core.fields.MacAddrField', [], {'blank': 'True', 'max_length': '17', 'dhcp_enabled': "'dhcp_enabled'"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'range': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Range']"}),
            'system': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.System']"}),
            'workgroup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Workgroup']", 'null': 'True', 'blank': 'True'})
        },
        'cyder.dynamicinterfaceav': {
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'DynamicInterfaceAV', 'db_table': "'dynamic_interface_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.DynamicInterface']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "''", 'max_length': '255'})
        },
        'cyder.mx': {
            'Meta': {'unique_together': "(('domain', 'label', 'server', 'priority'),)", 'object_name': 'MX', 'db_table': "'mx'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
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
            'Meta': {'unique_together': "(('ip_upper', 'ip_lower', 'prefixlen'),)", 'object_name': 'Network', 'db_table': "'network'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'dhcpd_raw_include': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_lower': ('django.db.models.fields.BigIntegerField', [], {'blank': 'True'}),
            'ip_type': ('django.db.models.fields.CharField', [], {'default': "'4'", 'max_length': '1'}),
            'ip_upper': ('django.db.models.fields.BigIntegerField', [], {'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'network_str': ('django.db.models.fields.CharField', [], {'max_length': '49'}),
            'prefixlen': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Site']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'vlan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Vlan']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'vrf': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Vrf']", 'null': 'True', 'blank': 'True'})
        },
        'cyder.networkav': {
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'NetworkAV', 'db_table': "'network_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Network']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "''", 'max_length': '255'})
        },
        'cyder.ptr': {
            'Meta': {'unique_together': "(('ip_str', 'ip_type', 'fqdn'),)", 'object_name': 'PTR', 'db_table': "'ptr'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
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
            'reverse_domain': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reverse_ptr_set'", 'blank': 'True', 'to': "orm['cyder.Domain']"}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'}),
            'views': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cyder.View']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'cyder.range': {
            'Meta': {'unique_together': "(('start_upper', 'start_lower', 'end_upper', 'end_lower'),)", 'object_name': 'Range', 'db_table': "'range'"},
            'allow': ('django.db.models.fields.CharField', [], {'default': "'l'", 'max_length': '1'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'dhcp_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'dhcpd_raw_include': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end_lower': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'end_str': ('django.db.models.fields.CharField', [], {'max_length': '39'}),
            'end_upper': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_type': ('django.db.models.fields.CharField', [], {'default': "'4'", 'max_length': '1'}),
            'is_reserved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'network': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Network']", 'null': 'True', 'blank': 'True'}),
            'range_type': ('django.db.models.fields.CharField', [], {'default': "'st'", 'max_length': '2'}),
            'start_lower': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'start_str': ('django.db.models.fields.CharField', [], {'max_length': '39'}),
            'start_upper': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'})
        },
        'cyder.rangeav': {
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'RangeAV', 'db_table': "'range_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Range']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'SiteAV', 'db_table': "'site_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Site']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "''", 'max_length': '255'})
        },
        'cyder.soa': {
            'Meta': {'unique_together': "(('primary', 'contact', 'description'),)", 'object_name': 'SOA', 'db_table': "'soa'"},
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'dirty': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'expire': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1209600'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_signed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'minimum': ('django.db.models.fields.PositiveIntegerField', [], {'default': '180'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'primary': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'refresh': ('django.db.models.fields.PositiveIntegerField', [], {'default': '180'}),
            'retry': ('django.db.models.fields.PositiveIntegerField', [], {'default': '86400'}),
            'serial': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1383781801'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'})
        },
        'cyder.soaav': {
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'SOAAV', 'db_table': "'soa_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.SOA']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "''", 'max_length': '255'})
        },
        'cyder.srv': {
            'Meta': {'unique_together': "(('label', 'domain', 'target', 'port'),)", 'object_name': 'SRV', 'db_table': "'srv'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
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
            'Meta': {'object_name': 'SSHFP', 'db_table': "'sshfp'"},
            'algorithm_number': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Domain']"}),
            'fingerprint_type': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'fqdn': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '63', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'}),
            'views': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cyder.View']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'cyder.staticinterface': {
            'Meta': {'unique_together': "(('ip_upper', 'ip_lower', 'label', 'domain', 'mac'),)", 'object_name': 'StaticInterface', 'db_table': "'static_interface'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'ctnr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Ctnr']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'dhcp_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'dns_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Domain']"}),
            'fqdn': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_lower': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ip_str': ('django.db.models.fields.CharField', [], {'max_length': '39'}),
            'ip_type': ('django.db.models.fields.CharField', [], {'default': "'4'", 'max_length': '1'}),
            'ip_upper': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '63', 'blank': 'True'}),
            'last_seen': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'max_length': '11', 'blank': 'True'}),
            'mac': ('cyder.core.fields.MacAddrField', [], {'blank': 'True', 'max_length': '17', 'dhcp_enabled': "'dhcp_enabled'"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'reverse_domain': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reverse_staticintr_set'", 'null': 'True', 'to': "orm['cyder.Domain']"}),
            'system': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.System']"}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'}),
            'views': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cyder.View']", 'symmetrical': 'False', 'blank': 'True'}),
            'workgroup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Workgroup']", 'null': 'True', 'blank': 'True'})
        },
        'cyder.staticinterfaceav': {
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'StaticInterfaceAV', 'db_table': "'static_interface_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.StaticInterface']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "''", 'max_length': '255'})
        },
        'cyder.system': {
            'Meta': {'object_name': 'System', 'db_table': "'system'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'cyder.systemav': {
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'SystemAV', 'db_table': "'system_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.System']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'purpose': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'cyder.txt': {
            'Meta': {'object_name': 'TXT', 'db_table': "'txt'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
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
            'phone_number': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
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
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'VlanAV', 'db_table': "'vlan_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Vlan']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'VrfAV', 'db_table': "'vrf_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Vrf']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'WorkgroupAV', 'db_table': "'workgroup_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Workgroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "''", 'max_length': '255'})
        }
    }

    complete_apps = ['cyder']