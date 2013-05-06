from django.db import models
# Create your models here.
from cyder.base.mixins import ObjectUrlMixin
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.keyvalue.models import KeyValue

from itertools import chain

class Vrf(models.Model, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    network = models.ForeignKey(Network, null=True)

    search_fields = ('name',)

    class Meta:
        db_table = 'vrf'

    def __str__(self):
        return self.name

    def details(self):
        data = super(Vrf, self).details()
        data['data'] = (
            ('Name', 'name', self),
            ('Network', 'network', self.network),
        )
        return data

    def eg_metadata(self):
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'name', 'datatype': 'string', 'editable': True},
            {'name': 'network', 'datatype': 'string', 'editable': False},
        ]}


    def build_vrf(self):
        build_str = ''
        dynamic_clients = self.dynamicinterface_set.all()
        if not dynamic_clients:
            return build_str
        for range_ in self.network.range_set.all():
            build_str += "\nclass \"{0}:{1}:{2}\" {{\n".format(
                self.name, range_.start_str, range_.end_str)
            build_str += "\n# {0} for range {1}:{2}\n".format(
                self.name, range_.start_str, range_.end_str)
            build_str += "\tmatch hardware;\n"
            build_str += "}\n"
            for client in dynamic_clients:
                build_str += client.build_subclass(self.name)
        return build_str


class VrfKeyValue(KeyValue):
    vrf = models. ForeignKey(Vrf, null=False)

    class Meta:
        db_table = "vrf_key_value"

    def _aa_decription(self):
        return
