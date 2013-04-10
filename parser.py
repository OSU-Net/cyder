from parsley import wrapGrammar
from ometa.grammar import OMeta
from ometa.runtime import OMetaBase
from string import letters, hexdigits
from itertools import chain
from ipaddr import IPv4Address, IPv6Address, IPv4Network, IPv6Network
from collections import defaultdict
import re
import sys

class Host(object):
    def __init__(self, fqdn, ip=None, mac=None):
        self.fqdn = fqdn
        self.ip = ip
        self.mac = mac

    def value(self):
        return set([self.fqdn, self.mac, self.ip])

    def __eq__(self, other):
        if not isinstance(type(self), other):
            raise Exception("Can't compare objects of type "
                            "{0} and {1}".format(type(self), type(other)))
        return self.value() == other.value()

    def __str__(self):
        return "{0} {1} {2}".format(self.fqdn, self.mac, self.ip)


class Option(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __eq__(self, other):
        return self.key == other.key and self.value == other.value


class Pool(object):
    def __init__(self, start, end, deny=None, allow=None, failover=None,
                 options=None):
        self.start = IPv4Address(start)
        self.end = IPv4Address(end)
        self.deny = deny or []
        self.allow = allow or []
        self.failover = failover or []


def parse_to_pool(parse):
    kwargs = {}
    for key, value in chain(*(elem.items() for elem in parse)):
        if key in kwargs:
            kwargs[key].append(value)
        else:
            kwargs[key] = [value] if key not in ['start', 'end'] else value
    return Pool(**kwargs)


class Subnet(object):
    def __init__(self, network_addr, netmask_addr, options=None,
            statements=None, pools=None):
        self.network_addr = IPv4Address(network_addr)
        self.netmask_addr = IPv4Address(netmask_addr)
        self.options = options or []
        self.statements = statements or []
        self.pools = pools or []

mac_match = "(([0-9a-f]){2}:){5}([0-9a-f]){2}$"
is_mac = re.compile(mac_match)
is_ip = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

grammar = open('isc.parsley').read()
B = OMeta.makeGrammar(grammar, name='isc').createParserClass(OMetaBase, globals())


class ISCDhcp(B):
    pass


if __name__ == '__main__':
    iscgrammar = wrapGrammar(ISCDhcp)
    print iscgrammar(sys.argv[1]).Subnet()
