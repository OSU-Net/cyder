from parsley import wrapGrammar
from ometa.grammar import OMeta
from ometa.runtime import OMetaBase
from constants import POOL, SUBNET, GROUP, HOST, GLOBAL
from dhcp_objects import (Host, Pool, Parameter, Option, Subnet, Group, Allow, Deny)
from utils import prepare_arguments, is_mac, is_ip
import sys
from bisect import insort_left, bisect_left


def strip_comments(content):
    return "".join(line[:line.find('#')] if '#' in line else line for line in content)


grammar = open('isc.parsley').read()

class DhcpConfigContext(
        OMeta.makeGrammar(grammar, name='DhcpConfigContext').createParserClass(OMetaBase, globals())):

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

    # I think that I will be doing something with classes in the future
    def add_class(self, dhcp_class):
        self.classes.add(dhcp_class)

    def __eq__(self, other):
        return self.hosts == other.hosts and \
               self.subnets == other.subnets and \
               self.groups  == other.groups and \
               self.classes == other.classes


iscgrammar = wrapGrammar(DhcpConfigContext)

if __name__ == '__main__':
    parse1 = iscgrammar(strip_comments(open(sys.argv[1]))).GlobalParse()
    parse2 = iscgrammar(strip_comments(open(sys.argv[2]))).GlobalParse()
    print parse1 == parse2
