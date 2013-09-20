from itertools import ifilter


def join_p(xs, d=1):
    if not xs:
        return ''
    lines = "".join(map(str, xs)).splitlines()
    return "".join('\t' * d + line + '\n' for line in lines)


class EqualityMixin(object):
    def __ne__(self, other):
        return not self == other


class Option(EqualityMixin):
    friendly_name = 'option'

    def __init__(self, option, value):
        self.option = option
        self.value = value

    def __eq__(self, other):
        return self.option == other.option and self.value == other.value

    def __hash__(self):
        return hash(self.option + self.value)

    def __str__(self):
        return 'option {0} {1};\n'.format(self.option, self.value)


class Statement(EqualityMixin):
    friendly_name = 'statement'

    def __init__(self, statement):
        self.statement = statement

    def __eq__(self, other):
        return self.statement == other.statement

    def __hash__(self):
        return hash(self.statement)

    def __str__(self):
        return self.statement + ';\n'


class RangeStmt(Statement):
    def __init__(self, start, end):
        self.statement = 'range {0} {1}'.format(start, end)
        self.start = start
        self.end = end


class Pool(EqualityMixin):
    friendly_name = 'pool'

    def __init__(self, contents):
        contents = set()
        for item in contents:
            if isinstance(item, RangeStmt):
                self.start, self.end = item.start, item.end
            self.contents.update([item])

    def __eq__(self, other):
        return (self.start, self.end) == (other.start, other.end)

    def __hash__(self):
        return hash(self.contents)

    def __str__(self):
        return ('pool {{\n'
                '{0}'
                '}}\n'
                .format(join_p(self.contents)))


class Subnet(EqualityMixin):
    friendly_name = 'subnet'

    def __init__(self, netaddr, netmask, contents):
        self.netaddr = netaddr
        self.netmask = netmask
        self.contents = set(contents or [])

    def __eq__(self, other):
        return (self.netaddr, self.netmask) == (other.netaddr, other.netmask)

    def __hash__(self):
        return hash(self.netaddr + self.netmask)

    def __str__(self):
        return ('subnet {0} netmask {1} {{\n'
                '{2}'
                '}}\n'
                .format(self.netaddr, self.netmask, join_p(self.contents)))

class Class(EqualityMixin):
    friendly_name = 'class'

    subclasses = set()

    def __init__(self, name, contents):
        self.name = name
        self.contents = set(contents or [])

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def add_subclass(self, match, contents):
        self.subclasses.update([Subclass(self.name, match, contents)])

    def __str__(self):
        return ('class "{0}" {{\n'
                '{1}'
                '}}\n'
                '{2}'
                .format(self.name, join_p(self.contents),
                        join_p(self.subclasses, 0)))


class Subclass(EqualityMixin):
    friendly_name = 'subclass'

    def __init__(self, classname, match, contents):
        self.classname = classname
        self.match = match
        self.contents = set(contents or [])

    def __str__(self):
        if self.contents:
            end = (' {{\n'
                   '{0}'
                   '}}\n'
                   .format(join_p(self.contents)))
        else:
            end = ';\n'
        return ('subclass "{0}" {1}{2}'
                .format(self.classname, self.match, end))


class Group(EqualityMixin):
    friendly_name = 'group'

    def __init__(self, name, contents):
        self.name = name
        self.contents = set(contents or [])

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return ('group {{ # {0}\n'
                '{1}'
                '}}\n'
                .format(self.name, join_p(self.contents)))


class Host(EqualityMixin):
    friendly_name = 'host'

    def __init__(self, name, contents):
        self.name = name
        self.contents = contents

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return ('host {0} {{\n'
                '{1}'
                '}}\n'
                .format(self.name, join_p(self.contents)))


class ConfigFile(EqualityMixin):
    friendly_name = 'config file'

    contents = set()

    def add(self, item):
        if item:
            self.contents.update([item])

    def get_class(self, name):
        classes = ifilter(lambda x: isinstance(x, Class) and x.name == name,
                          self.contents)
        return next(classes)

    def __str__(self):
        return join_p(self.contents, 0)
