from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from cyder.base.mixins import ObjectUrlMixin
from cyder.cydns.domain.models import Domain
from cyder.cydhcp.utils import networks_to_Q
from cyder.cydhcp.keyvalue.models import KeyValue


class Vlan(models.Model, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    number = models.PositiveIntegerField()

    class Meta:
        db_table = "vlan"
        unique_together = ("name", "number")

    def __str__(self):
        return "{0}".format(self.name)

    def __repr__(self):
        return "<Vlan {0}>".format(str(self))

    def details(self):
        """For tables."""
        data = super(Vlan, self).details()
        data['data'] = [
            ('Name', 'name', self),
            ('Number', 'number', self.number),
        ]
        return data

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
                expected_name = "{0}.{1}.mozilla.com".format(self.name,
                                                network.site.get_site_path())
                try:
                    domain = Domain.objects.get(name=expected_name)
                except ObjectDoesNotExist:
                    continue
                return domain.name

        return None

    def get_related_networks(self):
        from cyder.cydhcp.network.models import Network
        from cyder.cydhcp.network.utils import calc_networks
        related_networks = Network.objects.filter(vlan=self)
        networks = set(related_networks)
        while related_networks:
            subnets = set()
            for network in related_networks:
                _, related = calc_networks(network)
                subnets.update(related)
            networks.update(subnets)
            related_networks = subnets
        return networks

    def get_related_sites(self, related_networks):
        return set([network.site for network in related_networks])


class VlanKeyValue(KeyValue):
    vlan = models.ForeignKey(Vlan, null=False)

    class Meta:
        db_table = "vlan_key_value"
        unique_together = ("key", "value")

    def _aa_description(self):
        return
