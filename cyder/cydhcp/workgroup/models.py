from itertools import chain

from django.db import models
from django.db.models import Q

from cyder.base.eav.constants import ATTRIBUTE_OPTION, ATTRIBUTE_STATEMENT
from cyder.base.eav.fields import EAVAttributeField
from cyder.base.eav.models import Attribute, EAVBase
from cyder.base.mixins import ObjectUrlMixin
from cyder.base.models import BaseModel
from cyder.base.utils import transaction_atomic
from cyder.cydhcp.utils import join_dhcp_args


class Workgroup(BaseModel, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    search_fields = ('name',)
    sort_fields = ('name',)

    class Meta:
        app_label = 'cyder'
        db_table = 'workgroup'

    def __unicode__(self):
        return self.name

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        workgroups = Workgroup.objects.filter(Q(id__in=ctnr.workgroups.all()) |
                                              Q(name="default"))
        if objects is not None:
            workgroups = workgroups.filter(pk__in=objects)
        return workgroups

    def details(self):
        data = super(Workgroup, self).details()
        data['data'] = [
            ('Name', 'name', self),
        ]
        return data

    @staticmethod
    def eg_metadata():
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'name', 'datatype': 'string', 'editable': True},
        ]}

    @transaction_atomic
    def save(self, *args, **kwargs):
        self.full_clean()

        super(Workgroup, self).save(*args, **kwargs)

    def build_workgroup(self):
        from cyder.cydhcp.interface.static_intr.models import StaticInterface
        from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
        build_str = ""
        dynamic_clients = DynamicInterface.objects.filter(
            workgroup=self, dhcp_enabled=True)
        static_clients = StaticInterface.objects.filter(
            workgroup=self, dhcp_enabled=True)
        #if not (static_clients or dynamic_clients):
            #return build_str
        build_str += "group {{ #{0}\n".format(self.name)
        statements = self.workgroupav_set.filter(
            attribute__attribute_type=ATTRIBUTE_STATEMENT)
        options = list(self.workgroupav_set.filter(
            attribute__attribute_type=ATTRIBUTE_OPTION))

        def is_host_option(option):
            return any(x in option.value for x in ['%h', '%i', '%m', '%6m'])

        host_options = filter(is_host_option, options)
        for x in host_options:
            options.remove(x)

        build_str += "\t# Workgroup Options\n"
        if options:
            build_str += join_dhcp_args(options)
        build_str += "\t# Workgroup Statements\n"
        if statements:
            build_str += join_dhcp_args(statements)
        build_str += "\t# Static Hosts in Workgroup\n"
        for client in chain(dynamic_clients, static_clients):
            build_str += client.build_host(host_options)
        build_str += "}\n"
        return build_str


class WorkgroupAV(EAVBase):
    class Meta(EAVBase.Meta):
        app_label = 'cyder'
        db_table = 'workgroup_av'

    entity = models.ForeignKey(Workgroup)
    attribute = EAVAttributeField(Attribute,
        type_choices=(ATTRIBUTE_OPTION, ATTRIBUTE_STATEMENT))
