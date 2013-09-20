import re
from parsley import makeGrammar


from dhcp_objects import (Option, Statement, RangeStmt, Pool, Subnet, Class,
                          Subclass, Group, Host, ConfigFile)

symbols = reduce(lambda x,y: x + y,
                 (chr(i) for i in xrange(0x21, 0x7E + 1)))


config = ConfigFile()


bindings = {
    'symbols': symbols,
    'config': config,
    'Option': Option,
    'Statement': Statement,
    'RangeStmt': RangeStmt,
    'Pool': Pool,
    'Subnet': Subnet,
    'Class': Class,
    'Subclass': Subclass,
    'Group': Group,
    'Host': Host,
}

with open('dhcp.parsley') as f:
    grammar = makeGrammar(f.read(), bindings)

comment = re.compile(r'(?:"(?:[^"\\]|\\.)*"|[^"#])*(#|$)')

with open('dhcpd.conf') as f:
    fStr = ''
    for line in f:
        if not line.startswith('group'):
            line = line[:comment.match(line).start(1)]
            if line[-1] != '\n':
                line += '\n' # not strictly necessary
        fStr += line

    x = grammar(fStr)

x.configFile()
