from django.db import models
from django.db.models.loading import get_model
from django.core.exceptions import ObjectDoesNotExist

from cyder.base.mixins import ObjectUrlMixin
from cyder.base.helpers import get_display
from cyder.cydns.domain.models import Domain
from cyder.cydhcp.utils import networks_to_Q
from cyder.cydhcp.keyvalue.models import KeyValue


class Vlan(models.Model, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    number = models.PositiveIntegerField()

    search_fields = ('name', 'number',)
    display_fields = ('name',)

    class Meta:
        db_table = "vlan"
        unique_together = ("name", "number")

    def __str__(self):
        return get_display(self)

    def __repr__(self):
        return "<Vlan {0}>".format(str(self))

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        Network = get_model('network', 'network')
        networks = Network.objects.filter(range__in=ctnr.ranges.all())
        objects = objects or Vlan.objects
        return objects.filter(network__in=networks)

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


class VlanKeyValue(KeyValue):
    vlan = models.ForeignKey(Vlan, null=False)

    class Meta:
        db_table = "vlan_kv"
        unique_together = ("key", "value")

    def _aa_description(self):
        return
