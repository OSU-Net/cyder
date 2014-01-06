from django.db import models

from cyder.base.eav.constants import (ATTRIBUTE_OPTION, ATTRIBUTE_STATEMENT,
                                      ATTRIBUTE_INVENTORY)
from cyder.base.eav.fields import EAVAttributeField
from cyder.base.eav.models import Attribute, EAVBase
from cyder.cydhcp.interface.dynamic_intr.validation import is_dynamic_range
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.utils import format_mac, join_dhcp_args
from cyder.cydhcp.workgroup.models import Workgroup
from cyder.core.fields import MacAddrField
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.base.mixins import ObjectUrlMixin
from cyder.base.models import BaseModel

import datetime
import re


class DynamicInterface(BaseModel, ObjectUrlMixin):
    ctnr = models.ForeignKey(Ctnr, null=False, verbose_name="Container")
    workgroup = models.ForeignKey(Workgroup, null=True, blank=True)
    system = models.ForeignKey(System, help_text="System to associate "
                                                 "the interface with")
    mac = MacAddrField(dhcp_enabled='dhcp_enabled', verbose_name='MAC address',
                       help_text='(required if DHCP is enabled)')
    range = models.ForeignKey(Range, validators=[is_dynamic_range])
    dhcp_enabled = models.BooleanField(default=True,
                                       verbose_name='Enable DHCP?')
    last_seen = models.PositiveIntegerField(
        max_length=11, blank=True, default=0)
    search_fields = ('mac',)

    class Meta:
        app_label = 'cyder'
        db_table = 'dynamic_interface'

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        objects = objects or DynamicInterface.objects
        return objects.filter(ctnr=ctnr)

    def __str__(self):
        return "{0}".format(self.mac_str)

    @property
    def mac_str(self):
        return (':').join(re.findall('..', self.mac))

    def __repr__(self):
        return "Interface {0}".format(str(self))

    def details(self):
        data = super(DynamicInterface, self).details()
        if self.last_seen == 0:
            date = 0

        else:
            date = datetime.datetime.fromtimestamp(self.last_seen)
            date = date.strftime('%B %d, %Y, %I:%M %p')

        data['data'] = [
            ('System', 'system', self.system),
            ('Mac', 'mac', self),
            ('Range', 'range', self.range),
            ('Workgroup', 'workgroup', self.workgroup),
            ('Last seen', 'last_seen', date)]
        return data

    @staticmethod
    def eg_metadata():
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'system', 'datatype': 'string', 'editable': False},
        ]}

    def format_host_option(self, option):
        s = str(option)
        s = s.replace('%h', self.system.name)
        s = s.replace('%i', self.ip_str)
        s = s.replace('%m', self.mac)
        s = s.replace('%6m', self.mac[0:6])
        return s

    def build_host(self, options=None):
        build_str = "\thost {0} {{\n".format(self.get_fqdn())
        build_str += "\t\thardware ethernet {0};\n".format(
            format_mac(self.mac))
        build_str += join_dhcp_args(map(self.format_host_option, options),
                                    depth=2)
        options = self.dynamicinterfaceav_set.filter(
            attribute__attribute_type=ATTRIBUTE_OPTION)
        statements = self.dynamicinterfaceav_set.filter(
            attribute__attribute_type=ATTRIBUTE_STATEMENT)
        if options:
            build_str += "\t\t# Host Options\n"
            build_str += join_dhcp_args(options, depth=2)
        if statements:
            build_str += "\t\t# Host Statemets\n"
            build_str += join_dhcp_args(statements, depth=2)
        build_str += "\t}\n"
        return build_str

    def build_subclass(self, classname):
        return 'subclass "{0}" 1:{1};\n'.format(
            classname, format_mac(self.mac))

    def get_related_systems(self):
        related_interfaces = DynamicInterface.objects.filter(mac=self.mac)
        related_interfaces = related_interfaces.select_related('system')
        related_systems = set()
        for interface in related_interfaces:
            related_systems.update([interface.system])
        return related_systems

    def get_fqdn(self):
        if not self.system.name:
            return self.range.domain.name
        else:
            return "{0}.{1}".format(self.system.name, self.range.domain.name)

    def clean(self, *args, **kwargs):
        super(DynamicInterface, self).clean(*args, **kwargs)

    def delete(self, *args, **kwargs):
        delete_system = kwargs.pop('delete_system', True)
        update_range_usage = kwargs.pop('update_range_usage', True)
        rng = self.range
        if delete_system:
            if (not self.system.dynamicinterface_set.all().exclude(
                    id=self.id).exists() and
                    not self.system.staticinterface_set.all().exists()):
                self.system.delete()
        super(DynamicInterface, self).delete()
        if rng and update_range_usage:
            rng.save()

    def save(self, *args, **kwargs):
        update_range_usage = kwargs.pop('update_range_usage', True)
        old_range = None
        if self.id is not None:
            old_range = DynamicInterface.objects.get(id=self.id).range

        super(DynamicInterface, self).save()
        if self.range and update_range_usage:
            self.range.save()
            if old_range:
                old_range.save()


class DynamicInterfaceAV(EAVBase):
    class Meta(EAVBase.Meta):
        app_label = 'cyder'
        db_table = "dynamic_interface_av"

    entity = models.ForeignKey(DynamicInterface)
    attribute = EAVAttributeField(
        Attribute,
        type_choices=(ATTRIBUTE_INVENTORY,))
