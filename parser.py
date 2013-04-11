from parsley import wrapGrammar
from ometa.grammar import OMeta
from ometa.runtime import OMetaBase
from constants import scope_weight
from dhcp_objects import Host, Pool, Option, Subnet, Group, DhcpConfigContext
from utils import parse_to_dict, is_mac, is_ip
import sys


grammar = open('isc.parsley').read()

config = DhcpConfigContext()

B = OMeta.makeGrammar(grammar, name='isc').createParserClass(OMetaBase, globals())

class ISCDhcp(B):
    pass


if __name__ == '__main__':
    iscgrammar = wrapGrammar(ISCDhcp)
    print iscgrammar(sys.argv[1]).Subnet()
