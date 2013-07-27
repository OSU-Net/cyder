from parsley import wrapGrammar
from ometa.grammar import OMeta
from ometa.runtime import OMetaBase
from constants import *
from dhcp_objects import (Host, Pool, Parameter, Option, Subnet, Group, Allow,
                          Deny, ClientClass)
from utils import prepare_arguments, is_mac, is_ip
import sys
from bisect import insort_left, bisect_left
from ipaddr import IPv4Address, IPv6Address


def strip_comments(content):
    return "".join(line[:line.find('#')] if '#' in line else line for line in content)


grammar = open('cyder/migration/management/commands/lib/dhcpd_compare/'
               'isc.parsley').read()

class DhcpConfigContext(
        OMeta.makeGrammar(
            grammar,
            name='DhcpConfigContext').createParserClass(OMetaBase, globals())):

    def __init__(self, *args, **kwargs):
        self.hosts = set()
        self.subnets = set()
        self.groups = set()
        self.classes = set()
        self.options = set()
        self.parameters = set()
        super(DhcpConfigContext, self).__init__(*args, **kwargs)

    def apply_attrs(self, host, attrs):
        for attr in attrs:
            host.add_option_or_parameter(attr)

    def add_subnet(self, subnet):
        self.subnets.add(subnet)

    def add_host(self, host):
        self.hosts.add(host)

    def add_group(self, group):
        self.groups.add(group)

    def add_option(self, option):
        self.options.add(option)

    def add_parameter(self, parameter):
        self.parameters.add(parameter)

    def add_class(self, dhcp_class):
        self.classes.add(dhcp_class)

    def add_subclass(self, start, end, mac):
        start = IPv4Address(start)
        for _class in self.classes:
            if _class.start == start:
                _class.add_subclass(mac)
                return True
        return False

    def __eq__(self, other):
        return self.hosts == other.hosts and \
               self.subnets == other.subnets and \
               self.groups  == other.groups and \
               self.classes == other.classes

    def diff(self, other):
        if not (self == other):
            first_subnets = self.subnets - other.subnets
            second_subnets = other.subnets - self.subnets
            first_hosts = self.hosts - other.hosts
            second_hosts = other.hosts - self.hosts
            first_groups = self.groups - other.groups
            second_groups = other.groups - self.groups
            if first_subnets:
                print "Subnets found in the first config and not in the second"
                for subnet in first_subnets:
                    print subnet
            if second_subnets:
                print "Subnets found in the second config and not in the first"
                for subnet in second_subnets:
                    print subnet
            if first_hosts:
                print "Hosts found in the first config and not in the second"
                for host in first_hosts:
                    print host
            if second_hosts:
                print "Hosts found in the second config and not in the first"
                for host in second_hosts:
                    print host
            if first_groups:
                print "Groups found in the first config and not in the second"
                for groups in first_groups:
                    print groups
            if second_groups:
                print "Groups found in the second config and not in the first"
                for groups in second_groups:
                    print groups





iscgrammar = wrapGrammar(DhcpConfigContext)

def compare(file1, file2):
    parse1 = iscgrammar(strip_comments(open(file1))).GlobalParse()
    parse2 = iscgrammar(strip_comments(open(file2))).GlobalParse()
    parse1.diff(parse2)
