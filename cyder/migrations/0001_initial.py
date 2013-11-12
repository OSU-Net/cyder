# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Task'
        db.create_table(u'task', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ttype', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('cyder', ['Task'])

        # Adding model 'SOA'
        db.create_table('soa', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('primary', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('contact', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('serial', self.gf('django.db.models.fields.PositiveIntegerField')(default=1383209914)),
            ('expire', self.gf('django.db.models.fields.PositiveIntegerField')(default=1209600)),
            ('retry', self.gf('django.db.models.fields.PositiveIntegerField')(default=86400)),
            ('refresh', self.gf('django.db.models.fields.PositiveIntegerField')(default=180)),
            ('minimum', self.gf('django.db.models.fields.PositiveIntegerField')(default=180)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('dirty', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_signed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('cyder', ['SOA'])

        # Adding unique constraint on 'SOA', fields ['primary', 'contact', 'description']
        db.create_unique('soa', ['primary', 'contact', 'description'])

        # Adding model 'SOAKeyValue'
        db.create_table('soa_kv', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('soa', self.gf('django.db.models.fields.related.ForeignKey')(related_name='keyvalue_set', to=orm['cyder.SOA'])),
        ))
        db.send_create_signal('cyder', ['SOAKeyValue'])

        # Adding model 'Domain'
        db.create_table('domain', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('master_domain', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['cyder.Domain'], null=True, blank=True)),
            ('soa', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['cyder.SOA'], null=True, blank=True)),
            ('is_reverse', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('dirty', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('purgeable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('delegated', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('cyder', ['Domain'])

        # Adding model 'View'
        db.create_table('view', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('cyder', ['View'])

        # Adding unique constraint on 'View', fields ['name']
        db.create_unique('view', ['name'])

        # Adding model 'SSHFP'
        db.create_table('sshfp', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Domain'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=63, blank=True)),
            ('fqdn', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, blank=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('algorithm_number', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('fingerprint_type', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('cyder', ['SSHFP'])

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

        # Adding model 'CNAME'
        db.create_table('cname', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Domain'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=63, blank=True)),
            ('fqdn', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, blank=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('target', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('cyder', ['CNAME'])

        # Adding unique constraint on 'CNAME', fields ['domain', 'label', 'target']
        db.create_unique('cname', ['domain_id', 'label', 'target'])

        # Adding M2M table for field views on 'CNAME'
        m2m_table_name = db.shorten_name('cname_views')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cname', models.ForeignKey(orm['cyder.cname'], null=False)),
            ('view', models.ForeignKey(orm['cyder.view'], null=False))
        ))
        db.create_unique(m2m_table_name, ['cname_id', 'view_id'])

        # Adding model 'MX'
        db.create_table('mx', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Domain'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=63, blank=True)),
            ('fqdn', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, blank=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('server', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('priority', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('cyder', ['MX'])

        # Adding unique constraint on 'MX', fields ['domain', 'label', 'server', 'priority']
        db.create_unique('mx', ['domain_id', 'label', 'server', 'priority'])

        # Adding M2M table for field views on 'MX'
        m2m_table_name = db.shorten_name('mx_views')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mx', models.ForeignKey(orm['cyder.mx'], null=False)),
            ('view', models.ForeignKey(orm['cyder.view'], null=False))
        ))
        db.create_unique(m2m_table_name, ['mx_id', 'view_id'])

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

        # Adding model 'System'
        db.create_table('system', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('cyder', ['System'])

        # Adding model 'SystemKeyValue'
        db.create_table('system_kv', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('system', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.System'])),
        ))
        db.send_create_signal('cyder', ['SystemKeyValue'])

        # Adding unique constraint on 'SystemKeyValue', fields ['key', 'value', 'system']
        db.create_unique('system_kv', ['key', 'value', 'system_id'])

        # Adding model 'AddressRecord'
        db.create_table('address_record', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Domain'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=63, blank=True)),
            ('fqdn', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, blank=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
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
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Domain'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=63, blank=True)),
            ('fqdn', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, blank=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('ip_str', self.gf('django.db.models.fields.CharField')(max_length=39)),
            ('ip_upper', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('ip_lower', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('ip_type', self.gf('django.db.models.fields.CharField')(default='4', max_length=1)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reverse_domain', self.gf('django.db.models.fields.related.ForeignKey')(related_name='reverse_ptr_set', blank=True, to=orm['cyder.Domain'])),
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

        # Adding model 'Workgroup'
        db.create_table('workgroup', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal('cyder', ['Workgroup'])

        # Adding model 'WorkgroupKeyValue'
        db.create_table('workgroup_kv', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_option', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_statement', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_validator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('workgroup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Workgroup'])),
        ))
        db.send_create_signal('cyder', ['WorkgroupKeyValue'])

        # Adding unique constraint on 'WorkgroupKeyValue', fields ['key', 'value', 'workgroup']
        db.create_unique('workgroup_kv', ['key', 'value', 'workgroup_id'])

        # Adding model 'StaticInterface'
        db.create_table('static_interface', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Domain'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=63, blank=True)),
            ('fqdn', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, blank=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('ip_str', self.gf('django.db.models.fields.CharField')(max_length=39)),
            ('ip_upper', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('ip_lower', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('ip_type', self.gf('django.db.models.fields.CharField')(default='4', max_length=1)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ctnr', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Ctnr'])),
            ('mac', self.gf('cyder.core.fields.MacAddrField')(blank=True, max_length=17, dhcp_enabled='dhcp_enabled')),
            ('reverse_domain', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='reverse_staticintr_set', null=True, to=orm['cyder.Domain'])),
            ('system', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.System'])),
            ('workgroup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Workgroup'], null=True, blank=True)),
            ('dhcp_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('dns_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('last_seen', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, max_length=11, blank=True)),
        ))
        db.send_create_signal('cyder', ['StaticInterface'])

        # Adding unique constraint on 'StaticInterface', fields ['ip_upper', 'ip_lower', 'label', 'domain', 'mac']
        db.create_unique('static_interface', ['ip_upper', 'ip_lower', 'label', 'domain_id', 'mac'])

        # Adding M2M table for field views on 'StaticInterface'
        m2m_table_name = db.shorten_name('static_interface_views')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('staticinterface', models.ForeignKey(orm['cyder.staticinterface'], null=False)),
            ('view', models.ForeignKey(orm['cyder.view'], null=False))
        ))
        db.create_unique(m2m_table_name, ['staticinterface_id', 'view_id'])

        # Adding model 'StaticIntrKeyValue'
        db.create_table('static_interface_kv', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_option', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_statement', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_validator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('static_interface', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.StaticInterface'])),
        ))
        db.send_create_signal('cyder', ['StaticIntrKeyValue'])

        # Adding unique constraint on 'StaticIntrKeyValue', fields ['key', 'value', 'static_interface']
        db.create_unique('static_interface_kv', ['key', 'value', 'static_interface_id'])

        # Adding model 'Nameserver'
        db.create_table('nameserver', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
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

        # Adding model 'SRV'
        db.create_table('srv', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=3600, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
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

        # Adding model 'SiteKeyValue'
        db.create_table('site_kv', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Site'])),
        ))
        db.send_create_signal('cyder', ['SiteKeyValue'])

        # Adding unique constraint on 'SiteKeyValue', fields ['key', 'value']
        db.create_unique('site_kv', ['key', 'value'])

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

        # Adding model 'VlanKeyValue'
        db.create_table('vlan_kv', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('vlan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Vlan'])),
        ))
        db.send_create_signal('cyder', ['VlanKeyValue'])

        # Adding unique constraint on 'VlanKeyValue', fields ['key', 'value']
        db.create_unique('vlan_kv', ['key', 'value'])

        # Adding model 'Network'
        db.create_table('network', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vlan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Vlan'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Site'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('vrf', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Vrf'], null=True, blank=True)),
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

        # Adding model 'NetworkKeyValue'
        db.create_table('network_kv', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_option', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_statement', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_validator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('network', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Network'])),
        ))
        db.send_create_signal('cyder', ['NetworkKeyValue'])

        # Adding unique constraint on 'NetworkKeyValue', fields ['key', 'value', 'network']
        db.create_unique('network_kv', ['key', 'value', 'network_id'])

        # Adding model 'Vrf'
        db.create_table('vrf', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal('cyder', ['Vrf'])

        # Adding model 'VrfKeyValue'
        db.create_table('vrf_kv', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('vrf', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Vrf'])),
        ))
        db.send_create_signal('cyder', ['VrfKeyValue'])

        # Adding model 'Range'
        db.create_table('range', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('network', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Network'], null=True, blank=True)),
            ('range_type', self.gf('django.db.models.fields.CharField')(default='st', max_length=2)),
            ('ip_type', self.gf('django.db.models.fields.CharField')(default='4', max_length=1)),
            ('start_upper', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('start_lower', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('start_str', self.gf('django.db.models.fields.CharField')(max_length=39)),
            ('end_lower', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('end_upper', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('end_str', self.gf('django.db.models.fields.CharField')(max_length=39)),
            ('is_reserved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow', self.gf('django.db.models.fields.CharField')(default='l', max_length=1)),
            ('dhcpd_raw_include', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('dhcp_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('cyder', ['Range'])

        # Adding unique constraint on 'Range', fields ['start_upper', 'start_lower', 'end_upper', 'end_lower']
        db.create_unique('range', ['start_upper', 'start_lower', 'end_upper', 'end_lower'])

        # Adding model 'RangeKeyValue'
        db.create_table('range_kv', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_option', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_statement', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_validator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('range', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Range'])),
        ))
        db.send_create_signal('cyder', ['RangeKeyValue'])

        # Adding unique constraint on 'RangeKeyValue', fields ['key', 'value', 'range']
        db.create_unique('range_kv', ['key', 'value', 'range_id'])

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

        # Adding model 'DynamicInterface'
        db.create_table('dynamic_interface', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('ctnr', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Ctnr'])),
            ('workgroup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Workgroup'], null=True, blank=True)),
            ('system', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.System'])),
            ('mac', self.gf('cyder.core.fields.MacAddrField')(blank=True, max_length=17, dhcp_enabled='dhcp_enabled')),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Domain'], null=True)),
            ('range', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.Range'])),
            ('dhcp_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('last_seen', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, max_length=11, blank=True)),
        ))
        db.send_create_signal('cyder', ['DynamicInterface'])

        # Adding model 'DynamicIntrKeyValue'
        db.create_table('dynamic_interface_kv', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_quoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_option', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_statement', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_validator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('dynamic_interface', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyder.DynamicInterface'])),
        ))
        db.send_create_signal('cyder', ['DynamicIntrKeyValue'])

        # Adding unique constraint on 'DynamicIntrKeyValue', fields ['key', 'value', 'dynamic_interface']
        db.create_unique('dynamic_interface_kv', ['key', 'value', 'dynamic_interface_id'])

        # Adding model 'UserProfile'
        db.create_table('auth_user_profile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='profile', unique=True, to=orm['auth.User'])),
            ('default_ctnr', self.gf('django.db.models.fields.related.ForeignKey')(default=2, to=orm['cyder.Ctnr'])),
            ('phone_number', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('cyder', ['UserProfile'])

        # Adding model 'Token'
        db.create_table('cyder_token', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('purpose', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('cyder', ['Token'])


    def backwards(self, orm):
        # Removing unique constraint on 'DynamicIntrKeyValue', fields ['key', 'value', 'dynamic_interface']
        db.delete_unique('dynamic_interface_kv', ['key', 'value', 'dynamic_interface_id'])

        # Removing unique constraint on 'CtnrUser', fields ['ctnr', 'user']
        db.delete_unique('ctnr_users', ['ctnr_id', 'user_id'])

        # Removing unique constraint on 'RangeKeyValue', fields ['key', 'value', 'range']
        db.delete_unique('range_kv', ['key', 'value', 'range_id'])

        # Removing unique constraint on 'Range', fields ['start_upper', 'start_lower', 'end_upper', 'end_lower']
        db.delete_unique('range', ['start_upper', 'start_lower', 'end_upper', 'end_lower'])

        # Removing unique constraint on 'NetworkKeyValue', fields ['key', 'value', 'network']
        db.delete_unique('network_kv', ['key', 'value', 'network_id'])

        # Removing unique constraint on 'Network', fields ['ip_upper', 'ip_lower', 'prefixlen']
        db.delete_unique('network', ['ip_upper', 'ip_lower', 'prefixlen'])

        # Removing unique constraint on 'VlanKeyValue', fields ['key', 'value']
        db.delete_unique('vlan_kv', ['key', 'value'])

        # Removing unique constraint on 'Vlan', fields ['name', 'number']
        db.delete_unique('vlan', ['name', 'number'])

        # Removing unique constraint on 'SiteKeyValue', fields ['key', 'value']
        db.delete_unique('site_kv', ['key', 'value'])

        # Removing unique constraint on 'Site', fields ['name', 'parent']
        db.delete_unique('site', ['name', 'parent_id'])

        # Removing unique constraint on 'SRV', fields ['label', 'domain', 'target', 'port']
        db.delete_unique('srv', ['label', 'domain_id', 'target', 'port'])

        # Removing unique constraint on 'Nameserver', fields ['domain', 'server']
        db.delete_unique('nameserver', ['domain_id', 'server'])

        # Removing unique constraint on 'StaticIntrKeyValue', fields ['key', 'value', 'static_interface']
        db.delete_unique('static_interface_kv', ['key', 'value', 'static_interface_id'])

        # Removing unique constraint on 'StaticInterface', fields ['ip_upper', 'ip_lower', 'label', 'domain', 'mac']
        db.delete_unique('static_interface', ['ip_upper', 'ip_lower', 'label', 'domain_id', 'mac'])

        # Removing unique constraint on 'WorkgroupKeyValue', fields ['key', 'value', 'workgroup']
        db.delete_unique('workgroup_kv', ['key', 'value', 'workgroup_id'])

        # Removing unique constraint on 'PTR', fields ['ip_str', 'ip_type', 'fqdn']
        db.delete_unique('ptr', ['ip_str', 'ip_type', 'fqdn'])

        # Removing unique constraint on 'AddressRecord', fields ['label', 'domain', 'fqdn', 'ip_upper', 'ip_lower', 'ip_type']
        db.delete_unique('address_record', ['label', 'domain_id', 'fqdn', 'ip_upper', 'ip_lower', 'ip_type'])

        # Removing unique constraint on 'SystemKeyValue', fields ['key', 'value', 'system']
        db.delete_unique('system_kv', ['key', 'value', 'system_id'])

        # Removing unique constraint on 'MX', fields ['domain', 'label', 'server', 'priority']
        db.delete_unique('mx', ['domain_id', 'label', 'server', 'priority'])

        # Removing unique constraint on 'CNAME', fields ['domain', 'label', 'target']
        db.delete_unique('cname', ['domain_id', 'label', 'target'])

        # Removing unique constraint on 'View', fields ['name']
        db.delete_unique('view', ['name'])

        # Removing unique constraint on 'SOA', fields ['primary', 'contact', 'description']
        db.delete_unique('soa', ['primary', 'contact', 'description'])

        # Deleting model 'Task'
        db.delete_table(u'task')

        # Deleting model 'SOA'
        db.delete_table('soa')

        # Deleting model 'SOAKeyValue'
        db.delete_table('soa_kv')

        # Deleting model 'Domain'
        db.delete_table('domain')

        # Deleting model 'View'
        db.delete_table('view')

        # Deleting model 'SSHFP'
        db.delete_table('sshfp')

        # Removing M2M table for field views on 'SSHFP'
        db.delete_table(db.shorten_name('sshfp_views'))

        # Deleting model 'TXT'
        db.delete_table('txt')

        # Removing M2M table for field views on 'TXT'
        db.delete_table(db.shorten_name('txt_views'))

        # Deleting model 'CNAME'
        db.delete_table('cname')

        # Removing M2M table for field views on 'CNAME'
        db.delete_table(db.shorten_name('cname_views'))

        # Deleting model 'MX'
        db.delete_table('mx')

        # Removing M2M table for field views on 'MX'
        db.delete_table(db.shorten_name('mx_views'))

        # Deleting model 'DNSBuildRun'
        db.delete_table('cyder_dnsbuildrun')

        # Deleting model 'BuildManifest'
        db.delete_table('cyder_buildmanifest')

        # Deleting model 'System'
        db.delete_table('system')

        # Deleting model 'SystemKeyValue'
        db.delete_table('system_kv')

        # Deleting model 'AddressRecord'
        db.delete_table('address_record')

        # Removing M2M table for field views on 'AddressRecord'
        db.delete_table(db.shorten_name('address_record_views'))

        # Deleting model 'PTR'
        db.delete_table('ptr')

        # Removing M2M table for field views on 'PTR'
        db.delete_table(db.shorten_name('ptr_views'))

        # Deleting model 'Workgroup'
        db.delete_table('workgroup')

        # Deleting model 'WorkgroupKeyValue'
        db.delete_table('workgroup_kv')

        # Deleting model 'StaticInterface'
        db.delete_table('static_interface')

        # Removing M2M table for field views on 'StaticInterface'
        db.delete_table(db.shorten_name('static_interface_views'))

        # Deleting model 'StaticIntrKeyValue'
        db.delete_table('static_interface_kv')

        # Deleting model 'Nameserver'
        db.delete_table('nameserver')

        # Removing M2M table for field views on 'Nameserver'
        db.delete_table(db.shorten_name('nameserver_views'))

        # Deleting model 'SRV'
        db.delete_table('srv')

        # Removing M2M table for field views on 'SRV'
        db.delete_table(db.shorten_name('srv_views'))

        # Deleting model 'Site'
        db.delete_table('site')

        # Deleting model 'SiteKeyValue'
        db.delete_table('site_kv')

        # Deleting model 'Vlan'
        db.delete_table('vlan')

        # Deleting model 'VlanKeyValue'
        db.delete_table('vlan_kv')

        # Deleting model 'Network'
        db.delete_table('network')

        # Deleting model 'NetworkKeyValue'
        db.delete_table('network_kv')

        # Deleting model 'Vrf'
        db.delete_table('vrf')

        # Deleting model 'VrfKeyValue'
        db.delete_table('vrf_kv')

        # Deleting model 'Range'
        db.delete_table('range')

        # Deleting model 'RangeKeyValue'
        db.delete_table('range_kv')

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

        # Deleting model 'DynamicInterface'
        db.delete_table('dynamic_interface')

        # Deleting model 'DynamicIntrKeyValue'
        db.delete_table('dynamic_interface_kv')

        # Deleting model 'UserProfile'
        db.delete_table('auth_user_profile')

        # Deleting model 'Token'
        db.delete_table('cyder_token')


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
        'cyder.dynamicintrkeyvalue': {
            'Meta': {'unique_together': "(('key', 'value', 'dynamic_interface'),)", 'object_name': 'DynamicIntrKeyValue', 'db_table': "'dynamic_interface_kv'"},
            'dynamic_interface': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.DynamicInterface']"}),
            'has_validator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_option': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_quoted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_statement': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
        'cyder.networkkeyvalue': {
            'Meta': {'unique_together': "(('key', 'value', 'network'),)", 'object_name': 'NetworkKeyValue', 'db_table': "'network_kv'"},
            'has_validator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_option': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_quoted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_statement': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'network': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Network']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
        'cyder.rangekeyvalue': {
            'Meta': {'unique_together': "(('key', 'value', 'range'),)", 'object_name': 'RangeKeyValue', 'db_table': "'range_kv'"},
            'has_validator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_option': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_quoted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_statement': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'range': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Range']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'cyder.site': {
            'Meta': {'unique_together': "(('name', 'parent'),)", 'object_name': 'Site', 'db_table': "'site'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Site']", 'null': 'True', 'blank': 'True'})
        },
        'cyder.sitekeyvalue': {
            'Meta': {'unique_together': "(('key', 'value'),)", 'object_name': 'SiteKeyValue', 'db_table': "'site_kv'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_quoted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Site']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
            'serial': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1383209914'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'})
        },
        'cyder.soakeyvalue': {
            'Meta': {'object_name': 'SOAKeyValue', 'db_table': "'soa_kv'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_quoted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'soa': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'keyvalue_set'", 'to': "orm['cyder.SOA']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
        'cyder.staticintrkeyvalue': {
            'Meta': {'unique_together': "(('key', 'value', 'static_interface'),)", 'object_name': 'StaticIntrKeyValue', 'db_table': "'static_interface_kv'"},
            'has_validator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_option': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_quoted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_statement': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'static_interface': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.StaticInterface']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'cyder.system': {
            'Meta': {'object_name': 'System', 'db_table': "'system'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'cyder.systemkeyvalue': {
            'Meta': {'unique_together': "(('key', 'value', 'system'),)", 'object_name': 'SystemKeyValue', 'db_table': "'system_kv'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_quoted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'system': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.System']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
        'cyder.vlankeyvalue': {
            'Meta': {'unique_together': "(('key', 'value'),)", 'object_name': 'VlanKeyValue', 'db_table': "'vlan_kv'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_quoted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'vlan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Vlan']"})
        },
        'cyder.vrf': {
            'Meta': {'object_name': 'Vrf', 'db_table': "'vrf'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'cyder.vrfkeyvalue': {
            'Meta': {'object_name': 'VrfKeyValue', 'db_table': "'vrf_kv'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_quoted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'vrf': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Vrf']"})
        },
        'cyder.workgroup': {
            'Meta': {'object_name': 'Workgroup', 'db_table': "'workgroup'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'cyder.workgroupkeyvalue': {
            'Meta': {'unique_together': "(('key', 'value', 'workgroup'),)", 'object_name': 'WorkgroupKeyValue', 'db_table': "'workgroup_kv'"},
            'has_validator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_option': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_quoted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_statement': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'workgroup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyder.Workgroup']"})
        }
    }

    complete_apps = ['cyder']