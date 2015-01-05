from gettext import gettext as _

from django.db import models
from django.core.exceptions import ValidationError

import datetime
import re

from cyder.core.fields import MacAddrField

from cyder.core.system.models import System

from cyder.base.constants import IP_TYPE_6
from cyder.base.eav.constants import (ATTRIBUTE_OPTION, ATTRIBUTE_STATEMENT,
                                      ATTRIBUTE_INVENTORY)
from cyder.base.eav.fields import EAVAttributeField
from cyder.base.eav.models import Attribute, EAVBase
from cyder.base.models import ExpirableMixin
from cyder.base.utils import transaction_atomic

from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.range.utils import find_range
from cyder.cydhcp.utils import format_mac, join_dhcp_args
from cyder.cydhcp.workgroup.models import Workgroup

from cyder.cydns.ptr.models import BasePTR, PTR
from cyder.cydns.address_record.models import AddressRecord, BaseAddressRecord
from cyder.cydns.ip.utils import ip_to_reverse_name
from cyder.cydns.domain.models import Domain


class StaticInterface(BaseAddressRecord, BasePTR, ExpirableMixin):
    # Keep in mind that BaseAddressRecord will have it's methods called before
    # BasePTR
    """The StaticInterface Class.

        >>> s = StaticInterface(label=label, domain=domain, ip_str=ip_str,
        ... ip_type=ip_type, dhcp_enabled=True, dns_enabled=True)
        >>> s.save()

    This class is the main interface to DNS and DHCP. A static
    interface consists of three key pieces of information: IP address, MAC
    address, and hostname (the hostname is comprised of a label and a domain).
    From these three pieces of information, three things are ensured: An A or
    AAAA DNS record, a PTR record, and a `host` statement in the DHCP builds
    that grants the MAC address of the interface the correct IP address and
    hostname.

    If you want an A/AAAA, PTR, and a DHCP lease, create one of these objects.

    In terms of DNS, a static interface represents a PTR and A record and must
    adhere to the requirements of those classes. The interface inherits from
    BaseAddressRecord.
    """

    pretty_type = 'static interface'

    id = models.AutoField(primary_key=True)
    mac = MacAddrField(dhcp_enabled='dhcp_enabled', verbose_name='MAC address',
                       help_text='(required if DHCP is enabled)')
    reverse_domain = models.ForeignKey(Domain, null=True, blank=True,
                                       related_name='reverse_staticintr_set')
    system = models.ForeignKey(
        System, help_text='System to associate the interface with')

    workgroup = models.ForeignKey(Workgroup, null=True, blank=True)

    dhcp_enabled = models.BooleanField(verbose_name='Enable DHCP?',
                                       default=True)
    dns_enabled = models.BooleanField(verbose_name='Enable DNS?',
                                      default=True)

    last_seen = models.DateTimeField(null=True, blank=True)

    search_fields = ('mac', 'ip_str', 'fqdn')

    class Meta:
        app_label = 'cyder'
        db_table = 'static_interface'
        unique_together = (('ip_upper', 'ip_lower'), ('label', 'domain'))

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        objects = objects or StaticInterface.objects
        return objects.filter(ctnr=ctnr)

    def __unicode__(self):
        return self.fqdn

    @property
    def range(self):
        if self.ip_str:
            return find_range(self.ip_str)

    def details(self):
        data = super(StaticInterface, self).details()
        data['data'] = (
            ('Name', 'fqdn', self),
            ('System', 'system', self.system),
            ('IP', 'ip_str', str(self.ip_str)),
            ('MAC', 'mac', self.mac),
            ('Workgroup', 'workgroup', self.workgroup),
            ('DHCP', 'dhcp_enabled',
                'True' if self.dhcp_enabled else 'False'),
            ('DNS', 'dns_enabled',
                'True' if self.dns_enabled else 'False'),
            ('Last seen', 'last_seen', self.last_seen),
        )
        return data

    @staticmethod
    def eg_metadata():
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'fqdn', 'datatype': 'string', 'editable': False},
        ]}

    @property
    def rdtype(self):
        return 'INTR'

    def get_related_systems(self):
        related_interfaces = StaticInterface.objects.filter(mac=self.mac)
        related_interfaces = related_interfaces.select_related('system')
        related_systems = set()
        for interface in related_interfaces:
            related_systems.update([interface.system])
        return related_systems

    @transaction_atomic
    def save(self, *args, **kwargs):
        self.full_clean()

        update_range_usage = kwargs.pop('update_range_usage', True)
        old_range = None
        if self.id is not None:
            old_range = StaticInterface.objects.get(id=self.id).range

        super(StaticInterface, self).save(*args, **kwargs)
        self.schedule_zone_rebuild()
        if update_range_usage:
            new_range = self.range
            if new_range:
                new_range.save(commit=False)
            if old_range:
                old_range.save(commit=False)

    @transaction_atomic
    def delete(self, *args, **kwargs):
        rng = self.range
        update_range_usage = kwargs.pop('update_range_usage', True)
        delete_system = kwargs.pop('delete_system', True)

        if delete_system:
            if(not self.system.staticinterface_set.exclude(
                    id=self.id).exists() and
                    not self.system.dynamicinterface_set.exists()):
                self.system.delete(commit=False)

        super(StaticInterface, self).delete(*args, **kwargs)
        if rng and update_range_usage:
            rng.save(commit=False)

    def schedule_zone_rebuild(self):
        if self.domain.soa is not None:
            self.domain.soa.schedule_rebuild()
        if self.reverse_domain.soa is not None:
            self.reverse_domain.soa.schedule_rebuild()

    def check_A_PTR_collision(self):
        if PTR.objects.filter(ip_str=self.ip_str).exists():
            raise ValidationError("A PTR already uses '%s'" %
                                  self.ip_str)
        if AddressRecord.objects.filter(ip_str=self.ip_str, fqdn=self.fqdn
                                        ).exists():
            raise ValidationError("An A record already uses '%s' and '%s'" %
                                  (self.fqdn, self.ip_str))

    def format_host_option(self, option):
        s = str(option)
        s = s.replace('%h', self.label)
        s = s.replace('%i', self.ip_str)
        s = s.replace('%m', self.mac.replace(':', ''))
        s = s.replace('%6m', self.mac.replace(':', '')[0:6])
        return s

    def build_host(self, options=None):
        build_str = '\thost {0} {{\n'.format(self.fqdn)
        build_str += '\t\thardware ethernet {0};\n'.format(self.mac)
        if self.ip_type == IP_TYPE_6:
            build_str += '\t\tfixed-address6 {0};\n'.format(self.ip_str)
        else:
            build_str += '\t\tfixed-address {0};\n'.format(self.ip_str)
        build_str += join_dhcp_args(map(self.format_host_option, options),
                                    depth=2)
        options = self.staticinterfaceav_set.filter(
            attribute__attribute_type=ATTRIBUTE_OPTION)
        statements = self.staticinterfaceav_set.filter(
            attribute__attribute_type=ATTRIBUTE_STATEMENT)
        if options:
            build_str += '\t\t# Host Options\n'
            build_str += join_dhcp_args(options, depth=2)
        if statements:
            build_str += '\t\t# Host Statements\n'
            build_str += join_dhcp_args(statements, depth=2)
        build_str += '\t}\n'
        return build_str

    def build_subclass(self, classname):
        return 'subclass "{0}" 1:{1};\n'.format(classname, self.mac)

    def clean(self, *args, **kwargs):
        validate_glue = kwargs.pop('validate_glue', True)

        super(StaticInterface, self).clean(validate_glue=False,
                                           ignore_intr=True)

        from cyder.cydns.ptr.models import PTR
        if PTR.objects.filter(ip_str=self.ip_str, fqdn=self.fqdn).exists():
            raise ValidationError("A PTR already uses '%s' and '%s'" %
                                  (self.fqdn, self.ip_str))
        if AddressRecord.objects.filter(ip_str=self.ip_str, fqdn=self.fqdn
                                        ).exists():
            raise ValidationError("An A record already uses '%s' and '%s'" %
                                  (self.fqdn, self.ip_str))

        if validate_glue:
            self.check_glue_status()

        if self.dhcp_enabled:
            if not (self.range and self.range.range_type == STATIC):
                raise ValidationError('DHCP is enabled for this interface, so '
                                      'its IP must be in a static range.')

    def check_glue_status(self):
        """If this interface is a 'glue' record for a Nameserver instance,
        do not allow modifications to this record. The Nameserver will
        need to point to a different record before this record can
        be updated.
        """
        if self.pk is None:
            return
        # First get this object from the database and compare it to the
        # Nameserver object about to be saved.
        db_self = StaticInterface.objects.get(pk=self.pk)
        if db_self.label == self.label and db_self.domain == self.domain:
            return
        # The label of the domain changed. Make sure it's not a glue record.
        from cyder.cydns.nameserver.models import Nameserver
        if Nameserver.objects.filter(intr_glue=self).exists():
            raise ValidationError(
                "This Interface represents a glue record for a "
                "Nameserver. Change the Nameserver to edit this record.")

    a_template = _("{bind_name:$lhs_just} {ttl:$ttl_just}  "
                   "{rdclass:$rdclass_just}"
                   " {rdtype_clob:$rdtype_just} {ip_str:$rhs_just}")
    ptr_template = _("{dns_ip:$lhs_just} {ttl:$ttl_just}  "
                     "{rdclass:$rdclass_just}"
                     " {rdtype_clob:$rdtype_just} {fqdn:1}.")

    def bind_render_record(self, pk=False, **kwargs):
        self.rdtype_clob = kwargs.pop('rdtype', 'INTR')
        if kwargs.pop('reverse', False):
            self.template = self.ptr_template
            self.dns_ip = ip_to_reverse_name(self.ip_str) + '.'
        else:
            self.template = self.a_template
        return super(StaticInterface, self).bind_render_record(pk=pk, **kwargs)


class StaticInterfaceAV(EAVBase):
    class Meta(EAVBase.Meta):
        app_label = 'cyder'
        db_table = 'static_interface_av'

    entity = models.ForeignKey(StaticInterface)
    attribute = EAVAttributeField(
        Attribute,
        type_choices=(ATTRIBUTE_INVENTORY,))
