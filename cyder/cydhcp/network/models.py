import ipaddr

from django.db import models
from django.core.exceptions import ValidationError

from cyder.base.constants import IP_TYPES, IP_TYPE_4, IP_TYPE_6
from cyder.base.eav.constants import ATTRIBUTE_OPTION, ATTRIBUTE_STATEMENT
from cyder.base.eav.fields import EAVAttributeField
from cyder.base.eav.models import Attribute, EAVBase
from cyder.base.mixins import ObjectUrlMixin
from cyder.base.helpers import get_display
from cyder.base.models import BaseModel
from cyder.cydhcp.constants import DYNAMIC
from cyder.cydhcp.utils import IPFilter, join_dhcp_args
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydhcp.site.models import Site
from cyder.cydns.validation import validate_ip_type
from cyder.cydns.ip.models import ipv6_to_longs

# import reversion


class Network(BaseModel, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)
    vlan = models.ForeignKey(Vlan, null=True,
                             blank=True, on_delete=models.SET_NULL)
    site = models.ForeignKey(Site, null=True,
                             blank=True, on_delete=models.SET_NULL)
    vrf = models.ForeignKey('cyder.Vrf',
                            default=lambda: Vrf.objects.get(name='Legacy'))

    # NETWORK/NETMASK FIELDS
    ip_type = models.CharField(
        verbose_name='IP address type', max_length=1,
        choices=IP_TYPES.items(), default=IP_TYPE_4,
        validators=[validate_ip_type]
    )
    ip_upper = models.BigIntegerField(null=False, blank=True)
    ip_lower = models.BigIntegerField(null=False, blank=True)
    # This field is here so ES can search this model easier.
    network_str = models.CharField(
        max_length=49, editable=True,
        help_text="The network address of this network.",
        verbose_name="Network address")
    prefixlen = models.PositiveIntegerField(
        null=False, help_text="The number of binary 1's in the netmask.")
    enabled = models.BooleanField(default=True)
    dhcpd_raw_include = models.TextField(
        blank=True,
        help_text="The config options in this box will be included "
                  "*as is* in the dhcpd.conf file for this subnet.")
    network = None

    search_fields = ('vlan__name', 'site__name', 'network_str')
    display_fields = ('network_str',)

    class Meta:
        app_label = 'cyder'
        db_table = 'network'
        unique_together = ('ip_upper', 'ip_lower', 'prefixlen')

    def __str__(self):
        return get_display(self)

    def __repr__(self):
        return "<Network {0}>".format(str(self))

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        objects = objects or Network.objects
        return objects.filter(range__in=ctnr.ranges.all())

    def details(self):
        """For tables."""
        data = super(Network, self).details()
        data['data'] = (
            ('Network', 'network_str', self),
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

    def save(self, *args, **kwargs):
        self.update_network()
        super(Network, self).save(*args, **kwargs)

        #if (self.pk is None and
                #not self.networkkeyvalue_set.filter(key='routers').exists()):
            #if self.ip_type == IP_TYPE_4:
                #router = str(
                #    ipaddr.IPv4Address(int(self.network.network) + 1))
            #else:
                #router = str(
                #   ipaddr.IPv6Address(int(self.network.network) + 1))

            #eav = NetworkAV(attribute=Attribute.objects.get(name="routers"),
                            #value=router, network=self)
            #eav.clean()
            #eav.save()

    def delete(self, *args, **kwargs):
        if self.range_set.all().exists():
            raise ValidationError("Cannot delete this network because it has "
                                  "child ranges")
        super(Network, self).delete(*args, **kwargs)

    def full_clean(self, *args, **kwargs):
        self.update_network()
        super(Network, self).full_clean(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.check_valid_range()
        allocated = Network.objects.filter(prefixlen=self.prefixlen,
                                           ip_upper=self.ip_upper,
                                           ip_lower=self.ip_lower)
        if allocated:
            if not self.id or self not in allocated:
                raise ValidationError(
                    "This network has already been allocated.")

        super(Network, self).clean(*args, **kwargs)

    def check_valid_range(self):
        # Look at all ranges that claim to be in this subnet, are they actually
        # in the subnet?
        self.update_network()
        fail = False
        for range_ in self.range_set.all():
            # TODO
            """
                I was writing checks to make sure that subnets wouldn't orphan
                ranges. IPv6 needs support.
            """
            # Check the start addresses.
            if range_.start_upper < self.ip_upper:
                fail = True
                break
            elif (range_.start_upper > self.ip_upper and range_.start_lower <
                  self.ip_lower):
                fail = True
                break
            elif (range_.start_upper == self.ip_upper and range_.start_lower <
                    self.ip_lower):
                fail = True
                break

            if self.ip_type == IP_TYPE_4:
                brdcst_upper, brdcst_lower = 0, int(self.network.broadcast)
            else:
                brdcst_upper, brdcst_lower = ipv6_to_longs(str(
                    self.network.broadcast))

            # Check the end addresses.
            if range_.end_upper > brdcst_upper:
                fail = True
                break
            elif (range_.end_upper < brdcst_upper and range_.end_lower >
                    brdcst_lower):
                fail = True
                break
            elif (range_.end_upper == brdcst_upper and range_.end_lower
                    > brdcst_lower):
                fail = True

            if fail:
                raise ValidationError("Resizing this subnet to the requested "
                                      "network prefix would orphan existing "
                                      "ranges.")

    def update_ipf(self):
        """Update the IP filter. Used for compiling search queries and firewall
        rules."""
        self.update_network()
        self.ipf = IPFilter(self.network.network, self.network.broadcast,
                            self.ip_type, object_=self)

    def get_related_vlans(self, related_networks):
        return set([network.vlan for network in related_networks])

    def get_related_networks(self):
        from cyder.cydhcp.network.utils import calc_networks
        _, related_networks = calc_networks(self)
        networks = set(related_networks)
        networks.update([self])
        while related_networks:
            subnets = set()
            for network in related_networks:
                _, sub_networks = calc_networks(network)
                subnets.update(set(sub_networks))
            networks.update(subnets)
            related_networks = subnets
        return networks

    def get_related_sites(self, related_networks):
        return set([network.site for network in related_networks])

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
                build_str += join_dhcp_args(self.dhcpd_raw_include.split("\n"))
        for range_ in ranges:
            build_str += range_.build_range()
        build_str += "}\n"
        return build_str

    def get_related(self):
        related_networks = self.get_related_networks()
        related_sites = self.get_related_sites(related_networks)
        return [related_sites, related_networks]

    def update_network(self):
        """This function will look at the value of network_str to update other
        fields in the network object. This function will also set the 'network'
        attribute to either an ipaddr.IPv4Network or ipaddr.IPv6Network object.
        """
        if not isinstance(self.network_str, basestring):
            raise ValidationError("ERROR: No network str.")
        try:
            if self.ip_type == IP_TYPE_4:
                self.network = ipaddr.IPv4Network(self.network_str)
            elif self.ip_type == IP_TYPE_6:
                self.network = ipaddr.IPv6Network(self.network_str)
            else:
                raise ValidationError("Could not determine IP type of network"
                                      " %s" % (self.network_str))
        except (ipaddr.AddressValueError, ipaddr.NetmaskValueError):
            raise ValidationError('Invalid IPv{0} network'
                                  .format(self.ip_type))
        # Update fields
        self.ip_upper = int(self.network) >> 64
        self.ip_lower = int(self.network) & (1 << 64) - 1  # Mask off
                                                    # the last sixty-four bits
        self.prefixlen = self.network.prefixlen


class NetworkAV(EAVBase):
    class Meta(EAVBase.Meta):
        app_label = 'cyder'
        db_table = 'network_av'


    entity = models.ForeignKey(Network)
    attribute = EAVAttributeField(Attribute)
