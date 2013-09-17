import ipaddr
import re
from django.core.exceptions import ValidationError

from cyder.cydns.validation import validate_domain_name
from cyder.base.eav.utils import strip_and_get_base, validate_list


### Naming conventions in this module:
###
###     - A function that does not start with '_' is a validator that can be
###       used in Key.value_type
###
###     - A function that starts with '_' is a utility function not useful
###       outside this module
###
###         - A function like '_foo' raises an exception if the value is not
###           valid
###
###         - A function like '_is_foo' returns a bool indicating whether the
###           value is valid


### Parameter assumptions:
###     - 'value' in all functions:
###         - basestring object
###         - not '' or u''
###         - no leading or trailing spaces


VALUE_TYPES = (
    ('flag', "flag: 'yes', 'no', 'true', or 'false' (case-insensitive)"),
    ('text', "text: 'text' -> '\"text\"'"),
    ('string', "string: 'text' -> '\"text\"' or "
               "'1a:2b:3c:4d' -> '1a:2b:3c:4d'"),
    ('identifier', "identifier: 'identifier'"),
    ('int8', "int8: 8-bit signed integer"),
    ('uint8', "uint8: 8-bit unsigned integer"),
    ('int16', "int16: 16-bit signed integer"),
    ('uint16', "uint16: 16-bit unsigned integer"),
    ('int32', "int32: 32-bit signed integer"),
    ('uint32', "uint32: 32-bit unsigned integer"),
    ('host', "host: IPv4 address ('1.2.3.4') or hostname ('example.com')"),
    ('domain', "domain: 'example.com'"),
    ('leasetime', "lease time: uint32 or 'infinite'"),
    ('flag_optional_text', "'flag [text]'"),
    ('uint8_list', "'uint8, uint8, uint8 ...'"),
    ('uint16_list', "'uint16, uint16, uint16 ...'"),
    ('host_list', "host list: 'host, host, host ...'"),
    ('host_pair', "'host host'"),
    ('host_pair_list', "'host host, host host, host host ...'"),
    ('flag_host_list', "'flag host, host, host ...'"),
    ('domain_list', "domain list: '\"domain\", \"domain\", \"domain\" ...'"),
    ('ddnsstyle', "DDNS style"),
    ('syslogfacility', "syslog facility"),
    ('ldapmethod', "LDAP method"),
    ('ldapsslusage', "ldap-ssl-usage value"),
    ('ldaptlsreqcert', "ldap-tls-reqcert value"),
    ('ldaptlscrlcheck', "ldap-tls-crlcheck value"),
)


###########################################
### Utility functions that return bools ###
###########################################

# These are not validators. They return bools.


def _is_ip(value):
    try:
        ipaddr.IPAddress(value)
        return True
    except ValueError:
        return False


def _is_ip4(value):
    try:
        ipaddr.IPv4Address(value)
        return True
    except ipaddr.AddressValueError:
        return False


def _is_ip6(value):
    try:
        ipaddr.IPv6Address(value)
        return True
    except ipaddr.AddressValueError:
        return False


def _is_domain(value):
    if value[-1] == '.':
        value = value[:-1]

    try:
        validate_domain_name(value)
        return True
    except ValidationError:
        # validate_domain_name doesn't always include the invalid domain in its
        # exceptions. We need to do that for it.
        return False


def _is_uint(value, bits):
    try:
        value, base = strip_and_get_base(value)
        if base == 10 and not value.isdigit(): # "performance" hack
            return False
        return 0 <= int(value, base) <= (2**bits - 1)
    except ValueError:
        return False


def _is_int(value, bits):
    try:
        value, base = strip_and_get_base(value)
        return -(2**(bits-1)) <= int(value, base) <= (2**(bits-1) - 1)
    except ValueError:
        return False


###############################################
### Utility functions that raise exceptions ###
###############################################

# These are not validators. They do raise exceptions, though.


def _uint(value, bits):
    if not _is_uint(value, bits):
        raise ValidationError("Invalid {0}-bit unsigned integer '{1}'"
                              .format(bits, value))


def _int(value, bits):
    if not _is_int(value, bits):
        raise ValidationError("Invalid {0}-bit signed integer '{1}'"
                              .format(bits, value))

def _unquote(value):
    if not value[0] == value[-1] == '"':
        raise ValidationError("'{0}' must be quoted".format(value))
    return value[1:-1]


def _dhcpclass(value):
    if '"' in value:
        raise ValidationError("Invalid DHCP class '{0}'".format(value))


##################
### Validators ###
##################

# These return None or raise an exception


def flag(value):
    # ISC dhcpd ignores capitalization in flags. Why? No idea.
    if not value.lower() in ('on', 'off', 'true', 'false'):
        raise ValidationError("Invalid flag '{0}'".format(value))


def text(value):
    if '"' in value:
        raise ValidationError("Invalid text '{0}'".format(value))


def string(value):
    if '"' in value:
        raise ValidationError("Invalid string '{0}'".format(value))


_identifier_regex = re.compile(r'^[a-zA-Z0-9-][a-zA-Z0-9_-]*$')


def identifier(value):
    if not (_identifier_regex.match(value) and
            re.search(r'[a-zA-Z_-]', value)): # at least one non-numeric char
        raise ValidationError("Invalid identifier '{0}'".format(value))


def uint8(value):
    _uint(value, 8)


def int8(value):
    _int(value, 8)


def uint16(value):
    _uint(value, 16)


def int16(value):
    _int(value, 16)


def uint32(value):
    _uint(value, 32)


def int32(value):
    _int(value, 32)


def host(value):
    """
    Where ISC dhcpd expects a host (what it calls an 'ip-address'), it
    validates the value as a hostname. The semantics differs depending on
    whether the value resembles an IPv4 address, but the validation does not.
    Therefore, a malformed IPv4 address that is still a valid hostname passes
    validation and is interpreted as a hostname. It's up to the user to make
    sure that what they think is an IPv4 address actually is one.

    NOTE: validate_domain_name is outside of this module and, therefore, its
    jurisdiction. At the moment, validate_domain_name considers domain names
    like '1.2.3.4' to be valid.  However, if that behavior changes in the
    future, host()'s behavior must not. That's why we fall back to _is_ip4.
    """

    if not (_is_domain(value) or _is_ip4(value)):
        raise ValidationError("Invalid host '{0}'".format(value))


def domain(value):
    if not _is_domain(value):
        raise ValidationError("Invalid domain '{0}'".format(value))


def leasetime(value):
    if not (_is_uint(value, 32) or value == 'infinite'):
        raise ValidationError("Invalid lease time '{0}'".format(value))


def flag_optional_text(value):
    splat = value.split(None, 1)

    if len(splat) == 1:
        flag(value)
    else:
        flag(splat[0])
        text(_unquote(splat[1]))


def uint8_list(value):
    list_validator(value, uint8)


def uint16_list(value):
    list_validator(value, uint16)


def host_list(value):
    validate_list(value, host)


def host_pair(value):
    splat = value.split()
    if len(splat) != 2:
        comparison = 'few' if len(splat) < 2 else 'many'
        raise ValidationError("Invalid host pair '{0}'; too {1} hosts"
                              .format(value, comparison))
    [first, second] = splat
    host(first)
    host(second)


def host_pair_list(value):
    validate_list(value, host_pair)


def flag_host_list(value):
    splat = value.split(None, 1) # split on first whitespace
    if len(splat) == 1:
        raise ValidationError("Invalid flag and host list; missing host list"
                              .format(value))
    [first, rest] = splat
    flag(first)
    host_list(rest)


def domain_list(value):
    validate_list(value, lambda x: domain(_unquote(x)))


def ddnsstyle(value):
    if value not in ('none', 'ad-hoc', 'interim'):
        raise ValidationError("Invalid DDNS style")


def syslogfacility(value):
    if value not in ('kern', 'user', 'mail', 'daemon', 'auth', 'syslog',
                     'lpr', 'news', 'uucp', 'cron', 'authpriv', 'ftp',
                     'local0', 'local1', 'local2', 'local3', 'local4',
                     'local5', 'local6', 'local7'):
        raise ValidationError("Invalid syslog facility")


def ldapmethod(value):
    if value not in ('static', 'dynamic'):
        raise ValidationError("Invalid LDAP method")


def ldapsslusage(value):
    if value not in ('off', 'on', 'ldaps', 'start_tls'):
        raise ValidationError("Invalid ldap-ssl-usage value") # FIXME?


def ldaptlsreqcert(value):
    if value not in ('never', 'hard', 'demand', 'allow', 'try'):
        raise ValidationError("Invalid ldap-tls-reqcert value") # FIXME?


def ldaptlscrlcheck(value):
    if value not in ('none', 'peer', 'all'):
        raise ValidationError("Invalid ldap-tls-crlcheck value") # FIXME?
