from django.db import models
# Create your models here.

from cyder.base.mixins import ObjectUrlMixin
from cyder.cydhcp.keyvalue.base_option import CommonOption


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
        join_args = lambda x: "\n".join(map(lambda y: "\t{0};\n".format(y), x))
        clients = self.static_interface_set.all()
        build_str = "group {\n"
        statements = self.workgroup_key_value_set.filter(is_statement=True)
        options = self.workgroup_key_value_set.filter(is_option=True)
        build_str += "\t# Workgroup Options\n"
        build_str += join_args(options)
        build_str += "\t# Workgroup Statements\n"
        build_str += join_args(statements)
        # This only builds the static interfaces in the workgroup which is not
        # complete.  We should also build dynamic ranges but that requires that
        # each dynamic ranges has a fqdn.  That is not currently the case so
        # logic needs to be implemented to make sure that they do.
        build_str += "\t# Static Hosts in Workgorup\n"
        build_str += join_args(map(lambda x: x.build_host(), clients))
        build_str += ")\n"
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
