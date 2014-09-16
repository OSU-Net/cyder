from django.db import models
from django.db.models.loading import get_model
from django.core.exceptions import ObjectDoesNotExist

from cyder.base.eav.constants import ATTRIBUTE_INVENTORY
from cyder.base.eav.fields import EAVAttributeField
from cyder.base.eav.models import Attribute, EAVBase
from cyder.base.mixins import ObjectUrlMixin
from cyder.base.helpers import get_display
from cyder.base.models import BaseModel
from cyder.base.validators import validate_positive_integer_field
from cyder.cydns.domain.models import Domain
from cyder.cydhcp.utils import networks_to_Q


class Vlan(BaseModel, ObjectUrlMixin):
    @property
    def pretty_name(self):
        return self.name

    pretty_type = 'VLAN'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    number = models.PositiveIntegerField(
        validators=[validate_positive_integer_field])

    search_fields = ('name', 'number',)
    display_fields = ('name',)

    class Meta:
        app_label = 'cyder'
        db_table = "vlan"
        unique_together = ("name", "number")

    def __str__(self):
        return '{0} ({1})'.format(get_display(self), self.number)

    def __repr__(self):
        return "<Vlan {0}>".format(str(self))

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        Network = get_model('cyder', 'network')
        networks = Network.objects.filter(range__in=ctnr.ranges.all())
        objects = objects or Vlan.objects
        return objects.filter(network__in=networks)

    def check_in_ctnr(self, ctnr):
        return self.network_set.filter(range__in=ctnr.ranges.all()).exists()

    def details(self):
        """For tables."""
        data = super(Vlan, self).details()
        data['data'] = [
            ('Name', 'name', self),
            ('Number', 'number', self.number),
        ]
        return data

    @staticmethod
    def eg_metadata():
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'name', 'datatype': 'string', 'editable': True},
            {'name': 'number', 'datatype': 'string', 'editable': True},
        ]}

    def compile_Q(self):
        """Compile a Django Q that will match any IP inside this vlan."""
        return networks_to_Q(self.network_set.all())

    def find_domain(self):
        """
        This memeber function will look at all the Domain objects and attempt
        to find an approriate domain that corresponds to this VLAN.
        """
        for network in self.network_set.all():
            if network.site:
                expected_name = "{0}.{1}.mozilla.com".format(
                    self.name, network.site.get_site_path())
                try:
                    domain = Domain.objects.get(name=expected_name)
                except ObjectDoesNotExist:
                    continue
                return domain.name

        return None


class VlanAV(EAVBase):
    class Meta(EAVBase.Meta):
        app_label = 'cyder'
        db_table = 'vlan_av'


    entity = models.ForeignKey(Vlan)
    attribute = EAVAttributeField(Attribute,
        type_choices=(ATTRIBUTE_INVENTORY,))
