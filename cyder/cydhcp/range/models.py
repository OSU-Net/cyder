from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponse

from cyder.base.mixins import ObjectUrlMixin
from cyder.base.constants import IP_TYPES
from cyder.cydhcp.constants import *
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.utils import IPFilter, four_to_two
from cyder.cydhcp.keyvalue.utils import AuxAttr
from cyder.cydhcp.keyvalue.base_option import CommonOption
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.ip.models import ipv6_to_longs
from cyder.cydns.ptr.models import PTR

import ipaddr
# import reversion


class Range(models.Model, ObjectUrlMixin):
    """The Range class.

        >>> Range(start=start_ip, end=end_ip,
        >>>         defualt_domain=domain, network=network)

    Ranges live inside networks; their start ip address is greater than or
    equal to the the start of their network and their end ip address is less
    than or equal to the end of their network; both the Range and the network
    class enforce these requirements. Good practice says ranges should not
    start on the network address of their network and they should not end on
    the broadcast address of their network; the Range and Network classes do
    not enforce this.

    Changing a Range

    Things that happen when a static range is changed:

        *   The new `start` and `end` values are checked against the range's
            network to ensure that the range still exists within the network.
        *   The new `start` and `end` values are checked against all other
            existing range's `start` and `end` values to make sure that the new
            range does not overlap.
    """
    id = models.AutoField(primary_key=True)

    ip_type = models.CharField(max_length=1, choices=IP_TYPES.items())
    start_upper = models.BigIntegerField(null=True)
    start_lower = models.BigIntegerField(null=True)
    start_str = models.CharField(max_length=39, editable=True)

    end_lower = models.BigIntegerField(null=True)
    end_upper = models.BigIntegerField(null=True)
    end_str = models.CharField(max_length=39, editable=True)

    network = models.ForeignKey(Network, null=True, blank=True)
    is_reserved = models.BooleanField(default=False, blank=False)

    allow = models.CharField(max_length=20, choices=ALLOW_OPTIONS.items(),
                             null=True, blank=True)
    deny = models.CharField(max_length=20, choices=DENY_OPTIONS.items(),
                            null=True, blank=True)

    attrs = None
    dhcpd_raw_include = models.TextField(null=True, blank=True)

    range_type = models.CharField(max_length=2, choices=RANGE_TYPE.items(),
                                  default=STATIC, editable=False)

    search_fields = ('start_str', 'end_str')

    class Meta:
        db_table = 'range'
        unique_together = ('start_upper', 'start_lower', 'end_upper',
                           'end_lower')

    def __str__(self):
        return "{0}  -  {1}".format(self.start_str, self.end_str)

    def __repr__(self):
        return "<Range: {0}>".format(str(self))

    def update_attrs(self):
        self.attrs = AuxAttr(RangeKeyValue, self, "range")

    def _range_ips(self):
        self._start, self._end = four_to_two(
            self.start_upper,
            self.start_lower,
            self.end_upper,
            self.end_lower)

    def details(self):
        """For tables."""
        data = super(Range, self).details()
        has_net = self.network is not None
        data['data'] = [
            ('Range', 'start_str', self),
            ('Network', 'network', self.network if has_net else ""),
            ('Site', 'network__site', self.network.site if has_net else ""),
            ('Vlan', 'network__vlan', self.network.vlan if has_net else "")]
        return data

    def eg_metadata(self):
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'start_str', 'datatype': 'string', 'editable': False},
            {'name': 'network', 'datatype': 'string', 'editable': False},
            {'name': 'site', 'datatype': 'string', 'editable': False},
            {'name': 'vlan', 'datatype': 'string', 'editable': False},
        ]}

    def save(self, *args, **kwargs):
        self.clean()
        super(Range, self).save(*args, **kwargs)

    def clean(self):
        if self.network is None and not self.is_reserved:
            raise ValidationError("ERROR: Range {0}-{1} is not associated "
                                  "with a network and is not reserved".format(
                                  self.start_str, self.end_str))
        try:
            if self.ip_type == '4':
                self.start_upper, self.start_lower = 0, int(
                    ipaddr.IPv4Address(self.start_str))
                self.end_upper, self.end_lower = 0, int(
                    ipaddr.IPv4Address(self.end_str))
            elif self.ip_type == '6':
                self.start_upper, self.start_lower = ipv6_to_longs(
                    self.start_str)
                self.end_upper, self.end_lower = ipv6_to_longs(self.end_str)
            else:
                raise ValidationError("ERROR: could not determine the ip type")
        except ipaddr.AddressValueError, e:
            raise ValidationError(str(e))
        """
        Some notes:
        start = s1 s2
        end = e1 e2

        if s1 > e1:
            start > end
            # Bad
        if e1 > s1:
            end > start
            # Good
        if s1 == e1 and s2 > e2:
            start > end
            # Bad
        if s1 == e1 and s2 < e2:
            end > start
            # Good
        if s1 == e1 and s2 == e2:
            end == start
            # Bad
        """
        start, end = four_to_two(
            self.start_upper, self.start_lower, self.end_upper, self.end_lower)
        if start > end:
            raise ValidationError("The start of a range cannot be greater than"
                                  " or equal to the end of the range.")
        if not self.is_reserved:
            self.network.update_network()
            if self.network.ip_type == '4':
                IPClass = ipaddr.IPv4Address
            else:
                IPClass = ipaddr.IPv6Address

            if IPClass(self.start_str) < self.network.network.network or \
                    IPClass(self.end_str) > self.network.network.broadcast:
                raise RangeOverflowError(
                    "Range {0} to {1} doesn't fit in {2}".format(
                        IPClass(self.start_lower),
                        IPClass(self.end_lower),
                        self.network.network))
        self.check_for_overlaps()

    def check_for_overlaps(self):
        """This function will look at all the other ranges and make sure we
        don't overlap with any of them.
        """
        self._range_ips()
        Ip = ipaddr.IPv4Address if self.ip_type == '4' else ipaddr.IPv6Address
        for range in Range.objects.all():
            if range.pk == self.pk:
                continue
            range._range_ips()
            #the range being tested is above this range
            if self._start > range._end:
                continue
            # start > end
            if self._end < range._start:
                continue
            raise ValidationError("Stored range {0} - {1} would contain "
                                  "{2} - {3}".format(
                                      Ip(range._start),
                                      Ip(range._end),
                                      Ip(self._start),
                                      Ip(self._end)))

    def update_ipf(self):
        """Update the IP filter. Used for compiling search queries and firewall
        rules."""
        self.ipf = IPFilter(self.start_str, self.end_str, self.network.ip_type,
                            object_=self)

    def display(self):
        return "Range: {3} to {4} {0} -- {2} -- {1}".format(
            self.network.site, self.network.vlan, self.network,
            self.start_str, self.end_str)

    def choice_display(self):
        if not self.network.site:
            site_name = "No Site"
        else:
            site_name = self.network.site.name.upper()

        if not self.network.vlan:
            vlan_name = "No Vlan"
        else:
            vlan_name = str(self.network.vlan)
        return "{0} - {1} - ({2}) {3} to {4}".format(
            site_name, vlan_name,
            self.network, self.start_str, self.end_str)

    def get_next_ip(self):
        """Find's the most appropriate ip address within a range. If it can't
        find an IP it returns None. If it finds an IP it returns an IPv4Address
        object.

            :returns: ipaddr.IPv4Address
        """
        if self.network.ip_type is not '4':
            return None
        start = self.start_lower
        end = self.end_lower
        if start >= end - 1:
            return HttpResponse("Too small of a range.")
        ip = find_free_ip(start, end, ip_type='4')
        if ip:
            return ip
        else:
            return None


def find_free_ip(start, end, ip_type='4'):
    """Given start and end numbers, find a free ip.
    :param start: The start number
    :type start: int
    :param end: The end number
    :type end: int
    :param ip_type: The type of IP you are looking for.
    :type ip_type: str either '4' or '6'
    """
    if ip_type == '4':
        records = AddressRecord.objects.filter(ip_upper=0, ip_lower__gte=start,
                                               ip_lower__lte=end)
        ptrs = PTR.objects.filter(ip_upper=0, ip_lower__gte=start,
                                  ip_lower__lte=end)
        intrs = StaticInterface.objects.filter(ip_upper=0, ip_lower__gte=start,
                                               ip_lower__lte=end)
        if not records and not intrs:
            ip = ipaddr.IPv4Address(start)
            return ip
        for i in xrange(start, end + 1):
            taken = False
            for record in records:
                if record.ip_lower == i:
                    taken = True
                    break
            for ptr in ptrs:
                if ptr.ip_lower == i:
                    taken = True
                    break
            if not taken:
                for intr in intrs:
                    if intr.ip_lower == i:
                        taken = True
                        break
            if not taken:
                ip = ipaddr.IPv4Address(i)
                return ip
    else:
        raise NotImplemented


# reversion.(Range)


class RangeKeyValue(CommonOption):
    range = models.ForeignKey(Range, null=False)

    class Meta:
        db_table = 'range_key_value'
        unique_together = ('key', 'value', 'range')

    def _aa_failover(self):
        self.is_statement = True
        self.is_option = False
        if self.value != "peer \"dhcp-failover\"":
            raise ValidationError("Invalid failover option. Try `peer "
                                  "\"dhcp-failover\"`")

    def _aa_routers(self):
        self._routers(self.range.network.ip_type)

    def _aa_ntp_servers(self):
        self._ntp_servers(self.range.network.ip_type)

# reversion.(RangeKeyValue)


class RangeOverflowError(ValidationError):
    pass
