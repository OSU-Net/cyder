import re
from copy import deepcopy
from itertools import ifilter
from parsley import makeGrammar
from sys import argv, stderr, stdout

from dhcp_objects import (Statement, RangeStmt, Pool, Subnet, Class, Subclass,
                          Group, Host, ConfigFile)



def first(it):
    return next(it, None)

symbols = reduce(lambda x,y: x + y,
                 (chr(i) for i in xrange(0x21, 0x7E + 1)))

comment = re.compile(r'(?:"(?:[^"\\]|\\.)*"|[^"#])*(#|$)')


def parsefile(name):
    bindings = {
        'symbols': symbols,
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

    with open('dhcp.parsley') as f:
        grammar = makeGrammar(f.read(), bindings)

    with open(name) as f:
        fStr = ''
        for line in f:
            if not line.startswith('group'):
                line = line[:comment.match(line).start(1)]
                if not line or line[-1] != '\n':
                    line += '\n' # not strictly necessary
            fStr += line

    g = grammar(fStr)
    return g.configFile()


def find_in(obj, xs):
    return first(ifilter(lambda x: x == obj, xs))


def add_all(x, diff, side):
    cx = deepcopy(x)
    cx.side = side
    diff.contents.update([cx]) # add immediately


def compare(left, right, diff):
    same = True

    # set intersection is broken, but there's no way to fix it
    for x in left.contents:
        if x in right.contents: # both left and right
            y = find_in(x, right.contents)
            if not hasattr(x, 'contents') or not (x.contents or y.contents):
                if not x == y:
                    diff.contents.update([deepcopy(x), deepcopy(y)])
                    same = False
                continue
            cx = deepcopy(x)
            cx.contents = set()
            cx.side = ' '
            if not compare(x, y, cx): # if they're not the same
                diff.contents.update([cx])
                same = False
        else: # only left
            add_all(x, diff, '<')
            same = False

    for y in right.contents - left.contents: # only right
        add_all(y, diff, '>')
        same = False

    #stdout.write('================================\n')
    #stdout.write(str(left))
    #stdout.write('=========== l & r ==============\n')
    #stdout.write(str(right))
    #stdout.write('=========== diff ===============\n')
    #stdout.write(str(diff))
    #stdout.write('================================\n')

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
    compare(one, two, diffFile)
    return str(diffFile)

if __name__ == '__main__':
    stdout.write(compare_files(argv[1], argv[2], verbose=True))
