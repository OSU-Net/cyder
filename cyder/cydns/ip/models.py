from django.db import models
from django.core.exceptions import ValidationError

from cyder.base.constants import IP_TYPES, IP_TYPE_6, IP_TYPE_4

from cyder.cydhcp.utils import two_to_one

import ipaddr


class Ip(models.Model):
    """An :class:`Ip` instance represents either an IPv4 or IPv6 address.

    :class:`Ip` instances are used in the :ref:`address_record` (A and AAAA
    records), :ref:`ptr`, and the :ref:`staticinterface` classes.

    :class:`Ip` instances in a :ref:`ptr` record must be mapped back to a
    Reverse :ref:`domain` object. A :class:`ValidationError` is raised if an
    eligible Reverse :ref:`domain` cannot be found when trying to create the
    :ref:`ptr`'s :class:`Ip`.

    The reason why an IP must be mapped back to a Reverse :ref:`domain` has to
    do with how bind files are generated. In a reverse zone file, IP addresses
    are mapped from IP to DATA. For instance an :ref:`ptr` record would
    look like this::

        IP                  DATA
        197.1.1.1   PTR     foo.bob.com

    If we were building the file ``197.in-addr.arpa``, all IP addresses
    in the ``197`` domain would need to be in this file. To reduce the
    complexity of finding records for a reverse domain, an :class:`Ip` is
    linked to its appropriate reverse domain when it is created. Its
    mapping is updated when its reverse domain is deleted or a more
    appropriate reverse domain is added.  Keeping the :class:`Ip` field on
    :ref:`ptr` will help performance when building reverse zone files.

    The algorithm for determining which reverse domain an :class:`Ip`
    belongs to is done by applying a 'longest prefix match' to all
    reverse domains in the :ref:`domain` table.

    :ref:`address_record` objects need the IP validation that happens in this
    class but do not need their :class:`Ip`s to be tied back to a reverse
    domain.

    :ref:`staticinterface` objects need to have their IP tied back to reverse
    domain because they represent a :ref:`PTR` record as well as an
    :ref:`address_record`.

    .. note::
        Django's BigInteger wasn't "Big" enough, so there is code
        in `cydns/ip/sql/ip.sql` that Alters the IP table.

    .. note::
        This class is abstract.

    """
    ip_str = models.CharField(max_length=39, editable=True, verbose_name='IP',
                help_text="IP address in dotted quad or dotted colon format")
    # ip_upper/lower are calculated from ip_str on ip_clean.
    # TODO: rename ip_* to ipaddr_*
    ip_upper = models.BigIntegerField(null=True, blank=True)
    ip_lower = models.BigIntegerField(null=True, blank=True)
    # TODO: Should reverse_domain go into the PTR model?  I would think
    # it shouldn't because it is used in this class during the ip_clean
    # function.  Technically the ip_clean function would work if the
    # field existed in the PTR model, but overall it would hurt
    # readability.
    #
    # reactor.addCallback(think_about_it)
    # This can't be factored out because the related name classes. i.e.:
    # address_record.addressrecord: Accessor for field 'domain' clashes with
    # related field 'Domain.addressrecord_set'. Add a related_name argument to
    # the definition for 'domain'.
    # reverse_domain = models.ForeignKey(Domain, null=True, blank=True)
    ip_type = models.CharField(
        max_length=1, choices=IP_TYPES.items(), editable=True,
        help_text='IPv4 or IPv6 Address type'
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

    def clean_ip(self, update_reverse_domain=True):
        """
        The clean method in Ip is different from the rest. It needs
        to be called with the update_reverse_domain flag. Sometimes we
        need to not update the reverse domain of an IP (i.e. when we are
        deleting a reverse_domain).
        """
        # TODO: It's a fucking hack. Car babies.
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
