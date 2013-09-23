from itertools import ifilter


def is_rangestmt(x):
    return isinstance(x, RangeStmt)


def join_p(xs, indent=1, prefix=''):
    if not xs:
        return ''
    lines = "".join(map(str, xs)).splitlines()
    prefix += '    ' * indent
    return "".join(prefix + line + '\n' for line in lines)


class DHCPMixin(object):
    side = ''

    def __ne__(self, other):
        return not self == other

    def format_struct(self, firstline, comment=''):
        s = ''
        if hasattr(self, 'contents') and self.contents:
            comment = (' # ' + comment) if comment else ''
            s += self.side + firstline + ' {' + comment + '\n'
            s += join_p(self.contents, prefix=self.side)
            s += self.side + '}\n'
        if hasattr(self, 'related') and self.related:
            s += join_p(self.related, indent=0) # they print their own side
        return s


class Statement(DHCPMixin):
    def __init__(self, statement):
        self.statement = statement

    def __eq__(self, other):
        if not isinstance(other, Statement):
            return NotImplemented
        else:
            return (self.statement == other.statement)

    def __hash__(self):
        return hash(self.statement)

    def __str__(self):
        return self.side + self.statement + ';\n'


class RangeStmt(Statement):
    def __init__(self, start, end):
        self.statement = 'range {0} {1}'.format(start, end)
        self.start = start
        self.end = end


class Pool(DHCPMixin):
    def __init__(self, contents=None):
        self.contents = set(contents)

        rs = next(ifilter(is_rangestmt, contents), None)
        self.start, self.end = rs.start, rs.end

    def __eq__(self, other):
        if not isinstance(other, Pool):
            return NotImplemented
        else:
            return (self.start == other.start and
                    self.end == other.end)

    def __hash__(self):
        return hash(self.start + self.end)

    def __str__(self):
        return self.format_struct('pool')


class Subnet(DHCPMixin):
    def __init__(self, netaddr, netmask, contents=None):
        self.netaddr = netaddr
        self.netmask = netmask
        self.contents = set(contents or [])

    def __eq__(self, other):
        if not isinstance(other, Subnet):
            return NotImplemented
        else:
            return (self.netaddr == other.netaddr and
                    self.netmask == other.netmask)

    def __hash__(self):
        return hash(self.netaddr + self.netmask)

    def __str__(self):
        return self.format_struct('subnet {0} netmask {1}'.format(self.netaddr,
                                                                self.netmask))



class Subclass(DHCPMixin):
    def __init__(self, classname, match, contents=None):
        self.classname = classname
        self.match = match
        self.contents = set(contents or [])

    def __eq__(self, other):
        if not isinstance(other, Subclass):
            return NotImplemented
        else:
            return (self.classname == other.classname and
                    self.match == other.match)

    def __hash__(self):
        return hash(self.classname + self.match)

    def __str__(self):
        firstline = 'subclass "{0}" {1}'.format(self.classname, self.match)

        if self.contents:
            return self.format_struct(firstline)
        else:
            return self.side + firstline + ';\n'


class Class(DHCPMixin):
    def __init__(self, name, contents=None, related=None):
        self.name = name
        self.contents = set(contents or [])
        self.related = set(related or [])

    def __eq__(self, other):
        if not isinstance(other, Class):
            return NotImplemented
        else:
            return (self.name == other.name)

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.format_struct('class "{0}"'.format(self.name))

    def add_subclass(self, match, contents):
        self.related.update([Subclass(self.name, match, contents)])


class Group(DHCPMixin):
    def __init__(self, name, contents=None):
        self.name = name
        self.contents = set(contents or [])

    def __eq__(self, other):
        if not isinstance(other, Group):
            return NotImplemented
        else:
            return (self.name == other.name)

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.format_struct('group', comment=self.name)


class Host(DHCPMixin):
    def __init__(self, name, contents=None):
        self.name = name
        self.contents = set(contents or [])

    def __eq__(self, other):
        if not isinstance(other, Host):
            return NotImplemented
        else:
            return (self.name == other.name)

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.format_struct('host ' + self.name)


class ConfigFile(object):
    def __init__(self, related=None):
        self.related = set(related or [])

    def __str__(self):
        return join_p(self.related, indent=0)

    def add(self, obj):
        if obj:
            self.related.update((obj,))

    def get_class(self, name):
        classes = ifilter(lambda x: isinstance(x, Class) and x.name == name,
                          self.related)
        return next(classes)
