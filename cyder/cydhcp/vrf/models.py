from django.db import models
from django.db.models.loading import get_model

from cyder.base.eav.constants import ATTRIBUTE_INFORMATIONAL
from cyder.base.eav.models import Attribute, EAVBase
from cyder.base.mixins import ObjectUrlMixin
from cyder.base.helpers import get_display
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.keyvalue.models import KeyValue


class Vrf(models.Model, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    search_fields = ('name',)
    display_fields = ('name',)

    class Meta:
        db_table = 'vrf'

    def __str__(self):
        return get_display(self)

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        Network = get_model('network', 'network')
        networks = Network.objects.filter(range__in=ctnr.ranges.all())
        objects = objects or Vrf.objects
        return objects.filter(network__in=networks)

    def details(self):
        data = super(Vrf, self).details()
        data['data'] = (
            ('Name', 'name', self),
        )
        return data

    # NOTE: The following comment was written when Network had a one-to-many
    #       relationship with Vrf (which was wrong). The schema has been fixed,
    #       as has this function. However, the comment was not fixed because I
    #       can't understand it.
    # vrfs will have one masked network,
    # but that may change when they are expanding
    # eg: network_id's in vrf
    def get_related_networks(self, vrfs):
        networks = set()
        for vrf in vrfs:
            for network in vrf.network_set.all():
                networks.update(network.get_related_networks())
        return networks

    @staticmethod
    def eg_metadata():
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'name', 'datatype': 'string', 'editable': True},
            {'name': 'network', 'datatype': 'string', 'editable': False},
        ]}

    def build_vrf(self):
        build_str = ''
        for network_ in self.network_set.all():
            for range_ in network_.range_set.all():
                dynamic_clients = range_.dynamicinterface_set.filter(
                    dhcp_enabled=True)
                if not dynamic_clients:
                    continue
                build_str += "\nclass \"{0}:{1}:{2}\" {{\n".format(
                    self.name, range_.start_str, range_.end_str)
                build_str += "\tmatch hardware;\n"
                build_str += "}\n"
                for client in dynamic_clients:
                    build_str += client.build_subclass(self.name)
        return build_str


class VrfAV(EAVBase):
    class Meta:
        db_table = 'vrf_av'
        unique_together = ('vrf', 'attribute')


    vrf = models.ForeignKey(Vrf)
    attribute = models.ForeignKey(Attribute,
            limit_choices_to={'attribute_type': ATTRIBUTE_INFORMATIONAL})
