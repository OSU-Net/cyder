from django.db import models
from django.core.exceptions import ValidationError

from cyder.base.mixins import ObjectUrlMixin
from cyder.cydhcp.keyvalue.models import KeyValue


class Site(models.Model, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    parent = models.ForeignKey("self", null=True, blank=True)

    def details(self):
        return (
            ('Name', self.get_full_name()),
        )

    def get_full_name(self):
        full_name = self.name
        target = self
        while True:
            if target.parent is None:
                break
            else:
                full_name = target.parent.name + " " + target.name
                target = target.parent
        return full_name.title()

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
        networks = set()
        for site in related_sites:
            root_networks = Network.objects.filter(site=site)
            networks.update(network.get_related_networks())
            for network in root_networks:
                networks.update(network.get_related_networks())
        return networks

    def get_related_sites(self):
        related_sites = Site.objects.filter(parent=self)
        sites = set(related_sites)
        while related_sites:
            sub_sites = set()
            for site in related_sites:
                sub_sites.update(set(Site.objects.filter(parent=site)))
            related_sites = sub_sites
            sites.update(set(related_sites))
        return sites

    def get_related(self):
        related_sites = self.get_related_sites()
        related_networks =  self.get_related_networks(related_sites)
        return [related_sites, related_networks]

    class Meta:
        db_table = 'site'
        unique_together = ('name', 'parent')

    def __str__(self):
        return "{0}".format(self.get_full_name())

    def __repr__(self):
        return "<Site {0}>".format(str(self))


class SiteKeyValue(KeyValue):
    site = models.ForeignKey(Site, null=False)

    class Meta:
        db_table = 'site_key_value'
        unique_together = ('key', 'value')

    def _aa_address(self):
        # Everything is valid
        return

    def _aa_description(self):
        return
