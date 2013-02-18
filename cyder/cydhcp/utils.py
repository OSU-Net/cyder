import ipaddr
from django.core.exceptions import ValidationError
from django.db.models import Q


class IPFilterSet(object):
    """
    The IPFilterSet expects that all IPFilters added to it are of the same
    type. This might be useful later.
    """

    def __init__(self):
        self.ipfs = []

    def add(self, ipf):
        self.ipfs.append(ipf)

    def pprint(self):
        for ipf in self.ipfs:
            print ipf

    def pprint_intersect(self):
        for intersect in self.calc_intersect():
            print intersect

    def calc_intersect(self):
        """
        This is where the magic comes from. Given a list of IPFilter objects,
        figure the ranges that are common to all the IPFilters, and create a
        new list of IPFilter objects that represent this range.
        """

    def trim(self, r, rs, ip_type):
        if not (rs and r):
            return r
        r1 = rs[0]
        rx = self.intersect(r, r1, ip_type)
        return self.trim(rx, rs[1:], ip_type)

    def intersect(self, r1, r2, ip_type):
        """Cases:
            * Subset or equal
            * Left intersect
            * Right intersect
            * No intersect
        """
        if r1.start > r2.end:
            return None
        # We have intersection somewhere.
        if r1.end == r2.end and r1.start == r1.end:
            # r1 is subset of r2
            # Low                   High
            # r1    |---------|
            # r2    |---------|
            # rx    |---------|
            return r1
        if r1.start > r2.start and r1.end < r2.end:
            # r1 is subset of r2
            # Low                   High
            # r1     |-------|
            # r2    |---------|
            # rx    |---------|
            return r1
        if r1.start > r2.start and r1.end > r2.start:
            # Low                   High
            # r1    |---------|
            # r2 |---------|
            # rx    |------|
            return IPFilter(None, ip_type, r1.start_upper, r1.start_lower,
                            r2.end_upper, r2.end_lower)
        if r1.start < r2.start and r1.end < r2.end:
            # Low                   High
            # r1 |---------|
            # r2    |---------|
            # rx    |------|
            return IPFilter(None, ip_type, r2.start_upper, r2.start_lower,
                            r1.end_upper, r1.end_lower)


class IPFilter(object):

    def __init__(self, start, end, ip_type, object_=None):
        self.object_ = object_  # The composite object (it can be None)
        self.ip_type = ip_type
        self.start, self.end, self.Q = start_end_filter(start, end, ip_type)

    def __str__(self):
        return "{0} -- {1}".format(self.start, self.end)


def start_end_filter(start, end, ip_type):
    if ip_type == '6':
        IPKlass = ipaddr.IPv6Address
    elif ip_type == '4':
        IPKlass = ipaddr.IPv4Address

    istart = IPKlass(start)
    iend = IPKlass(end)

    if int(istart) == int(iend):
        raise ValidationError("start and end cannot be equal")
    elif int(istart) > int(iend):
        raise ValidationError("start cannot be greater than end")

    start_upper, start_lower = one_to_two(int(istart))
    end_upper, end_lower = one_to_two(int(iend))

    # Equal uppers. Lower must be within.
    if start_upper == end_upper:
        q = Q(ip_upper=start_upper,
              ip_lower__gte=start_lower,
              ip_lower__lte=end_lower,
              ip_type=ip_type)
    else:
        q = Q(ip_upper__gt=start_upper, ip_upper__lt=end_upper,
              ip_type=ip_type)

    return istart, iend, q


def networks_to_Q(networks):
    """
    Take a list of network objects and compile a Q that matches any object
    that exists in one of those networks.

    """
    q = Q()
    for network in networks:
        network.update_ipf()
        q = q | network.ipf.Q
    return q


def two_to_four(start, end):
    start_upper = start >> 64
    start_lower = start & (1 << 64) - 1
    end_upper = end >> 64
    end_lower = end & (1 << 64) - 1
    return start_upper, start_lower, end_upper, end_lower


def one_to_two(ip):
    return (ip >> 64, ip & (1 << 64) - 1)


def two_to_one(upper, lower):
    return long(upper << 64) + long(lower)


def four_to_two(start_upper, start_lower, end_upper, end_lower):
    return (two_to_one(start_upper, start_lower),
            two_to_one(end_upper, end_lower))


def int_to_ip(ip, ip_type):
    """
    A wrapper that converts a 32 or 128 bit integer into human readable IP
    format.

    """
    if ip_type == '6':
        IPKlass = ipaddr.IPv6Address
    elif ip_type == '4':
        IPKlass = ipaddr.IPv4Address
    return str(IPKlass(ip))


def find_network_for_range(start, end,):
    from cyder.cydhcp.network.models import Network
    for network in Network.objects.all():
        network.update_network()
        if int(network.network.network) < start < end < \
                int(network.network.broadcast):
            return network
    return None
