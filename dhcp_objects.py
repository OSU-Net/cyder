from itertools import ifilter
from numbers import Number


def join_p(xs, d=1):
    if not xs:
        return ''
    lines = "".join(map(str, xs)).splitlines()
    prefix = '    ' * d if isinstance(d, Number) else d
    return "".join(prefix + line + '\n' for line in lines)


class DHCPMixin(object):
    side = ''

    def __ne__(self, other):
        return not self == other

    def join_side(self, x):
        return join_p(x, self.side)


class Option(DHCPMixin):
    def __init__(self, option, value):
        self.option = option
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, Option):
            return NotImplemented
        else:
            return ((self.side, self.option, self.value) ==
                    (other.side, other.option, other.value))

    def __hash__(self):
        return hash(self.option + self.value)

    def __str__(self):
        return self.join_side(
            'option {0} {1};\n'.format(self.option, self.value)
        )


class Statement(DHCPMixin):
    def __init__(self, statement):
        self.statement = statement

    def __eq__(self, other):
        if not isinstance(other, Statement):
            return NotImplemented
        else:
            return ((self.side, self.statement) ==
                    (other.side, other.statement))

    def __hash__(self):
        return hash(self.statement)

    def __str__(self):
        return self.join_side(self.statement + ';\n')


class RangeStmt(Statement):
    def __init__(self, start, end):
        self.statement = 'range {0} {1}'.format(start, end)
        self.start = start
        self.end = end


class Pool(DHCPMixin):
    def __init__(self, contents):
        self.contents = set()
        for item in contents:
            if isinstance(item, RangeStmt):
                self.start, self.end = item.start, item.end
            self.contents.update([item])

    def __eq__(self, other):
        if not isinstance(other, Pool):
            return NotImplemented
        else:
            return ((self.side, self.start, self.end) ==
                    (other.side, other.start, other.end))

    def __hash__(self):
        return hash(self.start + self.end)

    def __str__(self):
        return self.join_side(
            'pool {{\n'
            '{0}'
            '}}\n'
            .format(join_p(self.contents))
        )


class Subnet(DHCPMixin):
    def __init__(self, netaddr, netmask, contents):
        self.netaddr = netaddr
        self.netmask = netmask
        self.contents = set(contents or [])

    def __eq__(self, other):
        if not isinstance(other, Subnet):
            return NotImplemented
        else:
            return ((self.side, self.netaddr, self.netmask) ==
                    (other.side, other.netaddr, other.netmask))

    def __hash__(self):
        return hash(self.netaddr + self.netmask)

    def __str__(self):
        return self.join_side(
            'subnet {0} netmask {1} {{\n'
            '{2}'
            '}}\n'
            .format(self.netaddr, self.netmask, join_p(self.contents))
        )



class Subclass(DHCPMixin):
    def __init__(self, classname, match, contents):
        self.classname = classname
        self.match = match
        self.contents = set(contents or [])

    def __eq__(self, other):
        if not isinstance(other, Subclass):
            return NotImplemented
        else:
            return ((self.side, self.classname, self.match) ==
                    (other.side, other.classname, other.match))

    def __str__(self):
        if self.contents:
            end = (' {{\n'
                   '{0}'
                   '}}\n'
                   .format(join_p(self.contents)))
        else:
            end = ';\n'
        return self.join_side(
            'subclass "{0}" {1}{2}'
            .format(self.classname, self.match, end)
        )


class Class(DHCPMixin):
    def __init__(self, name, contents):
        self.name = name
        self.contents = set(contents or [])

    def __eq__(self, other):
        if not isinstance(other, Class):
            return NotImplemented
        else:
            return ((self.side, self.name) ==
                    (other.side, other.name))

    def __hash__(self):
        return hash(self.name)

    def add_subclass(self, match, contents):
        self.contents.update([Subclass(self.name, match, contents)])

    @property
    def subclasses(self):
        return set(ifilter(lambda x: isinstance(x, Subclass), self.contents))

    @property
    def truecontents(self):
        return set(ifilter(lambda x: not isinstance(x, Subclass),
                   self.contents))

    def __str__(self):
        return self.join_side(
            'class "{0}" {{\n'
            '{1}'
            '}}\n'
            '{2}'
            .format(self.name, join_p(self.truecontents),
                    join_p(self.subclasses, 0))
        )


class Group(DHCPMixin):
    def __init__(self, name, contents):
        self.name = name
        self.contents = set(contents or [])

    def __eq__(self, other):
        if not isinstance(other, Group):
            return NotImplemented
        else:
            return ((self.side, self.name) ==
                    (other.side, other.name))

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.join_side(
            'group {{ # {0}\n'
            '{1}'
            '}}\n'
            .format(self.name, join_p(self.contents))
        )


class Host(DHCPMixin):
    def __init__(self, name, contents):
        self.name = name
        self.contents = set(contents or [])

    def __eq__(self, other):
        if not isinstance(other, Host):
            return NotImplemented
        else:
            return ((self.side, self.name) ==
                    (other.side, other.name))

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.join_side(
            'host {0} {{\n'
            '{1}'
            '}}\n'
            .format(self.name, join_p(self.contents))
        )


class ConfigFile(DHCPMixin):
    def __init__(self):
        self.contents = set()

    def __eq__(self, other):
        return NotImplemented

    def __hash__(self):
        return NotImplemented

    def add(self, item):
        if item:
            self.contents.update([item])

    def get_class(self, name):
        classes = ifilter(lambda x: isinstance(x, Class) and x.name == name,
                          self.contents)
        return next(classes)

    def __str__(self):
        return join_p(self.contents, 0)
