import ipaddr
from django.core.exceptions import ValidationError
from cyder.cydns.validation import validate_ip_type
from cyder.cydns.domain.utils import name_to_domain


def _labels_to_reverse_name(labels, ip_type):
    """
    Convert a list of octets (IPv4) or nibbles (IPv6) to a reverse domain name
    """
    name = '.'.join(list(reversed(labels)))
    name += '.in-addr.arpa' if ip_type == '4' else '.ip6.arpa'
    return name


def ip_prefix_to_reverse_name(ip, ip_type):
    """
    Convert an IP prefix in octet (IPv4) or nibble (IPv6) form to a reverse
    domain name
    """
    return _labels_to_reverse_name(ip.split('.'), ip_type=ip_type)


def ip_to_reverse_name(ip):
    """Convert an IP address to a reverse domain name"""
    ip_type = '6' if ':' in ip else '4'
    if ip_type == '4':
        labels = ip.split('.')
    else:
        ip = ipaddr.IPv6Address(ip).exploded
        labels = list(ip.replace(':', ''))

    return _labels_to_reverse_name(labels, ip_type)


def reverse_name_to_ip(name):
    if name.endswith('in-addr.arpa'):  # IPv4
        octets = reversed(name.split('.')[:-2])
        return '.'.join(octets)
    elif name.endswith('ip6.arpa'):  # IPv6
        nibbles = reversed(name.split('.')[:-2])
        b = bytearray()
        count = 0
        for nibble in nibbles:
            if count != 0 and count % 4 == 0:
                b.append(':')
            b.append(nibble)
            count += 1
        while count % 4 != 0:
            b.append('0')
            count += 1
        if count < 64:
            b.extend('::')
        return str(b)
    else:
        raise ValueError('Invalid reverse domain')


"""
>>> nibbilize('2620:0105:F000::1')
'2.6.2.0.0.1.0.5.F.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.1'
>>> nibbilize('2620:0105:F000:9::1')
'2.6.2.0.0.1.0.5.f.0.0.0.0.0.0.9.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.1'
>>> nibbilize('2620:0105:F000:9:0:1::1')
'2.6.2.0.0.1.0.5.f.0.0.0.0.0.0.9.0.0.0.0.0.0.0.1.0.0.0.0.0.0.0.1'
"""


def nibbilize(addr):
    """
    Given an IPv6 address is 'colon' format, return the address in 'nibble'
    form::

        nibblize('2620:0105:F000::1')
        '2.6.2.0.0.1.0.5.F.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.1'

    :param addr: The ip address to convert
    :type addr: str
    """
    try:
        ip_str = ipaddr.IPv6Address(str(addr)).exploded
    except ipaddr.AddressValueError:
        raise ValidationError("Error: Invalid IPv6 address {0}.".format(addr))

    return '.'.join(list(ip_str.replace(':', '')))


def i64_to_i128(upper_int, lower_int):
    return upper_int << 64 + lower_int


def i128_to_i64(bigint):
    ip_upper = bigint >> 64
    ip_lower = bigint & (1 << 64) - 1
    return ip_upper, ip_lower
