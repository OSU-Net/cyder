# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Token'
        db.create_table('cyder_token', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('purpose', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('can_write', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('cyder', ['Token'])

        # Adding model 'Attribute'
        db.create_table('attribute', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('attribute_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('value_type', self.gf('cyder.base.eav.fields.AttributeValueTypeField')(attribute_type_field='', max_length=20)),
        ))
        db.send_create_signal('cyder', ['Attribute'])

        # Adding model 'Domain'
        db.create_table('domain', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('master_domain', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['cyder.Domain'], null=True, blank=True)),
            ('soa', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['cyder.SOA'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('is_reverse', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('dirty', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('purgeable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('delegated', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('cyder', ['Domain'])

        # Adding model 'System'
        db.create_table('system', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('cyder', ['System'])

        # Adding model 'SystemAV'
        db.create_table('system_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.System'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['SystemAV'])

        # Adding unique constraint on 'SystemAV', fields ['entity', 'attribute']
        db.create_unique('system_av', ['entity_id', 'attribute_id'])

        # Adding model 'Workgroup'
        db.create_table('workgroup', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal('cyder', ['Workgroup'])

        # Adding model 'WorkgroupAV'
        db.create_table('workgroup_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Workgroup'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['WorkgroupAV'])

        # Adding unique constraint on 'WorkgroupAV', fields ['entity', 'attribute']
        db.create_unique('workgroup_av', ['entity_id', 'attribute_id'])

        # Adding model 'View'
        db.create_table('view', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('cyder', ['View'])

        # Adding unique constraint on 'View', fields ['name']
        db.create_unique('view', ['name'])

        # Adding model 'CNAME'
        db.create_table('cname', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Domain'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=63, blank=True)),
            ('fqdn', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, blank=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('ctnr', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Ctnr'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('target', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('cyder', ['CNAME'])

        # Adding unique constraint on 'CNAME', fields ['label', 'domain', 'target']
        db.create_unique('cname', ['label', 'domain_id', 'target'])

        # Adding M2M table for field views on 'CNAME'
        m2m_table_name = db.shorten_name('cname_views')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cname', models.ForeignKey(orm['cyder.cname'], null=False)),
            ('view', models.ForeignKey(orm['cyder.view'], null=False))
        ))
        db.create_unique(m2m_table_name, ['cname_id', 'view_id'])

        # Adding model 'AddressRecord'
        db.create_table('address_record', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Domain'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=63, blank=True)),
            ('fqdn', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, blank=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('ctnr', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Ctnr'])),
            ('ip_str', self.gf('django.db.models.fields.CharField')(max_length=39)),
            ('ip_upper', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('ip_lower', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('ip_type', self.gf('django.db.models.fields.CharField')(default='4', max_length=1)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('cyder', ['AddressRecord'])

        # Adding unique constraint on 'AddressRecord', fields ['label', 'domain', 'fqdn', 'ip_upper', 'ip_lower', 'ip_type']
        db.create_unique('address_record', ['label', 'domain_id', 'fqdn', 'ip_upper', 'ip_lower', 'ip_type'])

        # Adding M2M table for field views on 'AddressRecord'
        m2m_table_name = db.shorten_name('address_record_views')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('addressrecord', models.ForeignKey(orm['cyder.addressrecord'], null=False)),
            ('view', models.ForeignKey(orm['cyder.view'], null=False))
        ))
        db.create_unique(m2m_table_name, ['addressrecord_id', 'view_id'])

        # Adding model 'PTR'
        db.create_table('ptr', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('ip_str', self.gf('django.db.models.fields.CharField')(max_length=39)),
            ('ip_upper', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('ip_lower', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('ip_type', self.gf('django.db.models.fields.CharField')(default='4', max_length=1)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reverse_domain', self.gf('django.db.models.fields.related.ForeignKey')(related_name='reverse_ptr_set', blank=True, to=orm['cyder.Domain'])),
            ('fqdn', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, blank=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('ctnr', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Ctnr'])),
        ))
        db.send_create_signal('cyder', ['PTR'])

        # Adding unique constraint on 'PTR', fields ['ip_str', 'ip_type', 'fqdn']
        db.create_unique('ptr', ['ip_str', 'ip_type', 'fqdn'])

        # Adding M2M table for field views on 'PTR'
        m2m_table_name = db.shorten_name('ptr_views')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ptr', models.ForeignKey(orm['cyder.ptr'], null=False)),
            ('view', models.ForeignKey(orm['cyder.view'], null=False))
        ))
        db.create_unique(m2m_table_name, ['ptr_id', 'view_id'])

        # Adding model 'StaticInterface'
        db.create_table('static_interface', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('expire', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Domain'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=63, blank=True)),
            ('fqdn', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, blank=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('ctnr', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Ctnr'])),
            ('ip_str', self.gf('django.db.models.fields.CharField')(max_length=39)),
            ('ip_upper', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('ip_lower', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('ip_type', self.gf('django.db.models.fields.CharField')(default='4', max_length=1)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mac', self.gf('cyder.base.fields.MacAddrField')(max_length=17, null=True, dhcp_enabled='dhcp_enabled')),
            ('reverse_domain', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='reverse_staticintr_set', null=True, to=orm['cyder.Domain'])),
            ('system', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.System'])),
            ('workgroup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Workgroup'], null=True, blank=True)),
            ('dhcp_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('dns_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('last_seen', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('cyder', ['StaticInterface'])

        # Adding unique constraint on 'StaticInterface', fields ['ip_upper', 'ip_lower']
        db.create_unique('static_interface', ['ip_upper', 'ip_lower'])

        # Adding unique constraint on 'StaticInterface', fields ['label', 'domain']
        db.create_unique('static_interface', ['label', 'domain_id'])

        # Adding M2M table for field views on 'StaticInterface'
        m2m_table_name = db.shorten_name('static_interface_views')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('staticinterface', models.ForeignKey(orm['cyder.staticinterface'], null=False)),
            ('view', models.ForeignKey(orm['cyder.view'], null=False))
        ))
        db.create_unique(m2m_table_name, ['staticinterface_id', 'view_id'])

        # Adding model 'StaticInterfaceAV'
        db.create_table('static_interface_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.StaticInterface'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['StaticInterfaceAV'])

        # Adding unique constraint on 'StaticInterfaceAV', fields ['entity', 'attribute']
        db.create_unique('static_interface_av', ['entity_id', 'attribute_id'])

        # Adding model 'Vlan'
        db.create_table('vlan', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('number', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('cyder', ['Vlan'])

        # Adding unique constraint on 'Vlan', fields ['name', 'number']
        db.create_unique('vlan', ['name', 'number'])

        # Adding model 'VlanAV'
        db.create_table('vlan_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Vlan'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['VlanAV'])

        # Adding unique constraint on 'VlanAV', fields ['entity', 'attribute']
        db.create_unique('vlan_av', ['entity_id', 'attribute_id'])

        # Adding model 'Vrf'
        db.create_table('vrf', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal('cyder', ['Vrf'])

        # Adding model 'VrfAV'
        db.create_table('vrf_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Vrf'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['VrfAV'])

        # Adding unique constraint on 'VrfAV', fields ['entity', 'attribute']
        db.create_unique('vrf_av', ['entity_id', 'attribute_id'])

        # Adding model 'Site'
        db.create_table('site', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Site'], null=True, blank=True)),
        ))
        db.send_create_signal('cyder', ['Site'])

        # Adding unique constraint on 'Site', fields ['name', 'parent']
        db.create_unique('site', ['name', 'parent_id'])

        # Adding model 'SiteAV'
        db.create_table('site_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Site'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['SiteAV'])

        # Adding unique constraint on 'SiteAV', fields ['entity', 'attribute']
        db.create_unique('site_av', ['entity_id', 'attribute_id'])

        # Adding model 'Network'
        db.create_table('network', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vlan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Vlan'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Site'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('vrf', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['cyder.Vrf'])),
            ('ip_type', self.gf('django.db.models.fields.CharField')(default='4', max_length=1)),
            ('ip_upper', self.gf('django.db.models.fields.BigIntegerField')(blank=True)),
            ('ip_lower', self.gf('django.db.models.fields.BigIntegerField')(blank=True)),
            ('network_str', self.gf('django.db.models.fields.CharField')(max_length=49)),
            ('prefixlen', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('dhcpd_raw_include', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('cyder', ['Network'])

        # Adding unique constraint on 'Network', fields ['ip_upper', 'ip_lower', 'prefixlen']
        db.create_unique('network', ['ip_upper', 'ip_lower', 'prefixlen'])

        # Adding model 'NetworkAV'
        db.create_table('network_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Network'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['NetworkAV'])

        # Adding unique constraint on 'NetworkAV', fields ['entity', 'attribute']
        db.create_unique('network_av', ['entity_id', 'attribute_id'])

        # Adding model 'Range'
        db.create_table('range', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('network', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Network'])),
            ('range_type', self.gf('django.db.models.fields.CharField')(default='st', max_length=2)),
            ('ip_type', self.gf('django.db.models.fields.CharField')(default='4', max_length=1)),
            ('start_upper', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('start_lower', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('start_str', self.gf('django.db.models.fields.CharField')(max_length=39)),
            ('end_lower', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('end_upper', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('end_str', self.gf('django.db.models.fields.CharField')(max_length=39)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Domain'], null=True, blank=True)),
            ('is_reserved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow', self.gf('django.db.models.fields.CharField')(default='l', max_length=1)),
            ('dhcpd_raw_include', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('dhcp_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('allow_voip_phones', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('range_usage', self.gf('django.db.models.fields.IntegerField')(max_length=3, null=True, blank=True)),
        ))
        db.send_create_signal('cyder', ['Range'])

        # Adding unique constraint on 'Range', fields ['start_upper', 'start_lower', 'end_upper', 'end_lower']
        db.create_unique('range', ['start_upper', 'start_lower', 'end_upper', 'end_lower'])

        # Adding M2M table for field views on 'Range'
        m2m_table_name = db.shorten_name('range_views')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('range', models.ForeignKey(orm['cyder.range'], null=False)),
            ('view', models.ForeignKey(orm['cyder.view'], null=False))
        ))
        db.create_unique(m2m_table_name, ['range_id', 'view_id'])

        # Adding model 'RangeAV'
        db.create_table('range_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Range'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['RangeAV'])

        # Adding unique constraint on 'RangeAV', fields ['entity', 'attribute']
        db.create_unique('range_av', ['entity_id', 'attribute_id'])

        # Adding model 'Ctnr'
        db.create_table('ctnr', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('email_contact', self.gf('django.db.models.fields.CharField')(max_length=75, blank=True)),
        ))
        db.send_create_signal('cyder', ['Ctnr'])

        # Adding M2M table for field domains on 'Ctnr'
        m2m_table_name = db.shorten_name('ctnr_domains')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ctnr', models.ForeignKey(orm['cyder.ctnr'], null=False)),
            ('domain', models.ForeignKey(orm['cyder.domain'], null=False))
        ))
        db.create_unique(m2m_table_name, ['ctnr_id', 'domain_id'])

        # Adding M2M table for field ranges on 'Ctnr'
        m2m_table_name = db.shorten_name('ctnr_ranges')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ctnr', models.ForeignKey(orm['cyder.ctnr'], null=False)),
            ('range', models.ForeignKey(orm['cyder.range'], null=False))
        ))
        db.create_unique(m2m_table_name, ['ctnr_id', 'range_id'])

        # Adding M2M table for field workgroups on 'Ctnr'
        m2m_table_name = db.shorten_name('ctnr_workgroups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ctnr', models.ForeignKey(orm['cyder.ctnr'], null=False)),
            ('workgroup', models.ForeignKey(orm['cyder.workgroup'], null=False))
        ))
        db.create_unique(m2m_table_name, ['ctnr_id', 'workgroup_id'])

        # Adding model 'CtnrUser'
        db.create_table('ctnr_users', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('ctnr', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Ctnr'])),
            ('level', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('cyder', ['CtnrUser'])

        # Adding unique constraint on 'CtnrUser', fields ['ctnr', 'user']
        db.create_unique('ctnr_users', ['ctnr_id', 'user_id'])

        # Adding model 'UserProfile'
        db.create_table('auth_user_profile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='profile', unique=True, to=orm['auth.User'])),
            ('default_ctnr', self.gf('django.db.models.fields.related.ForeignKey')(default=2, to=orm['cyder.Ctnr'])),
            ('phone_number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('cyder', ['UserProfile'])

        # Adding model 'Task'
        db.create_table(u'task', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ttype', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('cyder', ['Task'])

        # Adding model 'DynamicInterface'
        db.create_table('dynamic_interface', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('expire', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('ctnr', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Ctnr'])),
            ('workgroup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Workgroup'], null=True, blank=True)),
            ('system', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.System'])),
            ('mac', self.gf('cyder.base.fields.MacAddrField')(max_length=17, null=True, dhcp_enabled='dhcp_enabled')),
            ('range', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Range'])),
            ('dhcp_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('last_seen', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('cyder', ['DynamicInterface'])

        # Adding unique constraint on 'DynamicInterface', fields ['range', 'mac']
        db.create_unique('dynamic_interface', ['range_id', 'mac'])

        # Adding model 'DynamicInterfaceAV'
        db.create_table('dynamic_interface_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.DynamicInterface'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['DynamicInterfaceAV'])

        # Adding unique constraint on 'DynamicInterfaceAV', fields ['entity', 'attribute']
        db.create_unique('dynamic_interface_av', ['entity_id', 'attribute_id'])

        # Adding model 'DNSBuildRun'
        db.create_table('cyder_dnsbuildrun', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('log', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('cyder', ['DNSBuildRun'])

        # Adding model 'BuildManifest'
        db.create_table('cyder_buildmanifest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zname', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('files', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('zhash', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('build_run', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.DNSBuildRun'])),
        ))
        db.send_create_signal('cyder', ['BuildManifest'])

        # Adding model 'MX'
        db.create_table('mx', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Domain'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=63, blank=True)),
            ('fqdn', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, blank=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('ctnr', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Ctnr'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('server', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('priority', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('cyder', ['MX'])

        # Adding unique constraint on 'MX', fields ['domain', 'label', 'server']
        db.create_unique('mx', ['domain_id', 'label', 'server'])

        # Adding M2M table for field views on 'MX'
        m2m_table_name = db.shorten_name('mx_views')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mx', models.ForeignKey(orm['cyder.mx'], null=False)),
            ('view', models.ForeignKey(orm['cyder.view'], null=False))
        ))
        db.create_unique(m2m_table_name, ['mx_id', 'view_id'])

        # Adding model 'Nameserver'
        db.create_table('nameserver', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('ctnr', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Ctnr'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Domain'])),
            ('server', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('addr_glue', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='nameserver_set', null=True, to=orm['cyder.AddressRecord'])),
            ('intr_glue', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='nameserver_set', null=True, to=orm['cyder.StaticInterface'])),
        ))
        db.send_create_signal('cyder', ['Nameserver'])

        # Adding unique constraint on 'Nameserver', fields ['domain', 'server']
        db.create_unique('nameserver', ['domain_id', 'server'])

        # Adding M2M table for field views on 'Nameserver'
        m2m_table_name = db.shorten_name('nameserver_views')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('nameserver', models.ForeignKey(orm['cyder.nameserver'], null=False)),
            ('view', models.ForeignKey(orm['cyder.view'], null=False))
        ))
        db.create_unique(m2m_table_name, ['nameserver_id', 'view_id'])

        # Adding model 'SOA'
        db.create_table('soa', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('primary', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('contact', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('serial', self.gf('django.db.models.fields.PositiveIntegerField')(default=1420739755)),
            ('expire', self.gf('django.db.models.fields.PositiveIntegerField')(default=1209600)),
            ('retry', self.gf('django.db.models.fields.PositiveIntegerField')(default=86400)),
            ('refresh', self.gf('django.db.models.fields.PositiveIntegerField')(default=180)),
            ('minimum', self.gf('django.db.models.fields.PositiveIntegerField')(default=180)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('root_domain', self.gf('django.db.models.fields.related.ForeignKey')(related_name='root_of_soa', unique=True, to=orm['cyder.Domain'])),
            ('dirty', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_signed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('dns_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('cyder', ['SOA'])

        # Adding model 'SOAAV'
        db.create_table('soa_av', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('value', self.gf('cyder.base.eav.fields.EAVValueField')(attribute_field='', max_length=255)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.SOA'])),
            ('attribute', self.gf('cyder.base.eav.fields.EAVAttributeField')(to=orm['cyder.Attribute'])),
        ))
        db.send_create_signal('cyder', ['SOAAV'])

        # Adding unique constraint on 'SOAAV', fields ['entity', 'attribute']
        db.create_unique('soa_av', ['entity_id', 'attribute_id'])

        # Adding model 'SRV'
        db.create_table('srv', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('ctnr', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Ctnr'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=63, blank=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Domain'])),
            ('fqdn', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('target', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('port', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('priority', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('weight', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('cyder', ['SRV'])

        # Adding unique constraint on 'SRV', fields ['label', 'domain', 'target', 'port']
        db.create_unique('srv', ['label', 'domain_id', 'target', 'port'])

        # Adding M2M table for field views on 'SRV'
        m2m_table_name = db.shorten_name('srv_views')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('srv', models.ForeignKey(orm['cyder.srv'], null=False)),
            ('view', models.ForeignKey(orm['cyder.view'], null=False))
        ))
        db.create_unique(m2m_table_name, ['srv_id', 'view_id'])

        # Adding model 'SSHFP'
        db.create_table('sshfp', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Domain'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=63, blank=True)),
            ('fqdn', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, blank=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('ctnr', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Ctnr'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('algorithm_number', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('fingerprint_type', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal('cyder', ['SSHFP'])

        # Adding unique constraint on 'SSHFP', fields ['domain', 'label']
        db.create_unique('sshfp', ['domain_id', 'label'])

        # Adding M2M table for field views on 'SSHFP'
        m2m_table_name = db.shorten_name('sshfp_views')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sshfp', models.ForeignKey(orm['cyder.sshfp'], null=False)),
            ('view', models.ForeignKey(orm['cyder.view'], null=False))
        ))
        db.create_unique(m2m_table_name, ['sshfp_id', 'view_id'])

        # Adding model 'TXT'
        db.create_table('txt', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Domain'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=63, blank=True)),
            ('fqdn', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, blank=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('ctnr', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Ctnr'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('txt_data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('cyder', ['TXT'])

        # Adding M2M table for field views on 'TXT'
        m2m_table_name = db.shorten_name('txt_views')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('txt', models.ForeignKey(orm['cyder.txt'], null=False)),
            ('view', models.ForeignKey(orm['cyder.view'], null=False))
        ))
        db.create_unique(m2m_table_name, ['txt_id', 'view_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'SSHFP', fields ['domain', 'label']
        db.delete_unique('sshfp', ['domain_id', 'label'])

        # Removing unique constraint on 'SRV', fields ['label', 'domain', 'target', 'port']
        db.delete_unique('srv', ['label', 'domain_id', 'target', 'port'])

        # Removing unique constraint on 'SOAAV', fields ['entity', 'attribute']
        db.delete_unique('soa_av', ['entity_id', 'attribute_id'])

        # Removing unique constraint on 'Nameserver', fields ['domain', 'server']
        db.delete_unique('nameserver', ['domain_id', 'server'])

        # Removing unique constraint on 'MX', fields ['domain', 'label', 'server']
        db.delete_unique('mx', ['domain_id', 'label', 'server'])

        # Removing unique constraint on 'DynamicInterfaceAV', fields ['entity', 'attribute']
        db.delete_unique('dynamic_interface_av', ['entity_id', 'attribute_id'])

        # Removing unique constraint on 'DynamicInterface', fields ['range', 'mac']
        db.delete_unique('dynamic_interface', ['range_id', 'mac'])

        # Removing unique constraint on 'CtnrUser', fields ['ctnr', 'user']
        db.delete_unique('ctnr_users', ['ctnr_id', 'user_id'])

        # Removing unique constraint on 'RangeAV', fields ['entity', 'attribute']
        db.delete_unique('range_av', ['entity_id', 'attribute_id'])

        # Removing unique constraint on 'Range', fields ['start_upper', 'start_lower', 'end_upper', 'end_lower']
        db.delete_unique('range', ['start_upper', 'start_lower', 'end_upper', 'end_lower'])

        # Removing unique constraint on 'NetworkAV', fields ['entity', 'attribute']
        db.delete_unique('network_av', ['entity_id', 'attribute_id'])

        # Removing unique constraint on 'Network', fields ['ip_upper', 'ip_lower', 'prefixlen']
        db.delete_unique('network', ['ip_upper', 'ip_lower', 'prefixlen'])

        # Removing unique constraint on 'SiteAV', fields ['entity', 'attribute']
        db.delete_unique('site_av', ['entity_id', 'attribute_id'])

        # Removing unique constraint on 'Site', fields ['name', 'parent']
        db.delete_unique('site', ['name', 'parent_id'])

        # Removing unique constraint on 'VrfAV', fields ['entity', 'attribute']
        db.delete_unique('vrf_av', ['entity_id', 'attribute_id'])

        # Removing unique constraint on 'VlanAV', fields ['entity', 'attribute']
        db.delete_unique('vlan_av', ['entity_id', 'attribute_id'])

        # Removing unique constraint on 'Vlan', fields ['name', 'number']
        db.delete_unique('vlan', ['name', 'number'])

        # Removing unique constraint on 'StaticInterfaceAV', fields ['entity', 'attribute']
        db.delete_unique('static_interface_av', ['entity_id', 'attribute_id'])

        # Removing unique constraint on 'StaticInterface', fields ['label', 'domain']
        db.delete_unique('static_interface', ['label', 'domain_id'])

        # Removing unique constraint on 'StaticInterface', fields ['ip_upper', 'ip_lower']
        db.delete_unique('static_interface', ['ip_upper', 'ip_lower'])

        # Removing unique constraint on 'PTR', fields ['ip_str', 'ip_type', 'fqdn']
        db.delete_unique('ptr', ['ip_str', 'ip_type', 'fqdn'])

        # Removing unique constraint on 'AddressRecord', fields ['label', 'domain', 'fqdn', 'ip_upper', 'ip_lower', 'ip_type']
        db.delete_unique('address_record', ['label', 'domain_id', 'fqdn', 'ip_upper', 'ip_lower', 'ip_type'])

        # Removing unique constraint on 'CNAME', fields ['label', 'domain', 'target']
        db.delete_unique('cname', ['label', 'domain_id', 'target'])

        # Removing unique constraint on 'View', fields ['name']
        db.delete_unique('view', ['name'])

        # Removing unique constraint on 'WorkgroupAV', fields ['entity', 'attribute']
        db.delete_unique('workgroup_av', ['entity_id', 'attribute_id'])

        # Removing unique constraint on 'SystemAV', fields ['entity', 'attribute']
        db.delete_unique('system_av', ['entity_id', 'attribute_id'])

        # Deleting model 'Token'
        db.delete_table('cyder_token')

        # Deleting model 'Attribute'
        db.delete_table('attribute')

        # Deleting model 'Domain'
        db.delete_table('domain')

        # Deleting model 'System'
        db.delete_table('system')

        # Deleting model 'SystemAV'
        db.delete_table('system_av')

        # Deleting model 'Workgroup'
        db.delete_table('workgroup')

        # Deleting model 'WorkgroupAV'
        db.delete_table('workgroup_av')

        # Deleting model 'View'
        db.delete_table('view')

        # Deleting model 'CNAME'
        db.delete_table('cname')

        # Removing M2M table for field views on 'CNAME'
        db.delete_table(db.shorten_name('cname_views'))

        # Deleting model 'AddressRecord'
        db.delete_table('address_record')

        # Removing M2M table for field views on 'AddressRecord'
        db.delete_table(db.shorten_name('address_record_views'))

        # Deleting model 'PTR'
        db.delete_table('ptr')

        # Removing M2M table for field views on 'PTR'
        db.delete_table(db.shorten_name('ptr_views'))

        # Deleting model 'StaticInterface'
        db.delete_table('static_interface')

        # Removing M2M table for field views on 'StaticInterface'
        db.delete_table(db.shorten_name('static_interface_views'))

        # Deleting model 'StaticInterfaceAV'
        db.delete_table('static_interface_av')

        # Deleting model 'Vlan'
        db.delete_table('vlan')

        # Deleting model 'VlanAV'
        db.delete_table('vlan_av')

        # Deleting model 'Vrf'
        db.delete_table('vrf')

        # Deleting model 'VrfAV'
        db.delete_table('vrf_av')

        # Deleting model 'Site'
        db.delete_table('site')

        # Deleting model 'SiteAV'
        db.delete_table('site_av')

        # Deleting model 'Network'
        db.delete_table('network')

        # Deleting model 'NetworkAV'
        db.delete_table('network_av')

        # Deleting model 'Range'
        db.delete_table('range')

        # Removing M2M table for field views on 'Range'
        db.delete_table(db.shorten_name('range_views'))

        # Deleting model 'RangeAV'
        db.delete_table('range_av')

        # Deleting model 'Ctnr'
        db.delete_table('ctnr')

        # Removing M2M table for field domains on 'Ctnr'
        db.delete_table(db.shorten_name('ctnr_domains'))

        # Removing M2M table for field ranges on 'Ctnr'
        db.delete_table(db.shorten_name('ctnr_ranges'))

        # Removing M2M table for field workgroups on 'Ctnr'
        db.delete_table(db.shorten_name('ctnr_workgroups'))

        # Deleting model 'CtnrUser'
        db.delete_table('ctnr_users')

        # Deleting model 'UserProfile'
        db.delete_table('auth_user_profile')

        # Deleting model 'Task'
        db.delete_table(u'task')

        # Deleting model 'DynamicInterface'
        db.delete_table('dynamic_interface')

        # Deleting model 'DynamicInterfaceAV'
        db.delete_table('dynamic_interface_av')

        # Deleting model 'DNSBuildRun'
        db.delete_table('cyder_dnsbuildrun')

        # Deleting model 'BuildManifest'
        db.delete_table('cyder_buildmanifest')

        # Deleting model 'MX'
        db.delete_table('mx')

        # Removing M2M table for field views on 'MX'
        db.delete_table(db.shorten_name('mx_views'))

        # Deleting model 'Nameserver'
        db.delete_table('nameserver')

        # Removing M2M table for field views on 'Nameserver'
        db.delete_table(db.shorten_name('nameserver_views'))

        # Deleting model 'SOA'
        db.delete_table('soa')

        # Deleting model 'SOAAV'
        db.delete_table('soa_av')

        # Deleting model 'SRV'
        db.delete_table('srv')

        # Removing M2M table for field views on 'SRV'
        db.delete_table(db.shorten_name('srv_views'))

        # Deleting model 'SSHFP'
        db.delete_table('sshfp')

        # Removing M2M table for field views on 'SSHFP'
        db.delete_table(db.shorten_name('sshfp_views'))

        # Deleting model 'TXT'
        db.delete_table('txt')

        # Removing M2M table for field views on 'TXT'
        db.delete_table(db.shorten_name('txt_views'))


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
            'ctnr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Ctnr']"}),
            'dhcp_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'expire': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'mac': ('cyder.base.fields.MacAddrField', [], {'max_length': '17', 'null': 'True', 'dhcp_enabled': "'dhcp_enabled'"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'range': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Range']"}),
            'system': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.System']"}),
            'workgroup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Workgroup']", 'null': 'True', 'blank': 'True'})
        },
        'cyder.dynamicinterfaceav': {
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'DynamicInterfaceAV', 'db_table': "'dynamic_interface_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.DynamicInterface']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "''", 'max_length': '255'})
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
            'ctnr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Ctnr']"}),
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
            'vrf': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['cyder.Vrf']"})
        },
        'cyder.networkav': {
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'NetworkAV', 'db_table': "'network_av'"},
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
            'allow_voip_phones': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'RangeAV', 'db_table': "'range_av'"},
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
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'SiteAV', 'db_table': "'site_av'"},
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
            'serial': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1420739755'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'})
        },
        'cyder.soaav': {
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'SOAAV', 'db_table': "'soa_av'"},
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
            'ctnr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Ctnr']"}),
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
            'workgroup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Workgroup']", 'null': 'True', 'blank': 'True'})
        },
        'cyder.staticinterfaceav': {
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'StaticInterfaceAV', 'db_table': "'static_interface_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.StaticInterface']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
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
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'VlanAV', 'db_table': "'vlan_av'"},
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
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'VrfAV', 'db_table': "'vrf_av'"},
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
            'Meta': {'unique_together': "(('entity', 'attribute'),)", 'object_name': 'WorkgroupAV', 'db_table': "'workgroup_av'"},
            'attribute': ('cyder.base.eav.fields.EAVAttributeField', [], {'to': "orm['cyder.Attribute']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Workgroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'value': ('cyder.base.eav.fields.EAVValueField', [], {'attribute_field': "''", 'max_length': '255'})
        }
    }

    complete_apps = ['cyder']