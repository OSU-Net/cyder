from django.db import models
from django.core.exceptions import ValidationError

from cyder.base.constants import IP_TYPES, IP_TYPE_6, IP_TYPE_4
from cyder.cydns.validation import validate_ip_type

from cyder.cydhcp.utils import two_to_one

import ipaddr


class Ip(models.Model):
    """An :class:`Ip` instance represents either an IPv4 or IPv6 address.

    :class:`Ip` instances are used in the :ref:`address_record` (A and AAAA
    records), :ref:`ptr`, and the :ref:`staticinterface` classes.

    .. note::
        Django's BigInteger wasn't "Big" enough, so there is code
        in `cyder/sql/cyder.sql` that alters the IP table.

    .. note::
        This class is abstract.

    """
    ip_str = models.CharField(
        max_length=39, editable=True, verbose_name='IP address')
    # ip_upper/lower are calculated from ip_str on clean_ip.
    ip_upper = models.BigIntegerField(null=True, blank=True)
    ip_lower = models.BigIntegerField(null=True, blank=True)
    ip_type = models.CharField(
        verbose_name='IP address type', max_length=1,
        choices=IP_TYPES.items(), default=IP_TYPE_4,
        validators=[validate_ip_type]
    )

    class Meta:
        abstract = True

    def __int__(self):
        if self.ip_type == IP_TYPE_4:
            return self.ip_lower
        return (self.ip_upper * (2 ** 64)) + self.ip_lower

    def get_wrapped_ip(self):
        if self.ip_type == IP_TYPE_4:
            ip_klass = ipaddr.IPv4Address
        else:
            ip_klass = ipaddr.IPv6Address
        return ip_klass(two_to_one(self.ip_upper, self.ip_lower))

    def clean_ip(self):
        if self.ip_type == IP_TYPE_4:
            Klass = ipaddr.IPv4Address
        elif self.ip_type == IP_TYPE_6:
            Klass = ipaddr.IPv6Address
        else:
            raise ValidationError("Invalid IP type {0}".format(self.ip_type))
        try:
            ip = Klass(self.ip_str)
            self.ip_str = str(ip)
        except ipaddr.AddressValueError:
            raise ValidationError("Invalid IP address {0}".format(self.ip_str))

        if self.ip_type == IP_TYPE_4:
            self.ip_upper, self.ip_lower = 0, int(ip)
        else:  # We already guarded against a non-'6' ip_type
            self.ip_upper, self.ip_lower = ipv6_to_longs(int(ip))

    def validate_ip_str(self):
        if not isinstance(self.ip_str, basestring):
            raise ValidationError("Plase provide the string representation"
                                  "of the IP")


def ipv6_to_longs(addr):
    """This function will turn an IPv6 into two longs. The first number
    represents the first 64 bits of the address and the second represents
    the lower 64 bits.

    :param addr: IPv6 to be converted.
    :type addr: str
    :returns: (ip_upper, ip_lower) -- (int, int)
    :raises: ValidationError
    """
    try:
        ip = ipaddr.IPv6Address(addr)
    except ipaddr.AddressValueError:
        raise ValidationError("AddressValueError: Invalid IPv6 address {0}".
                              format(addr))
    # TODO: Use int() instead of _int. Make sure tests pass.
    ip_upper = ip._ip >> 64  # Put the last 64 bits in the first 64
    ip_lower = ip._ip & (1 << 64) - 1  # Mask off the last 64 bits
    return (ip_upper, ip_lower)
