from ipaddr import IPv4Address, IPv6Address, IPv4Network, IPv6Network
from itertools import chain
from operator import __eq__
from functools import total_ordering
from collections import MutableSequence
from bisect import insort_left, bisect_left

scope_weight = {'global': 0,
                'subnet': 1,
                'group': 2,
                'host': 3}



@total_ordering
class Attribute(object):
    def __init__(self, key, value, scope):
        self.key = key
        self.value = value
        self.scope = scope_weight[scope]

    def __eq__(self, other):
        return (self.key, self.value)  == (other.key, other.value)

    def __lt__(self, other):
        return (self.key, self.value) < (other.key, other.value)

    def overrides(self, other):
        return self.scope < other.scope


class Option(Attribute):

    def __str__(self):
        return "option {0} {1};".format(self.key, self.value)

    def __repr__(self):
        return "option {0} {1};".format(self.key, self.value)


class Parameter(Attribute):

    def __str__(self):
        return "{0} {1};".format(self.key, self.value)

    def __repr__(self):
        return "{0} {1};".format(self.key, self.value)


# We need to consider creating an allow and deny type but I think taht i will
# just use the Parameter class for the time being.

@total_ordering
class Host(object):
    def __init__(self, fqdn, ip=None, mac=None, options=None, parameters=NOne):
        self.fqdn = fqdn
        self.ip = IPv4Address(ip) if ip else None
        self.mac = mac
        self.options = options or []
        self.classes_contained_in = ['known-clients']
        self.parameters = parameters or []

    def __eq__(self, other):
        if not isinstance(self, type(other)):
            raise Exception("Can't compare objects of type "
                            "{0} and {1}".format(type(self, type(other)))
        return self.fqdn == other.fqdn and \
               self.ip == other.ip and \
               self.mac == other.mac and \
               sorted(self.options) == sorted(other.options)

    def __lt__(self, other):
        self.ip < other.ip

    def __str__(self):
        return "{0} {1} {2}".format(self.fqdn, self.mac, self.ip)

    def add_to_class(self, dhcp_class):
        self.classes_contained_in.append(dhcp_class)

    def add_options_or_parameters(self, new_attrs, force=False
        for new_attr in new_attrs:
            self.add_option_or_parameter(new_attr, force=force)

    def add_option_or_parameter(self, new_attr, force=False):
        if isinstance(new_attr, Option):
            attr_list = self.options
        else:
            attr_list = self.parameters
        for i, old_attr in enumerate(attr_list):
            if old_attr.key == new_attr.key:
                if new_attr.overrides(old_attr) or force:
                    attr_list[i] = new_attr
                    return True
                return False
        attr_list.append(new_attr)
        return True


class ScopeForHost(object):

    def update_host_attributes(self, force=False):
        for host in self.hosts:
            for attr in chain(self.options, self.parameters):
                host.add_option_or_parameter(attr, force=force)


@total_ordering
class Pool(ScopeForHost):

    def __init__(self, start, end, deny=None, allow=None, options=None,
                 parameters=None):
        self.start = IPv4Address(start)
        self.end = IPv4Address(end)
        self.deny = deny or []
        self.allow = allow or []
        self.options = options or []
        self.parameters = parameters or []

    def __eq__(self, other):
        if not isinstance(type(self), other):
            raise Exception("Can't compare objects of type "
                            "{0} and {1}".format(type(self), type(other)))
        return self.start == other.start and \
                self.end == other.end and \
                sorted(self.options) == sorted(other.options)

    def __lt__(self, other):
        return self.start < other.start


@total_ordering
class Subnet(ScopeForHost):
    def __init__(self, network_addr, netmask_addr, options=None, pools=None,
                 parameters=None):
        netmask = IPv4Address(netmask_addr)
        self.network = IPv4Network("{0}/{1}".format(
            network_addr, len(bin(netmask).translate(None, "b0"))))
        self.options = options or []
        self.pools = pools or []
        self.parameters = parameters or []

    def compare_options(self, other):
        return sorted(self.options) == sorted(other.options)

    def compare_pools(self, other):
        return sorted(self.pools) == sorted(other.pools)

    def compare_parameters(self, other):
        return sorted(self.parameters) == sorted(other.parameters)

    def __eq__(self, other):
        return self.network == other.network and \
               self.compare_options(other) and \
               self.compare_pools(other)

    def __lt__(self, other):
        if isinstance(other, Host):
            return self.network < other
        else:
            return self.network < other.network

    def is_host_in_subnet(self, host):
        return host.ip in self.network


class Group(ScopeForHost):

    def __init__(self, options=None, groups=None, hosts=None, parameters=None):
        self.options = options or []
        self.groups = groups or []
        self.hosts = hosts or []
        self.parameters = parameters or []
        self.update_host_attributes(force=True)
        for group in self.groups:
            group.update_host_attributes(force=True)


class ClientClass(object):
    def __init__(self, name, subclass = None):
        self.name = name
        self.subclass = subclass or []


class DhcpConfigContext(object):
    def __init__(self):
        self.hosts = []
        self.subnets = []
        self.groups = []
        self.classes = []

    @classmethod
    def apply_attrs(host, attrs):
        for attr in chain(contained_in.options, contained_in.parameters):
            host.add_option_or_parameter(attr)

    def add_subnet(self, subnet):
        insort_left(self.subnets, subnet)
        hosts_contained_in = filter(lambda x: x in subnet, self.hosts)

    def add_host(self, host):
        insort_left(self.hosts, host)
        contained_in = self.subnet_search(host)
        if contained_in:
            self.apply_attrs(
                host, chain(contained_in.options, contained_in.parameters))

    def add_group(self, host):parser.py

    def subnet_search(self, host):
        if self.subnets:
            hi = len(self.subnets)
            lo = 0
            while lo < hi:
                mid = (lo + hi) / 2
                if host.ip in self.subnets[mid].network:
                    return self.subnets[mid]
                # lol if the ip is less than the network's network address
                elif host.ip < self.subnets[mid].network.network:
                    hi = mid
                else:
                    lo = mid + 1
        return None
