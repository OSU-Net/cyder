from django.db import models
from django.core.exceptions import ValidationError

from cyder.cydns.validation import validate_ip_type
from cyder.cydns.ip.models import ipv6_to_longs
from cyder.core.utils import IPFilter, two_to_four
from cyder.core.vlan.models import Vlan
from cyder.core.site.models import Site
from cyder.core.mixins import ObjectUrlMixin
from cyder.core.keyvalue.models import KeyValue
from cyder.core.keyvalue.base_option import CommonOption

import ipaddr
import pdb


class Network(models.Model, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)
    vlan = models.ForeignKey(Vlan, null=True,
                             blank=True, on_delete=models.SET_NULL)
    site = models.ForeignKey(Site, null=True,
                             blank=True, on_delete=models.SET_NULL)

    # NETWORK/NETMASK FIELDS
    IP_TYPE_CHOICES = (('4', 'ipv4'), ('6', 'ipv6'))
    ip_type = models.CharField(max_length=1, choices=IP_TYPE_CHOICES,
                               editable=True, validators=[validate_ip_type])
    ip_upper = models.BigIntegerField(null=False, blank=True)
    ip_lower = models.BigIntegerField(null=False, blank=True)
    # This field is here so ES can search this model easier.
    network_str = models.CharField(max_length=49, editable=True,
                                   help_text="The network address of this network.")
    prefixlen = models.PositiveIntegerField(null=False,
                                            help_text="The number of binary 1's in the netmask.")

    dhcpd_raw_include = models.TextField(null=True, blank=True, help_text="The"
                                         " config options in this box will be included *as is* in the "
                                         "dhcpd.conf file for this subnet.")

    network = None

    def details(self):
        return (
            ('Network', self.network_str),
        )

    class Meta:
        db_table = 'network'
        unique_together = ('ip_upper', 'ip_lower', 'prefixlen')

    def save(self, *args, **kwargs):
        if not self.pk:
            add_routers = True
        else:
            add_routers = False
        self.update_network()
        super(Network, self).save(*args, **kwargs)

        self.update_network()  # Gd forbid this hasn't already been called.
        if add_routers:
            if self.ip_type == '4':
                router = str(ipaddr.IPv4Address(int(self.network.network) + 1))
            else:
                router = str(ipaddr.IPv6Address(int(self.network.network) + 1))
            kv = NetworkKeyValue(key="routers", value=router, network=self)
            #kv.clean()
            #kv.save()

    def delete(self, *args, **kwargs):
        if self.range_set.all().exists():
            raise ValidationError("Cannot delete this network because it has "
                                  "child ranges")
        super(Network, self).delete(*args, **kwargs)

    def check_valid_site(self):
        from cyder.core.network.utils import calc_networks, calc_parent
        self.update_network()
        # If the network contains or is contained in another network make sure
        # that they share a parent
        fail = False
        child_networks , parent_networks = calc_networks(self)
        for parent_network in parent_networks:
            if calc_parent(parent_network) != calc_parent(self):
                fail = True
        for child_network in child_networks:
            if calc_parent(child_network) != calc_parent(self):
                fail = True
        return fail

    def check_valid_range(self):
        # Look at all ranges that claim to be in this subnet, are they actually
        # in the subnet?
        self.update_network()
        fail = False
        for range_ in self.range_set.all():
            """
                I was writing checks to make sure that subnets wouldn't orphan
                ranges. IPv6 needs support.
            """
            # Check the start addresses.
            if range_.start_upper < self.ip_upper:
                fail = True
            elif (range_.start_upper > self.ip_upper and range_.start_lower <
                  self.ip_lower):
                fail = True
            elif (range_.start_upper == self.ip_upper and range_.start_lower
                    < self.ip_lower):
                fail = True

            if self.ip_type == '4':
                brdcst_upper, brdcst_lower = 0, int(self.network.broadcast)
            else:
                brdcst_upper, brdcst_lower = ipv6_to_longs(str(
                    self.network.broadcast))

            # Check the end addresses.
            if range_.end_upper > brdcst_upper:
                fail = True
            elif (range_.end_upper < brdcst_upper and range_.end_lower >
                  brdcst_lower):
                fail = True
            elif (range_.end_upper == brdcst_upper and range_.end_lower
                    > brdcst_lower):
                fail = True
        return fail

    def clean(self):
        ranges_invalid = self.check_valid_range()
        sites_invalid = self.check_valid_site()
        if ranges_invalid:
            raise ValidationError("Resizing this subnet to the requested "
                                  "network prefix would orphan existing ranges.")
        if sites_invalid:
            raise ValidationError("This network has child or parent networks"
                                  "which have different parent sites")

    def update_ipf(self):
        """Update the IP filter. Used for compiling search queries and firewall
        rules."""
        self.update_network()
        ip_info = two_to_four(
            int(self.network.network), int(self.network.broadcast))
        self.ipf = IPFilter(self, self.ip_type, *ip_info)

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
        except (ipaddr.AddressValueError, ipaddr.NetmaskValueError), e:
            raise ValidationError("Invalid network for ip type of "
                                  "'{0}'.".format(self, self.ip_type))
        # Update fields
        self.ip_upper = int(self.network) >> 64
        self.ip_lower = int(self.network) & (1 << 64) - 1  # Mask off
                                                     # the last sixty-four bits
        self.prefixlen = self.network.prefixlen

    def __str__(self):
        return self.network_str

    def __repr__(self):
        return "<Network {0}>".format(str(self))


class NetworkKeyValue(CommonOption):
    network = models.ForeignKey(Network, null=False)
    aux_attrs = (
        ('description', 'A description of the site'),
    )

    class Meta:
        db_table = 'network_key_value'
        unique_together = ('key', 'value', 'network')

    """The NetworkOption Class.

        "DHCP option statements always start with the option keyword, followed
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

    def _aa_filename(self):
        """
        filename filename;

            The filename statement can be used to specify the name of the
            initial boot file which is to be loaded by a client. The filename
            should be a filename recognizable to whatever file transfer
            protocol the client can be expected to use to load the file.
        """
        self.is_statement = True
        self.is_option = False
        self.has_validator = True
        # Anything else?

    def _aa_next_server(self):
        """
        The next-server statement

            next-server server-name;

            The next-server statement is used to specify the host address
            of the server from which the initial boot file (specified in
            the filename statement) is to be loaded. Server-name should be
            a numeric IP address or a domain name. If no next-server
            parameter applies to a given client, the DHCP server's IP
            address is used.
        """
        self.has_validator = True
        self.is_statement = True
        self.is_option = False
        self._single_ip(self.network.ip_type)

    def _aa_dns_servers(self):
        """A list of DNS servers for this network."""
        self.is_statement = False
        self.is_option = False
        self._ip_list(self.network.ip_type)

    def _aa_routers(self):
        self._routers(self.network.ip_type)

    def _aa_ntp_servers(self):
        self._ntp_servers(self.network.ip_type)
