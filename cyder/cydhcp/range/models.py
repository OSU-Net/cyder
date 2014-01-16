# encoding=utf-8

from django.core.exceptions import ValidationError
from django.db import models

from cyder.base.constants import IP_TYPES, IP_TYPE_4, IP_TYPE_6
from cyder.base.eav.constants import ATTRIBUTE_OPTION, ATTRIBUTE_STATEMENT
from cyder.base.eav.fields import EAVAttributeField
from cyder.base.eav.models import Attribute, EAVBase
from cyder.base.mixins import ObjectUrlMixin
from cyder.base.models import BaseModel
from cyder.cydns.validation import validate_ip_type
from cyder.cydhcp.constants import (ALLOW_OPTIONS, ALLOW_ANY, ALLOW_KNOWN,
                                    ALLOW_LEGACY, ALLOW_VRF, RANGE_TYPE,
                                    STATIC, DYNAMIC)
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.utils import (IPFilter, four_to_two, join_dhcp_args,
                                start_end_filter)
from cyder.cydns.models import ViewMixin
from cyder.cydns.domain.models import Domain
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.ip.models import ipv6_to_longs
from cyder.cydns.ptr.models import PTR

import ipaddr


class Range(BaseModel, ViewMixin, ObjectUrlMixin):
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
    network = models.ForeignKey(Network, null=False, blank=False)

    range_type = models.CharField(max_length=2, choices=RANGE_TYPE,
                                  default=STATIC)

    ip_type = models.CharField(
        verbose_name='IP address type', max_length=1,
        choices=IP_TYPES.items(), default=IP_TYPE_4,
        validators=[validate_ip_type]
    )

    start_upper = models.BigIntegerField(null=True, editable=False)
    start_lower = models.BigIntegerField(null=True, editable=False)
    start_str = models.CharField(max_length=39, verbose_name="Start address")

    end_lower = models.BigIntegerField(null=True, editable=False)
    end_upper = models.BigIntegerField(null=True, editable=False)
    end_str = models.CharField(max_length=39, verbose_name="End address")

    domain = models.ForeignKey(Domain, null=True)

    is_reserved = models.BooleanField(default=False, blank=False)

    allow = models.CharField(max_length=1, choices=ALLOW_OPTIONS,
                             default=ALLOW_LEGACY)

    dhcpd_raw_include = models.TextField(blank=True)
    dhcp_enabled = models.BooleanField(default=True)

    name = models.CharField(blank=True, max_length=50)
    description = models.TextField(blank=True)

    allow_voip_phones = models.BooleanField(
        default=True, verbose_name='Allow VoIP phones')

    range_usage = models.IntegerField(max_length=3, null=True, blank=True)

    search_fields = ('start_str', 'end_str')
    display_fields = ('start_str', 'end_str')

    class Meta:
        app_label = 'cyder'
        db_table = 'range'
        unique_together = ('start_upper', 'start_lower', 'end_upper',
                           'end_lower')

    @property
    def range_str(self):
        return u'{0}-{1}'.format(self.start_str, self.end_str)

    @property
    def range_str_padded(self):
        s = u'{0:*>15} – {1:*<15}'.format(self.start_str, self.end_str)
        s = s.replace(u'*', u'\u00a0')
        return s

    def get_self_str(self, padded=False, add_usage=True, add_name=True):
        if padded:
            range_str = self.range_str_padded
        else:
            range_str = self.range_str

        if add_name:
            name = u' ' + self.name if self.name else u''
        else:
            name = u''

        if add_usage and self.range_usage is not None:
            if self.range_usage >= 100:
                usage = u'full'
            else:
                usage = u'{0}%'.format(str(self.range_usage))

            usage = u' ({0})'.format(usage)
        else:
            usage = u''

        return u''.join((range_str, name, usage))

    def __unicode__(self):
        return self.get_self_str(padded=True)

    def __repr__(self):
        return "<Range: {0}>".format(str(self))

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        if objects:
            return ctnr.ranges.filter(pk__in=objects)
        else:
            return ctnr.ranges

    @property
    def staticinterfaces(self):
        start, end = four_to_two(
            self.start_upper, self.start_lower, self.end_upper, self.end_lower)
        return StaticInterface.objects.filter(
            start_end_filter(start, end, self.ip_type)[2])

    def _range_ips(self):
        self._start, self._end = four_to_two(
            self.start_upper,
            self.start_lower,
            self.end_upper,
            self.end_lower)

    def details(self):
        """For tables."""
        data = super(Range, self).details()
        data['data'] = [
            ('Name', 'name', self.name),
            ('Range', 'start_str', self.get_self_str(add_name=False)),
            ('Domain', 'domain', self.domain),
            ('Type', 'range_type',
             'static' if self.range_type == 'st' else 'dynamic'),
            ('Network', 'network', self.network),
            ('Site', 'network__site', self.network.site),
            ('Vlan', 'network__vlan', self.network.vlan)]
        return data

    @staticmethod
    def eg_metadata():
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'start_str', 'datatype': 'string', 'editable': False},
            {'name': 'network', 'datatype': 'string', 'editable': False},
            {'name': 'site', 'datatype': 'string', 'editable': False},
            {'name': 'vlan', 'datatype': 'string', 'editable': False},
        ]}

    def save(self, *args, **kwargs):
        self.clean()
        update_range_usage = kwargs.pop('update_range_usage', True)
        if update_range_usage:
            self.range_usage = self.get_usage()
        super(Range, self).save(*args, **kwargs)

    def clean(self):
        try:
            if self.ip_type == IP_TYPE_4:
                self.start_upper, self.start_lower = 0, int(
                    ipaddr.IPv4Address(self.start_str))
                self.end_upper, self.end_lower = 0, int(
                    ipaddr.IPv4Address(self.end_str))
            elif self.ip_type == IP_TYPE_6:
                self.start_upper, self.start_lower = ipv6_to_longs(
                    self.start_str)
                self.end_upper, self.end_lower = ipv6_to_longs(self.end_str)
            else:
                raise ValidationError('Invalid IP type')
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
            raise ValidationError("The start of a range cannot be greater "
                                  "than the end of the range.")

        if (self.range_type == STATIC and
                self.dynamicinterface_set.filter(dhcp_enabled=True).exists()):
            raise ValidationError('A static range cannot contain dynamic '
                                  'interfaces')

        if self.range_type == DYNAMIC:
            if self.staticinterfaces.filter(dhcp_enabled=True).exists():
                raise ValidationError('A dynamic range cannot contain static '
                                      'interfaces')
            if not self.domain:
                raise ValidationError('A dynamic range must have a domain.')

        self.network.update_network()
        if self.network.ip_type == IP_TYPE_4:
            IPClass = ipaddr.IPv4Address
        else:
            IPClass = ipaddr.IPv6Address

        if (IPClass(self.start_str) < self.network.network.network or
                IPClass(self.end_str) > self.network.network.broadcast):
            raise RangeOverflowError("Range doesn't fit in network")

        self.check_for_overlaps()

    def get_allow_deny_list(self):
        if self.allow == ALLOW_ANY:
            allow = []
        elif self.allow == ALLOW_KNOWN:
            # FIXME: add hyphen once compatibility with Maintain is established
            allow = ['allow known clients']
            allow += ['allow members of "{0}:{1}:{2}"'.format(
                ctnr.name, self.start_str, self.end_str)
                for ctnr in self.ctnr_set.all()]
        else:
            allow = []
            if self.allow_voip_phones:
                allow += ['allow members of "VoIP"']
            if self.allow == ALLOW_VRF:
                allow += ['allow members of "{0}"'.format(
                    self.network.vrf.name)]
            if self.allow == ALLOW_LEGACY:
                allow += ['allow members of "{0}:{1}:{2}"'.format(
                    ctnr.name, self.start_str, self.end_str)
                    for ctnr in self.ctnr_set.all()]
            if not allow:
                allow += ['deny unknown-clients']

        return allow

    def check_for_overlaps(self):
        """
        This function will look at all the other ranges and make sure we don't
        overlap with any of them.
        """
        self._range_ips()

        for oldrange in Range.objects.all():
            if oldrange.pk == self.pk:
                continue
            oldrange._range_ips()
            #the range being tested is above this range
            if self._start > oldrange._end:
                continue
            # start > end
            if self._end < oldrange._start:
                continue
            raise ValidationError(u"Old range {0} would overlap with new "
                                  "range {1}".format(oldrange.range_str,
                                                     self.range_str))

    def build_range(self):
        range_options = self.rangeav_set.filter(
            attribute__attribute_type=ATTRIBUTE_OPTION)
        range_statements = self.rangeav_set.filter(
            attribute__attribute_type=ATTRIBUTE_STATEMENT)
        build_str = "\tpool {\n"
        build_str += "\t\t# Pool Statements\n"
        build_str += "\t\tfailover peer \"dhcp\";\n"
        build_str += "\t\tdeny dynamic bootp clients;\n"
        build_str += join_dhcp_args(range_statements, depth=2)
        if range_options:
            build_str += "\t\t# Pool Options\n"
            build_str += join_dhcp_args(range_options, depth=2)
        if self.dhcpd_raw_include:
            build_str += "\t\t# Raw pool includes\n"
            build_str += "\t\t{0};".format(self.dhcp_raw_include)
        build_str += "\t\t# Allow statements\n"
        build_str += join_dhcp_args(self.get_allow_deny_list(), depth=2)
        if self.ip_type == IP_TYPE_4:
            build_str += "\t\trange {0} {1};\n".format(self.start_str,
                                                       self.end_str)
        else:
            build_str += "\t\trange6{0} {1};\n".format(self.start_str,
                                                       self.end_str)
        build_str += "\t}\n\n"
        return build_str

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
            site_name = "No site"
        else:
            site_name = self.network.site.name.upper()

        if not self.network.vlan:
            vlan_name = "No VLAN"
        else:
            vlan_name = str(self.network.vlan)
        return "{0} - {1} - ({2}) {3} to {4}".format(
            site_name, vlan_name,
            self.network, self.start_str, self.end_str)

    def get_usage(self):
        if self.range_type == 'st':
            from cyder.cydhcp.range.range_usage import range_usage
            _, usage = range_usage(self.start_lower, self.end_lower,
                                   self.ip_type)
        else:
            DynamicInterface = models.get_model('cyder', 'dynamicinterface')
            used = float(DynamicInterface.objects.filter(
                range=self, dhcp_enabled=True).count())
            capacity = float(self.end_lower - self.start_lower + 1)
            usage = (used/capacity)*100

        return usage

    def get_next_ip(self):
        """Finds the most appropriate IP address within a range. If it can't
        find an IP it returns None. If it finds an IP it returns an IPv4Address
        object.

            :returns: ipaddr.IPv4Address
        """
        if self.network.ip_type != '4':
            return None
        elif self.ip_type != '4':
            return None

        ip = find_free_ip(self.start_lower, self.end_lower, ip_type='4')
        if ip:
            return ip
        else:
            return None

    def bind_render_record(self, **kwargs):
        if self.range_type == STATIC or self.ip_type == IP_TYPE_6:
            return ""

        DEFAULT_TTL = 3600
        if kwargs.pop('reverse', False):
            template = ("$GENERATE {3:>3}-{4:<3}  {1:44} {2}  IN  PTR     {0}")
        else:
            template = ("$GENERATE {3:>3}-{4:<3}  {0:44} {2}  IN  A       {1}")

        built = ""
        start = map(int, self.start_str.split("."))
        end = map(int, self.end_str.split("."))
        for a in range(start[0], end[0] + 1):
            b1 = start[1] if a == start[0] else 0
            b2 = end[1] if a == end[0] else 255
            for b in range(b1, b2 + 1):
                c1 = start[2] if (a, b) == tuple(start[:2]) else 0
                c2 = end[2] if (a, b) == tuple(end[:2]) else 255
                for c in range(c1, c2 + 1):
                    d1 = start[3] if (a, b, c) == tuple(start[:3]) else 0
                    d2 = end[3] if (a, b, c) == tuple(end[:3]) else 255
                    host = "{0}-{1}-{2}-$.{3}.".format(a, b, c, self.domain)
                    ip = "{0}.{1}.{2}.$".format(a, b, c)
                    rec = template.format(host, ip, DEFAULT_TTL, d1, d2)
                    built = "\n".join([built, rec]).strip()

        return built


def find_free_ip(start, end, ip_type='4'):
    """Given start and end numbers, find a free IP.
    :param start: The start number
    :type start: int
    :param end: The end number
    :type end: int
    :param ip_type: The type of IP you are looking for.
    :type ip_type: str either '4' or '6'
    """
    if ip_type == IP_TYPE_4:
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


class RangeAV(EAVBase):
    class Meta(EAVBase.Meta):
        app_label = 'cyder'
        db_table = 'range_av'

    entity = models.ForeignKey(Range)
    attribute = EAVAttributeField(Attribute)


class RangeOverflowError(ValidationError):
    pass
