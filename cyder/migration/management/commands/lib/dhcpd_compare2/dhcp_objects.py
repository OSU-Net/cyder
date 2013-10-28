from functools import total_ordering
from ipaddr import IPAddress
from itertools import ifilter


def is_rangestmt(x):
    return isinstance(x, RangeStmt)


def join_p(xs, indent=1, prefix=''):
    if not xs:
        return ''
    lines = "".join(map(str, xs)).splitlines()
    prefix += '    ' * indent
    return "".join(prefix + line + '\n' for line in lines)


@total_ordering
class DHCPMixin(object):
    side = ''

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return self.TYPE < other.TYPE or (self.TYPE == other.TYPE and
                                          self._sort_key < other._sort_key)

    def __str__(self):
        s = ''
        if hasattr(self, 'contents') and self.contents:
            map(lambda x: x.set_sort_key(), self.contents)
            if hasattr(self, 'comment') and self.comment:
                comment = ' # ' + self.comment
            else:
                comment = ''
            s += self.side + self.firstline + ' {' + comment + '\n'
            s += join_p(sorted(self.contents), prefix=self.side)
            s += self.side + '}\n'
        if hasattr(self, 'related') and self.related:
            map(lambda x: x.set_sort_key(), self.related)
            s += join_p(sorted(self.related), indent=0)
            # they print their own side
        return s


class Statement(DHCPMixin):
    TYPE = 1

    def __init__(self, statement):
        self.statement = statement

    def set_sort_key(self):
        self._sort_key = self.statement

    def __eq__(self, other):
        return (isinstance(other, Statement)
                and self.statement == other.statement)

    def __hash__(self):
        return hash(self.statement)

    def __str__(self):
        return self.side + self.statement + ';\n'


class RangeStmt(Statement):
    TYPE = 0

    def __init__(self, start, end):
        self.statement = 'range {0} {1}'.format(start, end)
        self.start = start
        self.end = end

    def set_sort_key(self):
        self._sort_key = (int(IPAddress(self.start)),
                          int(IPAddress(self.end)))

    def __eq__(self, other):
        return (isinstance(other, RangeStmt) and self.start == other.start
                and self.end == other.end)


class Pool(DHCPMixin):
    TYPE = 2

    def __init__(self, contents=None):
        self.contents = set(contents or [])
        self.firstline = 'pool'

        rs = next(ifilter(is_rangestmt, contents))
        self.start, self.end = rs.start, rs.end

    def set_sort_key(self):
        self._sort_key = (int(IPAddress(self.start)),
                          int(IPAddress(self.end)))

    def __eq__(self, other):
        return (isinstance(other, Pool) and self.start == other.start
                and self.end == other.end)

    def __hash__(self):
        return hash(self.start + self.end)


class Subnet(DHCPMixin):
    TYPE = 3

    def __init__(self, netaddr, netmask, contents=None):
        self.netaddr = netaddr
        self.netmask = netmask
        self.contents = set(contents or [])
        self.firstline = 'subnet {0} netmask {1}'.format(self.netaddr,
                                                         self.netmask)

    def set_sort_key(self):
        self._sort_key = (int(IPAddress(self.netaddr)),
                          int(IPAddress(self.netmask)))

    def __eq__(self, other):
        return (isinstance(other, Subnet) and self.netaddr == other.netaddr
                and self.netmask == other.netmask)

    def __hash__(self):
        return hash(self.netaddr + self.netmask)


class Subclass(DHCPMixin):
    TYPE = 4

    def __init__(self, classname, match, contents=None):
        self.classname = classname
        self.match = match
        self.contents = set(contents or [])
        self.firstline = 'subclass "{0}" {1}'.format(self.classname,
                                                     self.match)

    def set_sort_key(self):
        self._sort_key = self.classname + self.match

    def __eq__(self, other):
        return (isinstance(other, Subclass)
                and self.classname == other.classname
                and self.match == other.match)

    def __hash__(self):
        return hash(self.classname + self.match)

    def __str__(self):
        if self.contents:
            return super(Subclass, self).__str__()
        else:
            return self.side + self.firstline + ';\n'


class Class(DHCPMixin):
    TYPE = 5

    def __init__(self, name, contents=None, related=None):
        self.name = name
        self.contents = set(contents or [])
        self.related = set(related or [])
        self.firstline = 'class "{0}"'.format(self.name)

    def set_sort_key(self):
        self._sort_key = self.name

    def __eq__(self, other):
        return isinstance(other, Class) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def add_subclass(self, match, contents):
        self.related.add(Subclass(self.name, match, contents))


class Group(DHCPMixin):
    TYPE = 6

    def __init__(self, name, contents=None):
        self.name = name
        self.contents = set(contents or [])
        self.firstline = 'group'
        self.comment = self.name

    def set_sort_key(self):
        self._sort_key = self.name

    def __eq__(self, other):
        return isinstance(other, Group) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


class Host(DHCPMixin):
    TYPE = 7

    def __init__(self, name, contents=None):
        self.name = name
        self.contents = set(contents or [])
        self.firstline = 'host ' + self.name

    def set_sort_key(self):
        self._sort_key = self.name

    def __eq__(self, other):
        return isinstance(other, Host) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


class ConfigFile(DHCPMixin):
    def __init__(self, related=None):
        self.related = set(related or [])

    def add(self, obj):
        if obj:
            self.related.add(obj)

    def get_class(self, name):
        classes = ifilter(lambda x: isinstance(x, Class) and x.name == name,
                          self.related)
        return next(classes)
