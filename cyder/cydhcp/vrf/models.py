from django.db import models
from django.db.models.loading import get_model
from itertools import chain

from cyder.base.eav.constants import ATTRIBUTE_INVENTORY
from cyder.base.eav.fields import EAVAttributeField
from cyder.base.eav.models import Attribute, EAVBase
from cyder.base.mixins import ObjectUrlMixin
from cyder.base.models import BaseModel
from cyder.base.utils import transaction_atomic
from cyder.cydhcp.vrf.validators import validate_vrf_name


class Vrf(BaseModel, ObjectUrlMixin):
    pretty_type = 'VRF'

    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=100, unique=True, validators=[validate_vrf_name])

    search_fields = ('name',)
    sort_fields = ('name',)

    class Meta:
        app_label = 'cyder'
        db_table = 'vrf'

    def __unicode__(self):
        return self.name

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        if objects is None:
            return Vrf.objects.all()
        else:
            return objects

    def check_in_ctnr(self, ctnr):
        return self.network_set.filter(range__in=ctnr.ranges.all()).exists()

    def details(self):
        data = super(Vrf, self).details()
        data['data'] = (
            ('Name', 'name', self),
        )
        return data

    @staticmethod
    def get_related_networks(vrfs):
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

    @transaction_atomic
    def save(self, *args, **kwargs):
        self.full_clean()

        super(Vrf, self).save(*args, **kwargs)

    def build_vrf(self):
        build_str = ('class "{0}" {{\n'
                     '\tmatch hardware;\n'
                     '}}\n'
                     .format(self.name))

        for network_ in self.network_set.all():
            for range_ in network_.range_set.all():
                clients = chain(
                    range_.staticinterfaces.filter(dhcp_enabled=True),
                    range_.dynamicinterface_set.filter(dhcp_enabled=True)
                )
                for client in clients:
                    build_str += client.build_subclass(self.name)


        return build_str


class VrfAV(EAVBase):
    class Meta(EAVBase.Meta):
        app_label = 'cyder'
        db_table = 'vrf_av'


    entity = models.ForeignKey(Vrf)
    attribute = EAVAttributeField(Attribute,
        type_choices=(ATTRIBUTE_INVENTORY,))
