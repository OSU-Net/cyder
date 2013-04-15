from parsley import wrapGrammar
from ometa.grammar import OMeta
from ometa.runtime import OMetaBase
from constants import POOL, SUBNET, GROUP, HOST
from dhcp_objects import (Host, Pool, Parameter, Option, Subnet, Group,
                          DhcpConfigContext, Allow, Deny)
from utils import prepare_arguments, is_mac, is_ip
import sys


grammar = open('isc.parsley').read()

config = DhcpConfigContext()

B = OMeta.makeGrammar(grammar, name='i').createParserClass(OMetaBase, globals())

class ISCDhcp(B):
    pass

iscgrammar = wrapGrammar(ISCDhcp)

if __name__ == '__main__':
    print iscgrammar(sys.argv[1]).Subnet()
