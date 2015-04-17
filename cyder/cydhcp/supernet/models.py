import ipaddr

from django.db import models
from django.core.exceptions import ValidationError

from cyder.base.constants import IP_TYPES, IP_TYPE_4, IP_TYPE_6
from cyder.base.eav.fields import EAVAttributeField
from cyder.base.eav.models import Attribute, EAVBase
from cyder.base.mixins import ObjectUrlMixin
from cyder.base.models import BaseModel
from cyder.base.utils import transaction_atomic
from cyder.cydns.validation import validate_ip_type


class Supernet(BaseModel, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)

    ip_type = models.CharField(
        verbose_name='IP address type', max_length=1,
        choices=IP_TYPES.items(), default=IP_TYPE_4,
        validators=[validate_ip_type]
    )
    ip_upper = models.BigIntegerField(null=False, blank=True)
    ip_lower = models.BigIntegerField(null=False, blank=True)
    network_str = models.CharField(
        max_length=49, editable=True,
        help_text='Network address and prefix length, in CIDR notation',
        verbose_name='Network string')
    prefixlen = models.PositiveIntegerField(
        null=False, help_text="The number of binary 1's in the netmask.")

    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=1000, blank=True)

    network = None

    search_fields = ('',)
    sort_fields = ('',)

    class Meta:
        app_label = 'cyder'
        db_table = 'supernet'
        unique_together = ('ip_upper', 'ip_lower', 'prefixlen')

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
            ('Supernet', 'ip_lower', self),
        )
        return data

    @transaction_atomic
    def save(self, *args, **kwargs):
        self.full_clean()
        super(Supernet, self).save(*args, **kwargs)

    def full_clean(self, *args, **kwargs):
        self.update_network()
        super(Supernet, self).full_clean(*args, **kwargs)

    def update_network(self):
        """This function will look at the value of network_str to update other
        fields in the network object. This function will also set the 'network'
        attribute to either an ipaddr.IPv4Network or ipaddr.IPv6Network object.
        """
        if not isinstance(self.network_str, basestring):
            raise ValidationError("ERROR: No network str.")
        try:
            if self.ip_type == IP_TYPE_4:
                self.network = ipaddr.IPv4Network(self.network_str).masked()
            elif self.ip_type == IP_TYPE_6:
                self.network = ipaddr.IPv6Network(self.network_str).masked()
            else:
                raise ValidationError("Could not determine IP type of network"
                                      " %s" % (self.network_str))
        except (ipaddr.AddressValueError, ipaddr.NetmaskValueError), e:
            raise ValidationError('Invalid IPv{0} network: {1}'
                                  .format(self.ip_type, e))
        # Update fields
        self.ip_upper = int(self.network) >> 64
        self.ip_lower = int(self.network) & (1 << 64) - 1
        self.prefixlen = self.network.prefixlen
        self.network_str = str(self.network)


class SupernetAV(EAVBase):
    class Meta(EAVBase.Meta):
        app_label = 'cyder'
        db_table = 'supernet_av'

    entity = models.ForeignKey(Supernet)
    attribute = EAVAttributeField(Attribute)
