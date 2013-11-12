from ipaddr import IPv4Address, IPv6Address, IPv4Network, IPv6Network
from itertools import chain
from functools import total_ordering
from bisect import insort_left, bisect_left

def join_p(xs, d=1):
    if not xs:
        return ''
    lines = "".join(map(str, xs)).splitlines()
    return "".join('\t' * d + line + '\n' for line in lines)

@total_ordering
class Attribute(object):

    def __init__(self, key, value, scope):
        self.key = key
        self.value = value
        self.scope = scope

    def __eq__(self, other):
        return (self.key, self.value)  == (other.key, other.value)

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return (self.key, self.value) < (other.key, other.value)

    def __hash__(self):
        return hash(self.__str__())

    def __repr__(self):
        return self.__str__()

    def overrides(self, other):
        return self.scope < other.scope


class Option(Attribute):

    def __str__(self):
        return "option {0} {1};\n".format(self.key, self.value)


class Parameter(Attribute):

    def __str__(self):
        return "{0} {1};\n".format(self.key, self.value)


@total_ordering
class Accessable(object):

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return self.value < other.value

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__repr__())


class Allow(Accessable):

    def __str__(self):
        return "allow {0};\n".format(self.value)

    def is_allowed(self, host):
        # implement later
        return True


class Deny(Accessable):

    def __str__(self):
        return "deny {0};\n".format(self.value)

    def is_allowed(self, host):
        # implement later
        return True


@total_ordering
class Host(object):

    def __init__(self, fqdn, ip=None, mac=None, options=None, parameters=None):
        self.fqdn = fqdn
        self.ip = IPv4Address(ip) if ip else None
        self.mac = mac
        self.options = set(options or [])
        self.classes_contained_in = ['known-clients']
        self.parameters = set(parameters or [])

    def __eq__(self, other):
        return self.fqdn == other.fqdn and \
               self.ip == other.ip and \
               self.mac == other.mac and \
               self.options == other.options and \
               self.parameters == other.parameters

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return int(self.ip or 0) < int(other.ip or 0)

    def __hash__(self):
        return hash(self.__str__())

    def __str__(self):
        ip_line = "\tfixed-address {0};\n".format(self.ip) if self.ip else ""
        return ("host {0} {{\n"
                "\thardware ethernet {1};\n"
                "{2}{3}{4}"
                "}}\n".format(
                    self.fqdn,
                    self.mac,
                    ip_line,
                    join_p(sorted(self.options)),
                    join_p(sorted(self.parameters))))

    def add_to_class(self, dhcp_class):
        self.classes_contained_in.append(dhcp_class)

    def add_options_or_parameters(self, new_attrs, force=False):
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

    def compare_options(self, other):
        return sorted(self.options) == sorted(other.options)

    def compare_parameters(self, other):
        return sorted(self.parameters) == sorted(other.parameters)

    def __repr__(self):
        return self.__str__()


@total_ordering
class Pool(ScopeForHost):

    def __init__(self, start, end, deny=None, allow=None, options=None,
                 parameters=None):
        self.start = IPv4Address(start)
        self.end = IPv4Address(end)
        self.deny = set(deny or [])
        self.allow = set(allow or [])
        self.options = set(options or [])
        self.parameters = set(parameters or [])

    def __eq__(self, other):
        return  self.compare_options(other) and \
                self.compare_parameters(other) and \
                self.start == other.start and \
                self.end == other.end and \
                self.allow == other.allow and \
                self.deny == other.deny

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return self.start < other.start

    def __str__(self):
        return ("pool {{\n"
                "{0}{1}{2}{3}"
                "\trange {4} {5};\n"
                "}}\n".format(
                    join_p(sorted(self.options)),
                    join_p(sorted(self.parameters)),
                    join_p(sorted(self.allow)),
                    join_p(sorted(self.deny)),
                    self.start, self.end))

    def __hash__(self):
        return hash(self.__str__())


@total_ordering
class Subnet(ScopeForHost):

    def __init__(self, network_addr, netmask_addr, options=None, pools=None,
                 parameters=None):
        netmask = IPv4Address(netmask_addr)
        self.network = IPv4Network("{0}/{1}".format(
            network_addr, len(bin(netmask).translate(None, "b0"))))
        self.options = set(options or [])
        self.pools = set(pools or [])
        self.parameters = set(parameters or [])

    def compare_pools(self, other):
        return sorted(self.pools) == sorted(other.pools)

    def __str__(self):
        return ("subnet {0} netmask {1} {{\n"
                "{2}{3}{4}"
                "}}\n".format(
                   self.network.network,
                   self.network.netmask,
                   join_p(sorted(self.options)),
                   join_p(sorted(self.parameters)),
                   join_p(sorted(self.pools))))

    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, other):
        return self.options == other.options and \
               self.parameters == other.parameters and \
               self.pools == other.pools and \
               self.network == other.network

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        if isinstance(other, Host):
            return self.network < other.ip
        else:
            return self.network < other.network

    def is_host_in_subnet(self, host):
        return host.ip in self.network


@total_ordering
class Group(ScopeForHost):

    def __init__(self, options=None, groups=None, hosts=None, parameters=None):
        self.options = set(options or [])
        self.groups = set(groups or [])
        self.hosts = set(hosts or [])
        self.parameters = set(parameters or [])

    def group_update(self):
        self.update_host_attributes(force=True)
        for group in self.groups:
            group.group_update()

    def __eq__(self, other):
        return self.compare_options(other) and \
               self.compare_parameters(other) and \
               self.hosts == other.hosts and \
               self.groups == other.groups

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        # lol wut
        return len(self.groups) < len(other.groups)

    def __str__(self):
        return ("group {{\n"
                "{0}{1}{2}{3}"
                "}}\n".format(
                    join_p(sorted(self.options)),
                    join_p(sorted(self.parameters)),
                    join_p(sorted(self.groups)),
                    join_p(sorted(self.hosts, key=lambda x: x.fqdn))))

    def __hash__(self):
        return hash(self.__str__())

@total_ordering
class ClientClass(object):

    def __init__(self, name=None, options=None,
                 parameters=None, match=None):
        self.name = name
        self.options = set(options or [])
        self.parameters = set(parameters or [])
        self.match = match
        self.subclass = set()

    def __str__(self):
        return ('class "{0}" {{\n'
                '{1}{2}'
                '\tmatch {3};\n'
                '}}\n'.format(
                    self.name,
                    join_p(sorted(self.options)),
                    join_p(sorted(self.parameters)),
                    self.match) +
                ''.join(['subclass "{0}" 1:{1};\n'
                         .format(self.name, mac)
                         for mac in sorted(self.subclass)]))

    def __hash__(self):
        return hash(self.__str__())

    def add_subclass(self, mac):
        self.subclass.update([mac])

    def __eq__(self, other):
        return self.name == other.name and \
               self.subclass == other.subclass

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return self.start < other.start
