import datetime
import re
from django.core.exceptions import ValidationError
from django.db import models

from cyder.base.eav.constants import (ATTRIBUTE_OPTION, ATTRIBUTE_STATEMENT,
                                      ATTRIBUTE_INVENTORY)
from cyder.base.eav.fields import EAVAttributeField
from cyder.base.eav.models import Attribute, EAVBase
from cyder.base.mixins import ObjectUrlMixin
from cyder.base.models import BaseModel, ExpirableMixin
from cyder.base.utils import safe_delete, safe_save
from cyder.core.fields import MacAddrField
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydhcp.interface.dynamic_intr.validation import is_dynamic_range
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.utils import format_mac, join_dhcp_args
from cyder.cydhcp.workgroup.models import Workgroup


class DynamicInterface(BaseModel, ObjectUrlMixin, ExpirableMixin):
    pretty_type = 'dynamic interface'

    ctnr = models.ForeignKey(Ctnr, null=False, verbose_name="Container")
    workgroup = models.ForeignKey(Workgroup, null=True, blank=True)
    system = models.ForeignKey(System, help_text="System to associate "
                                                 "the interface with")
    mac = MacAddrField(dhcp_enabled='dhcp_enabled', verbose_name='MAC address',
                       help_text='(required if DHCP is enabled)')
    range = models.ForeignKey(Range, validators=[is_dynamic_range])
    dhcp_enabled = models.BooleanField(default=True,
                                       verbose_name='Enable DHCP?')
    last_seen = models.DateTimeField(null=True, blank=True)
    search_fields = ('mac',)

    class Meta:
        app_label = 'cyder'
        db_table = 'dynamic_interface'
        unique_together = (('range', 'mac'),)

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        objects = objects or DynamicInterface.objects
        return objects.filter(ctnr=ctnr)

    def __unicode__(self):
        if self.mac:
            return self.mac
        else:
            return '(no MAC address)'

    def details(self):
        data = super(DynamicInterface, self).details()
        data['data'] = [
            ('System', 'system', self.system),
            ('Mac', 'mac', self),
            ('Range', 'range', self.range),
            ('Workgroup', 'workgroup', self.workgroup),
            ('Last seen', 'last_seen', self.last_seen)]
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
        s = s.replace('%m', self.mac.replace(':', ''))
        s = s.replace('%6m', self.mac.replace(':', '')[0:6])
        return s

    def build_host(self, options=()):
        build_str = "\thost {0} {{\n".format(self.get_fqdn())
        build_str += "\t\thardware ethernet {0};\n".format(self.mac)
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
        return 'subclass "{0}" 1:{1};\n'.format(classname, self.mac)

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
        if self.mac:
            siblings = self.range.dynamicinterface_set.filter(mac=self.mac)
            if self.pk is not None:
                siblings = siblings.exclude(pk=self.pk)
            if siblings.exists():
                raise ValidationError(
                    "MAC address must be unique in this interface's range")

    @safe_delete
    def delete(self, *args, **kwargs):
        delete_system = kwargs.pop('delete_system', True)
        update_range_usage = kwargs.pop('update_range_usage', True)
        rng = self.range
        if delete_system:
            if (not self.system.dynamicinterface_set.exclude(
                    id=self.id).exists() and
                    not self.system.staticinterface_set.exists()):
                self.system.delete(commit=False)
        super(DynamicInterface, self).delete()
        if rng and update_range_usage:
            rng.save(commit=False)

    @safe_save
    def save(self, *args, **kwargs):
        update_range_usage = kwargs.pop('update_range_usage', True)
        old_range = None
        if self.id is not None:
            old_range = DynamicInterface.objects.get(id=self.id).range

        super(DynamicInterface, self).save()
        if self.range and update_range_usage:
            self.range.save(commit=False)
            if old_range:
                old_range.save(commit=False)


class DynamicInterfaceAV(EAVBase):
    class Meta(EAVBase.Meta):
        app_label = 'cyder'
        db_table = "dynamic_interface_av"

    entity = models.ForeignKey(DynamicInterface)
    attribute = EAVAttributeField(
        Attribute,
        type_choices=(ATTRIBUTE_INVENTORY,))
