from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

from cyder.base.constants import IP_TYPE_4, IP_TYPE_6
from cyder.cydns.validation import validate_domain_name

from ipaddr import IPv4Address, IPv6Address, AddressValueError
import re


is_attr = re.compile("^attr_\d+$")


def list_validator(things, validator):
    return all([validator(thing.strip()) for thing in things.split(',')])


def is_valid_ip(ip, ip_type=None):
    def validate_ip(ip, addr_type):
        try:
            addr_type(ip)
            return True
        except AddressValueError:
            return False

    if ip_type == IP_TYPE_4:
        return validate_ip(ip, IPv4Address)
    elif ip_type == IP_TYPE_6:
        return validate_ip(ip, IPv6Address)
    else:
        return validate_ip(ip, IPv4Address) or validate_ip(ip, IPv6Address)


def is_valid_domain(name):
    if name and name[-1] == '.':
        name = name[:-1]

    try:
        validate_domain_name(name)
        return True
    except ValidationError:
        return False


def is_valid_ip_or_domain(x, ip_type=None):
    return is_valid_ip(x, ip_type) or is_valid_domain(x)


def check_int(val, bits):
    return val.isdigit() and int(val) < (2 ** bits - 1)


def is_int8(val):
    return check_int(val, 8)


def is_int16(val):
    return check_int(val, 16)


def is_int32(val):
    return check_int(val, 32)


def is_bool(val):
    return val.lower() in ['on', 'off', 'true', 'false']


def is_ip_list(option_list, ip_type=None):
    return list_validator(option_list, lambda ip: is_valid_ip(ip, ip_type))


def is_ip_or_domain_list(option_list, ip_type=None):
    return list_validator(option_list,
                          lambda x: is_valid_ip_or_domain(x, ip_type))


def is_bool_and_ip_list(option_list, ip_type=None):
    # FIXME: if option_list was stripped before being stored, strip() on the
    # next line is not necessary
    option_list_parts = option_list.strip().split()
    if is_bool(option_list_parts[0]) and len(option_list_parts) == 2:
        return is_ip_list(option_list_parts[1], ip_type)
    else:
        return is_ip_list(option_list, ip_type)


def is_domain_list(option_list, ip_type=IP_TYPE_4):
    return list_validator(option_list, is_valid_domain)


def is_int32_list(val):
    return list_validator(val, is_int32)
