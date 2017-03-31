import ipaddr

from django.db import models
from django.core.exceptions import ValidationError

from cyder.base.constants import IP_TYPES, IP_TYPE_4, IP_TYPE_6
from cyder.base.eav.constants import ATTRIBUTE_OPTION, ATTRIBUTE_STATEMENT
from cyder.base.eav.fields import EAVAttributeField
from cyder.base.eav.models import Attribute, EAVBase
from cyder.base.mixins import ObjectUrlMixin
from cyder.base.models import BaseModel
from cyder.base.utils import transaction_atomic
from cyder.cydhcp.constants import DYNAMIC
from cyder.cydhcp.utils import IPFilter, join_dhcp_args
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.validation import (validate_network_overlap,
                                     get_partial_overlap)
from cyder.cydns.validation import validate_ip_type
from cyder.cydns.ip.models import ipv6_to_longs


class BaseNetwork(BaseModel, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)

    ip_type = models.CharField(
        verbose_name='IP address type', max_length=1,
        choices=IP_TYPES.items(), default=IP_TYPE_4,
        validators=[validate_ip_type]
    )
    start_upper = models.BigIntegerField(null=False, blank=True)
    start_lower = models.BigIntegerField(null=False, blank=True)
    end_upper = models.BigIntegerField(null=False, blank=True)
    end_lower = models.BigIntegerField(null=False, blank=True)
    network_str = models.CharField(
        max_length=49, editable=True,
        help_text='Network address and prefix length, in CIDR notation',
        verbose_name='Network string')

    class Meta:
        abstract = True

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
        self.start_upper = int(self.network.ip) >> 64
        self.start_lower = int(self.network.ip) % (2**64)
        self.end_upper = int(self.network.broadcast) >> 64
        self.end_lower = int(self.network.broadcast) % (2**64)
        self.network_str = str(self.network)

    def clean(self, *args, **kwargs):
        self.update_network()
        validate_network_overlap(self)
        super(BaseNetwork, self).clean(*args, **kwargs)


class Network(BaseNetwork):
    vlan = models.ForeignKey(Vlan, null=True,
                             blank=True, on_delete=models.SET_NULL)
    site = models.ForeignKey(Site, null=True,
                             blank=True, on_delete=models.SET_NULL)
    vrf = models.ForeignKey('cyder.Vrf', default=1)  # "Legacy"
    enabled = models.BooleanField(default=True)
    dhcpd_raw_include = models.TextField(
        blank=True,
        help_text="The config options in this box will be included "
                  "*as is* in the dhcpd.conf file for this subnet.")
    network = None

    search_fields = ('vlan__name', 'site__name', 'network_str',
                     'dhcpd_raw_include')
    sort_fields = ('start_lower',)

    class Meta:
        app_label = 'cyder'
        db_table = 'network'
        unique_together = ('start_upper', 'start_lower')

    def __unicode__(self):
        return self.network_str

    @property
    def supernets(self):
        from cyder.cydhcp.supernet.models import Supernet
        supernets = get_partial_overlap(self, netmodel=Supernet)
        return supernets

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        objects = objects or Network.objects
        return objects.filter(range__in=ctnr.ranges.all())

    def check_in_ctnr(self, ctnr):
        return self.range_set.filter(pk__in=ctnr.ranges.all()).exists()

    def details(self):
        """For tables."""
        data = super(Network, self).details()
        data['data'] = (
            ('Network', 'start_lower', self),
            ('Site', 'site', self.site),
            ('Vlan', 'vlan', self.vlan),
            ('Vrf', 'vrf', self.vrf),
        )
        return data

    @staticmethod
    def eg_metadata():
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'network_str', 'datatype': 'string', 'editable': True},
            {'name': 'site', 'datatype': 'string', 'editable': False},
            {'name': 'vlan', 'datatype': 'string', 'editable': False},
        ]}

    def __contains__(self, other):
        if self.ip_type is not other.ip_type:
            raise Exception("__contains__ is not defined for "
                            "IPv{0} and IPv{1}".format(
                            self.ip_type, other.ip_type))
        self.update_network()
        if type(other) is type(self):
            other.update_network()
            return self.network.network < other.network.network < \
                self.other.network.broadcast < self.network.broadcast
        else:
            other._range_ips()
            return self.network.network < other.network_address < \
                other.broadcast_address < self.broadcast_address

    def cyder_unique_error_message(self, model_class, unique_check):
        if unique_check == ('start_upper', 'start_lower'):
            return (
                'Network with this address already exists.')
        else:
            return super(Network, self).unique_error_message(
                model_class, unique_check)

    @transaction_atomic
    def save(self, *args, **kwargs):
        self.full_clean()

        super(Network, self).save(*args, **kwargs)

    @transaction_atomic
    def delete(self, *args, **kwargs):
        if self.range_set.exists():
            raise ValidationError("Cannot delete this network because it has "
                                  "child ranges")
        super(Network, self).delete(*args, **kwargs)

    def full_clean(self, *args, **kwargs):
        self.update_network()
        super(Network, self).full_clean(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.check_valid_range()
        super(Network, self).clean(*args, **kwargs)

    # TODO: I was writing checks to make sure that subnets wouldn't
    # orphan ranges. IPv6 needs support.
    def check_valid_range(self):
        # Look at all ranges that claim to be in this subnet, are they actually
        # in the subnet?
        self.update_network()
        for range_ in self.range_set.all():
            # Check the start addresses.
            if range_.start_upper < self.start_upper:
                break
            elif (range_.start_upper > self.start_upper and range_.start_lower <
                  self.start_lower):
                break
            elif (range_.start_upper == self.start_upper and range_.start_lower <
                    self.start_lower):
                break

            if self.ip_type == IP_TYPE_4:
                brdcst_upper, brdcst_lower = 0, int(self.network.broadcast)
            else:
                brdcst_upper, brdcst_lower = ipv6_to_longs(str(
                    self.network.broadcast))

            # Check the end addresses.
            if range_.end_upper > brdcst_upper:
                break
            elif (range_.end_upper < brdcst_upper and range_.end_lower >
                    brdcst_lower):
                break
            elif (range_.end_upper == brdcst_upper and range_.end_lower
                    > brdcst_lower):
                break
        else:  # All ranges are valid.
            return

        raise ValidationError(
            "Resizing this subnet to the requested network prefix would "
            "orphan existing ranges.")

    def update_ipf(self):
        """Update the IP filter. Used for compiling search queries and firewall
        rules."""
        self.update_network()
        self.ipf = IPFilter(self.network.network, self.network.broadcast,
                            self.ip_type, object_=self)

    @staticmethod
    def get_related_vlans(networks):
        return set([network.vlan for network in networks])

    def build_subnet(self, raw=False):
        self.update_network()
        statements = self.networkav_set.filter(
            attribute__attribute_type=ATTRIBUTE_STATEMENT)
        options = self.networkav_set.filter(
            attribute__attribute_type=ATTRIBUTE_OPTION)
        ranges = self.range_set.filter(range_type=DYNAMIC, dhcp_enabled=True)
        if self.ip_type == IP_TYPE_4:
            build_str = "\nsubnet {0} netmask {1} {{\n".format(
                self.network.network, self.network.netmask)
        else:
            build_str = "\nsubnet6 {0} netmask {1} {{\n".format(
                self.network.network, self.network.netmask)
        if not raw:
            build_str += "\t# Network statements\n"
            build_str += join_dhcp_args(statements)
            build_str += "\t# Network options\n"
            build_str += join_dhcp_args(options)
            if self.dhcpd_raw_include:
                build_str += "\t# Raw network options\n"
                for raw_line in self.dhcpd_raw_include.split("\n"):
                    build_str += "\t{0}\n".format(raw_line)
        for range_ in ranges:
            build_str += range_.build_range()
        build_str += "}\n"
        return build_str


class NetworkAV(EAVBase):
    class Meta(EAVBase.Meta):
        app_label = 'cyder'
        db_table = 'network_av'

    entity = models.ForeignKey(Network)
    attribute = EAVAttributeField(Attribute,
        type_choices=(ATTRIBUTE_OPTION, ATTRIBUTE_STATEMENT))
