import re
from copy import deepcopy
from itertools import ifilter
from parsley import makeGrammar
from sys import argv, stderr, stdout

from dhcp_objects import (Statement, RangeStmt, Pool, Subnet, Class, Subclass,
                          Group, Host, ConfigFile)



def first(it):
    return next(it, None)

symbols = ''.join(chr(i) for i in xrange(0x21, 0x7E + 1))

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
        'ConfigFile': ConfigFile,
    }

    with open('dhcp.parsley') as g:
        grammar = makeGrammar(g.read(), bindings)

    with open(name) as f:
        fStr = ''
        for line in f:
            if not line.startswith('group'):
                line = line[:comment.match(line).start(1)]
                if not line or line[-1] != '\n':
                    line += '\n'
            fStr += line

    g = grammar(fStr)
    g.configFile()

    return config


def find_in(obj, xs):
    return first(ifilter(lambda x: x == obj, xs))


def has_contents(x):
    return hasattr(x, 'contents') and x.contents


def has_related(x):
    return hasattr(x, 'related') and x.related


def has_children(x):
    return has_contents(x) or has_related(x)


def add_all(x, zs, side):
    z = deepcopy(x)
    z.side = side
    if hasattr(z, 'related') and z.related:
        for a in z.related:
            a.side = side
    zs.update([z])


def deep_compare(x, y, zs):
    same = True

    z = deepcopy(x)
    z.side = ' '
    if hasattr(z, 'contents'):
        z.contents = set()
    if hasattr(z, 'related'):
        z.related = set()

    if has_contents(x) or has_contents(y):
        if not compare(x, y, z, 'contents'):
            same = False

    if has_related(x) or has_related(y):
        if not compare(x, y, z, 'related'):
            same = False

    if not same:
        zs.add(z)

    return same


def shallow_compare(x, y, zs):
    if not x == y:
        zs.update((deepcopy(x), deepcopy(y)))
        return False
    else:
        return True


def compare(left, right, diff, childtype):
    same = True

    xs = getattr(left, childtype)
    ys = getattr(right, childtype)
    zs = getattr(diff, childtype)

    # WARNING: Because of the way the DHCP object `==` operator was designed,
    # two objects x and y where `x == y` may contain unequal attributes. This
    # is intentional. In this function, x and y come from different sets; if
    # we found the intersection of xs and ys by doing `xs & ys`, we would not
    # know whether each item in the intersection was from xs or ys, requiring
    # an extra find_in call (which is slightly expensive). We work around this
    # limitation by finding the set intersection manually. This is slightly
    # slower than doing `xs & ys` but enables us to guarantee that every
    # object in the intersection came from xs, saving us an extra find_in call
    # and resulting in better speed overall.
    for x in xs:
        if x in ys: # both
            y = find_in(x, ys)
            if has_children(x) or has_children(y): # non-terminal
                same = deep_compare(x, y, zs)
            else: # terminal
                same = shallow_compare(x, y, zs)
        else: # left
            add_all(x, zs, '<')
            same = False

    for y in ys - xs: # right
        add_all(y, zs, '>')
        same = False

    #stderr.write('================================\n')
    #stderr.write(str(left))
    #stderr.write('--------------------------------\n')
    #stderr.write(str(right))
    #stderr.write('------------- diff -------------\n')
    #stderr.write(str(diff))
    #stderr.write('================================\n')

    return same


def compare_files(filename1, filename2, verbose=False):
    if verbose:
        stderr.write('## Parsing {0}...\n'.format(filename1))
    one = parsefile(filename1)

    if verbose:
        stderr.write('## Parsing {0}...\n'.format(filename2))
    two = parsefile(filename2)

    diffFile = ConfigFile()
    if verbose:
        stderr.write('## Comparing...\n')
    compare(one, two, diffFile, 'related')
    return str(diffFile)

if __name__ == '__main__':
    stdout.write(compare_files(argv[1], argv[2], verbose=True))
