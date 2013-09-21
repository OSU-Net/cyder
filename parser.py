import re
from copy import deepcopy
from itertools import ifilter
from parsley import makeGrammar
from sys import stdout

from dhcp_objects import (Statement, RangeStmt, Pool, Subnet, Class, Subclass,
                          Group, Host, ConfigFile)



def first(it):
    return next(it, None)

symbols = reduce(lambda x,y: x + y,
                 (chr(i) for i in xrange(0x21, 0x7E + 1)))

comment = re.compile(r'(?:"(?:[^"\\]|\\.)*"|[^"#])*(#|$)')


def parsefile(name):
    config = ConfigFile()

    bindings = {
        'symbols': symbols,
        'config': config,
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

    with open(name) as f:
        fStr = ''
        for line in f:
            if not line.startswith('group'):
                line = line[:comment.match(line).start(1)]
                if line[-1] != '\n':
                    line += '\n' # not strictly necessary
            fStr += line

    g = grammar(fStr)
    g.configFile()

    #import pdb; pdb.set_trace()

    return config


def find_in(obj, xs):
    return first(ifilter(lambda x: x == obj, xs))


def add_all(x, diff, side):
    #if isinstance(x, Host):
        #import pdb; pdb.set_trace()
    cx = deepcopy(x)
    cx.side = side
    diff.contents.update([cx]) # add immediately
    #if hasattr(x, 'contents'):
        #for n in x.contents:
            #add_all(n, cx, side)


def compare(left, right, diff):
    if hasattr(left, 'contents'):
        same = True

        # set intersection is broken, but there's no way to fix it
        for x in left.contents:
            if x in right.contents: # both left and right
                cx = deepcopy(x)
                cx.contents = set()
                cx.side = ' '
                y = find_in(x, right.contents)
                if not compare(x, y, cx): # if they're not the same
                    diff.contents.update([cx])
                    same = False
            else: # only left
                add_all(x, diff, '<')
                same = False

        for y in right.contents - left.contents: # only right
            add_all(y, diff, '>')
            same = False
    else:
        same = (left == right) # simple comparison

    stdout.write('================================\n')
    stdout.write(str(left))
    stdout.write('=========== l & r ==============\n')
    stdout.write(str(right))
    stdout.write('=========== diff ===============\n')
    stdout.write(str(diff))
    stdout.write('================================\n')

    return same


diffFile = None
def do_it():
    global diffFile
    one = parsefile('dhcpd1.conf')
    two = parsefile('dhcpd2.conf')
    diffFile = ConfigFile()

    compare(one, two, diffFile)

if __name__ == '__main__':
    do_it()
