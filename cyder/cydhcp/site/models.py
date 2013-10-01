from django.db import models
from django.db.models.loading import get_model
from django.core.validators import RegexValidator

from cyder.base.eav.constants import ATTRIBUTE_INFORMATIONAL
from cyder.base.eav.models import Attribute, EAVBase
from cyder.base.mixins import ObjectUrlMixin
from cyder.cydhcp.utils import networks_to_Q


class Site(models.Model, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255,
                            validators=[RegexValidator('^[^/]+$')])
    parent = models.ForeignKey("self", null=True, blank=True)

    search_fields = ('name', 'parent__name')
    display_fields = ('name',)

    class Meta:
        db_table = 'site'
        unique_together = ('name', 'parent')

    def __str__(self):
        name = self.name.title()
        if self.parent:
            return "%s in %s" % (name, self.parent.get_full_name())
        else:
            return name

    def __repr__(self):
        return "<Site {0}>".format(str(self))

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        Network = get_model('network', 'network')
        networks = Network.objects.filter(range__in=ctnr.ranges.all())
        objects = objects or Site.objects
        return objects.filter(network__in=networks)

    def details(self):
        """For tables."""
        data = super(Site, self).details()
        data['data'] = (
            ('Name', 'name', self),
            ('Parent', 'parent', self.parent),
        )
        return data

    @staticmethod
    def eg_metadata():
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'name', 'datatype': 'string', 'editable': True},
            {'name': 'parent', 'datatype': 'string', 'editable': False},
        ]}

    def get_full_name(self):
        if self.parent is not None:
            return (self.parent.get_full_name() + "/" + self.name).title()
        else:
            return self.name.title()

    def get_site_path(self):
        full_name = self.name
        target = self
        while True:
            if target.parent is None:
                break
            else:
                full_name = target.name + '.' + target.parent.name
                target = target.parent
        return full_name

    def get_related_networks(self, related_sites):
        from cyder.cydhcp.network.models import Network
        networks = set()
        for site in related_sites:
            root_networks = Network.objects.filter(site=site)
            for network in root_networks:
                networks.update(network.get_related_networks())
        return networks

    def get_related_sites(self):
        related_sites = Site.objects.filter(parent=self)
        sites = set(related_sites)
        sites.update([self])
        while related_sites:
            sub_sites = set()
            for site in related_sites:
                sub_sites.update(Site.objects.filter(parent=site))
            related_sites = sub_sites
            sites.update(set(related_sites))
        return sites

    def get_related_vlans(self, related_networks):
        return set([network.vlan for network in related_networks])

    def get_related(self):
        related_sites = self.get_related_sites()
        related_networks = self.get_related_networks(related_sites)
        related_vlans = self.get_related_vlans(related_networks)
        return [related_sites, related_networks, related_vlans]

    def compile_Q(self):
        """Compile a Django Q that will match any IP inside this site."""
        return networks_to_Q(self.network_set.all())


class SiteAV(EAVBase):
    class Meta:
        db_table = 'site_av'
        unique_together = ('site', 'attribute')


    site = models.ForeignKey(Site)
    attribute = models.ForeignKey(Attribute,
            limit_choices_to={'attribute_type': ATTRIBUTE_INFORMATIONAL})
