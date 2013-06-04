from django.db import models
# Create your models here.
from cyder.base.mixins import ObjectUrlMixin
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.keyvalue.models import KeyValue


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

    # vrfs will have one masked network,
    # but that may change when they are expanding
    # eg: network_id's in vrf
    def get_related_networks(self, vrfs):
        networks = set()
        for vrf in vrfs:
            root_networks = Network.objects.filter(id=vrf.network_id)
            for network in root_networks:
                networks.update(network.get_related_networks())
        return networks

    def eg_metadata(self):
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'name', 'datatype': 'string', 'editable': True},
            {'name': 'network', 'datatype': 'string', 'editable': False},
        ]}

    def build_vrf(self):
        build_str = ''
        for range_ in self.network.range_set.all():
            dynamic_clients = range_.dynamicinterface_set.filter(
                dhcp_enabled=True)
            if not dynamic_clients:
                continue
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
        db_table = "vrf_kv"

    def _aa_decription(self):
        return
