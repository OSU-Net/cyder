import ipaddr

from django.db import models
from django.core.exceptions import ValidationError

from cyder.base.constants import IP_TYPES
from cyder.base.mixins import ObjectUrlMixin
from cyder.cydhcp.keyvalue.base_option import CommonOption
from cyder.cydhcp.utils import IPFilter
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.keyvalue.utils import AuxAttr
from cyder.cydhcp.site.models import Site
from cyder.cydns.validation import validate_ip_type
from cyder.cydns.ip.models import ipv6_to_longs

#import reversion


class Network(models.Model, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)
    vlan = models.ForeignKey(Vlan, null=True,
                             blank=True, on_delete=models.SET_NULL)
    site = models.ForeignKey(Site, null=True,
                             blank=True, on_delete=models.SET_NULL)

    # NETWORK/NETMASK FIELDS
    ip_type = models.CharField(max_length=1, choices=IP_TYPES.items(),
                               editable=True, validators=[validate_ip_type])
    ip_upper = models.BigIntegerField(null=False, blank=True)
    ip_lower = models.BigIntegerField(null=False, blank=True)
    # This field is here so ES can search this model easier.
    network_str = models.CharField(
        max_length=49, editable=True,
        help_text="The network address of this network.")
    prefixlen = models.PositiveIntegerField(
        null=False, help_text="The number of binary 1's in the netmask.")

    dhcpd_raw_include = models.TextField(
        null=True, blank=True,
        help_text="The config options in this box will be included "
                  "*as is* in the dhcpd.conf file for this subnet.")
    network = None

    search_fields = ('vlan__name', 'site__name', 'network_str')

    def __str__(self):
        return self.network_str

    def __repr__(self):
        return "<Network {0}>".format(str(self))

    def __contains__(self, other):
        if self.ip_type is not other.ip_type:
            raise Exception("__contains__ is not defined for "
                            "ip type {0} and ip type {1}".format(
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

    def update_attrs(self):
        self.attrs = AuxAttr(NetworkKeyValue, self, "network")

    def details(self):
        """For tables."""
        data = super(Network, self).details()
        data['data'] = (
            ('Network', 'network', self),
            ('Site', 'site', self.site),
            ('Vlan', 'vlan', self.vlan),
        )
        return data

    class Meta:
        db_table = 'network'
        unique_together = ('ip_upper', 'ip_lower', 'prefixlen')

    def save(self, *args, **kwargs):
        add_routers = True if not self.pk else False
        self.update_network()
        super(Network, self).save(*args, **kwargs)

        if add_routers:
            if self.ip_type == '4':
                router = str(ipaddr.IPv4Address(int(self.network.network) + 1))
            else:
                router = str(ipaddr.IPv6Address(int(self.network.network) + 1))

            kv = NetworkKeyValue(key="routers", value=router, network=self)
            kv.clean()
            kv.save()

    def delete(self, *args, **kwargs):
        if self.range_set.all().exists():
            raise ValidationError("Cannot delete this network because it has "
                                  "child ranges")
        super(Network, self).delete(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.check_valid_range()
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

            if self.ip_type == '4':
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
            if self.ip_type == '4':
                self.network = ipaddr.IPv4Network(self.network_str)
            elif self.ip_type == '6':
                self.network = ipaddr.IPv6Network(self.network_str)
            else:
                raise ValidationError("Could not determine IP type of network"
                                      " %s" % (self.network_str))
        except (ipaddr.AddressValueError, ipaddr.NetmaskValueError):
            raise ValidationError("Invalid network for ip type of "
                                  "'{0}'.".format(self, self.ip_type))
        # Update fields
        self.ip_upper = int(self.network) >> 64
        self.ip_lower = int(self.network) & (1 << 64) - 1  # Mask off
                                                    # the last sixty-four bits
        self.prefixlen = self.network.prefixlen


class NetworkKeyValue(CommonOption):
    network = models.ForeignKey(Network, null=False)
    aux_attrs = (
        ('description', 'A description of the network'),
    )

    class Meta:
        db_table = 'network_key_value'
        unique_together = ('key', 'value', 'network')

    """The NetworkOption Class.

        DHCP option statements always start with the option keyword, followed
        by an option name, followed by option data." -- The man page for
        dhcpd-options

        In this class, options are stored without the 'option' keyword. If it
        is an option, is option should be set.
    """

    def save(self, *args, **kwargs):
        self.clean()
        super(NetworkKeyValue, self).save(*args, **kwargs)

    def _aa_description(self):
        """A descrition of this network"""
        pass
