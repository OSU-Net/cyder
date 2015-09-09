from django.db import models
from django.core.exceptions import ValidationError

from cyder.base.eav.fields import EAVAttributeField
from cyder.base.eav.models import Attribute, EAVBase
from cyder.base.utils import transaction_atomic
from cyder.cydhcp.network.models import BaseNetwork
from cyder.cydhcp.validation import get_total_overlap


class Supernet(BaseNetwork):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=1000, blank=True)

    network = None

    search_fields = ('network_str', 'name', 'description')
    sort_fields = ('',)

    class Meta:
        app_label = 'cyder'
        db_table = 'supernet'
        unique_together = ('start_upper', 'start_lower')

    def __unicode__(self):
        return self.network_str

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        objects = objects or Supernet.objects
        return objects

    def check_in_ctnr(self, ctnr):
        return True

    def details(self):
        """For tables."""
        data = super(Supernet, self).details()
        data['data'] = (
            ('Name', 'name', self.name),
            ('Supernet', 'start_lower', self),
        )
        return data

    @transaction_atomic
    def save(self, *args, **kwargs):
        self.full_clean()
        super(Supernet, self).save(*args, **kwargs)

    def full_clean(self, *args, **kwargs):
        self.update_network()
        super(Supernet, self).full_clean(*args, **kwargs)

    @property
    def networks(self):
        return get_total_overlap(self)

    def contains(self, network):
        contained = (
            (self.start_upper < network.start_upper or
                (self.start_upper == network.start_upper and
                 self.start_lower <= network.start_lower)) and
            (self.end_upper > network.end_upper or
                (self.end_upper == network.end_upper and
                 self.end_lower >= network.end_lower)))
        return contained


class SupernetAV(EAVBase):
    class Meta(EAVBase.Meta):
        app_label = 'cyder'
        db_table = 'supernet_av'

    entity = models.ForeignKey(Supernet)
    attribute = EAVAttributeField(Attribute)
