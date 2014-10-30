from django.db import models
from django.db.models.loading import get_model
from django.core.validators import RegexValidator

from cyder.base.eav.constants import ATTRIBUTE_INVENTORY
from cyder.base.eav.fields import EAVAttributeField
from cyder.base.eav.models import Attribute, EAVBase
from cyder.base.mixins import ObjectUrlMixin
from cyder.base.models import BaseModel
from cyder.base.utils import transaction_atomic
from cyder.cydhcp.utils import networks_to_Q


class Site(BaseModel, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255,
                            validators=[RegexValidator('^[^/]+$')])
    parent = models.ForeignKey("self", null=True, blank=True,
                               verbose_name="Parent site")

    search_fields = ('name', 'parent__name')
    display_fields = ('name',)

    class Meta:
        app_label = 'cyder'
        db_table = 'site'
        unique_together = ('name', 'parent')

    def __str__(self):
        if self.parent:
            return "%s in %s" % (self.name, self.parent.get_full_name())
        else:
            return self.name

    def __repr__(self):
        return "<Site {0}>".format(str(self))

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        Network = get_model('cyder', 'network')
        networks = Network.objects.filter(range__in=ctnr.ranges.all())
        objects = objects or Site.objects
        return objects.filter(network__in=networks)

    def check_in_ctnr(self, ctnr):
        return self.network_set.filter(range__in=ctnr.ranges.all()).exists()

    def details(self):
        """For tables."""
        data = super(Site, self).details()
        data['data'] = (
            ('Name', 'name', self),
            ('Parent', 'parent', self.parent),
        )
        return data

    @transaction_atomic
    def save(self, *args, **kwargs):
        self.full_clean()

        super(Site, self).save(*args, **kwargs)

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

    @staticmethod
    def get_related_networks(sites):
        from cyder.cydhcp.network.models import Network
        networks = set()
        for site in sites:
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

    @staticmethod
    def get_related_vlans(networks):
        return set([network.vlan for network in networks])

    def get_related(self):
        related_sites = self.get_related_sites()
        related_networks = Site.get_related_networks(related_sites)
        related_vlans = Site.get_related_vlans(related_networks)
        return [related_sites, related_networks, related_vlans]

    def compile_Q(self):
        """Compile a Django Q that will match any IP inside this site."""
        return networks_to_Q(self.network_set.all())


class SiteAV(EAVBase):
    class Meta(EAVBase.Meta):
        app_label = 'cyder'
        db_table = 'site_av'

    entity = models.ForeignKey(Site)
    attribute = EAVAttributeField(Attribute,
        type_choices=(ATTRIBUTE_INVENTORY,))
