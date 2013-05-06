from django.db import models
# Create your models here.

from itertools import chain

from cyder.base.mixins import ObjectUrlMixin
from cyder.cydhcp.keyvalue.base_option import CommonOption
from cyder.cydhcp.utils import join_dhcp_args


class Workgroup(models.Model, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    search_fields = ('name',)

    class Meta:
        db_table = 'workgroup'

    def __str__(self):
        return self.name

    def details(self):
        data = super(Workgroup, self).details()
        data['data'] = [
            ('Name', 'name', self),
        ]
        return data

    def eg_metadata(self):
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'name', 'datatype': 'string', 'editable': True},
        ]}

    def build_workgroup(self):
        build_str = ""
        static_clients = self.staticinterface_set.all()
        dynamic_clients = self.dynamicinterface_set.all()
        if not (static_clients or dynamic_clients):
            return build_str
        build_str += "group {\n"
        statements = self.workgroupkeyvalue_set.filter(is_statement=True)
        options = self.workgroupkeyvalue_set.filter(is_option=True)
        build_str += "\t# Workgroup Options\n"
        build_str += join_dhcp_args(options)
        build_str += "\t# Workgroup Statements\n"
        build_str += join_dhcp_args(statements)
        build_str += "\t# Static Hosts in Workgorup\n"
        for client in chain(dynamic_clients, static_clients):
            build_str += client.build_host()
        build_str += "}\n"
        return build_str


class WorkgroupKeyValue(CommonOption):
    workgroup = models.ForeignKey(Workgroup, null=False)
    aux_attrs = (('description', 'A description of the workgroup'))

    class Meta:
        db_table = 'workgroup_key_value'
        unique_together = ('key', 'value', 'workgroup')

    def save(self, *args, **kwargs):
        self.clean()
        super(WorkgroupKeyValue, self).save(*args, **kwargs)
