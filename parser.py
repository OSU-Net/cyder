from parsley import wrapGrammar
from ometa.grammar import OMeta
from ometa.runtime import OMetaBase
from string import letters, hexdigits
from itertools import chain
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
