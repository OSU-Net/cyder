from gettext import gettext as _

from django.db import models
from django.db.models.loading import get_model
from django.core.exceptions import ValidationError
from ipaddr import AddressValueError, IPv4Address, IPv6Address

from cyder.base.models import BaseModel
from cyder.base.mixins import DisplayMixin, ObjectUrlMixin
from cyder.cydhcp.range.utils import find_range
from cyder.cydns.models import ViewMixin
from cyder.cydns.domain.models import Domain, name_to_domain
from cyder.cydns.ip.models import Ip
from cyder.cydns.ip.utils import ip_to_dns_form, ip_to_domain_name, nibbilize
from cyder.cydns.cname.models import CNAME
from cyder.cydns.validation import validate_fqdn, validate_ttl
from cyder.cydns.view.validation import check_no_ns_soa_condition


class BasePTR(object):
    """
    A :class:`BasePTR` instance must be mapped back to a Reverse :ref:`domain`
    object. A :class:`ValidationError` is raised if an eligible reverse
    :ref:`domain` cannot be found.

    The reason why an IP must be mapped back to a Reverse :ref:`domain` has to
    do with how bind files are generated. In a reverse zone file, IP addresses
    are mapped from IP to DATA. For instance a :ref:`PTR` record would
    look like this::

        IP                  DATA
        197.1.1.1   PTR     foo.bob.com

    If we were building the file ``197.in-addr.arpa``, all IP addresses
    in the ``197`` domain would need to be in this file. To reduce the
    complexity of finding records for a reverse domain, a :class:`BasePTR` is
    linked to its appropriate reverse domain when it is created. Its
    mapping is updated when its reverse domain is deleted or a more
    appropriate reverse domain is added.

    The algorithm for determining which reverse domain a :class:`BasePTR`
    belongs to is done by applying a 'longest prefix match' to all
    reverse domains in the :ref:`domain` table.

    :ref:`staticinterface` objects need to have their IP tied back to a reverse
    domain because they represent a :ref:`PTR` record as well as an
    :ref:`address_record`. Thus, they inherit from :class:`BasePtr`.
    """

    def clean(self, *args, **kwargs):
        super(BasePTR, self).clean(*args, **kwargs)

        is_new = self.pk is None

        if is_new:
            self.set_reverse_domain()
        else:
            db_self = self.__class__.objects.get(pk=self.pk)
            if db_self.ip_str != self.ip_str:
                self.set_reverse_domain()

        check_no_ns_soa_condition(self.reverse_domain)
        self.reverse_validate_no_cname()
        self.check_ip_conflict()

    def set_reverse_domain(self):
        """
        TODO: For IPv6, it might be more efficient to use a binary search to
        find the bottommost domain. zone_root_domain would still be used to
        find the root domain of that domain's zone.
        """

        self.clean_ip()  # Validate ip_str.
        if self.ip_type == '4':
            nibbles = str(IPv4Address(self.ip_str)).split('.')
        else:
            nibbles = IPv6Address(self.ip_str).exploded.replace(':', '')
        name = '.'.join(reversed(nibbles)) + (
            '.in-addr.arpa' if self.ip_type == '4' else '.ip6.arpa')
        while True:  # Find closest domain.
            try:  # Assume domain exists.
                reverse_domain = Domain.objects.get(name=name)
                break  # Found it.
            except Domain.DoesNotExist:
                pass
            name = name[name.find('.') + 1:]

        reverse_domain = reverse_domain.zone_root_domain
        if not reverse_domain:
            raise ValidationError(
                'No reverse domain found for {}'.format(self.ip_str))
        self.reverse_domain = reverse_domain

    def check_ip_conflict(self):
        StaticInterface = get_model('cyder', 'staticinterface')
        ptrs = PTR.objects.filter(ip_upper=self.ip_upper,
                                  ip_lower=self.ip_lower)
        sis = StaticInterface.objects.filter(ip_upper=self.ip_upper,
                                             ip_lower=self.ip_lower)
        if self.pk is not None:
            if isinstance(self, PTR):
                ptrs = ptrs.exclude(pk=self.pk)
            if isinstance(self, StaticInterface):
                sis = sis.exclude(pk=self.pk)

        if ptrs.exists():
            raise ValidationError("PTR already exists for %s" % self.ip_str)
        elif sis.exists():
            raise ValidationError("Static Interface already exists for %s" %
                                  self.ip_str)

    def reverse_validate_no_cname(self):
        """
        Considering existing CNAMES must be done when editing and
        creating new :class:`PTR` objects.

            "PTR records must point back to a valid A record, not a
            alias defined by a CNAME."

            -- `RFC 1912 <http://tools.ietf.org/html/rfc1912>`__

        An example of something that is not allowed::

            FOO.BAR.COM     CNAME       BEE.BAR.COM

            BEE.BAR.COM     A           128.193.1.1

            1.1.193.128     PTR         FOO.BAR.COM
            ^-- PTR's shouldn't point to CNAMES
        """
        name = self.fqdn

        if CNAME.objects.filter(fqdn=name).exists():
            raise ValidationError(
                "PTR records must point back to a valid A record, not a "
                "alias defined by a CNAME. -- RFC 1034"
            )

    def dns_name(self):
        """
        Return the cononical name of this ptr that can be placed in a
        reverse zone file.
        """
        return ip_to_dns_form(self.ip_str)


class PTR(BaseModel, BasePTR, Ip, ViewMixin, DisplayMixin, ObjectUrlMixin):
    """
    A PTR is used to map an IP to a domain name.

    >>> PTR(ip_str=ip_str, fqdn=fqdn, ip_type=ip_type)

    """
    pretty_type = 'PTR'

    id = models.AutoField(primary_key=True)
    reverse_domain = models.ForeignKey(Domain, null=False, blank=True,
                                       related_name='reverse_ptr_set')
    fqdn = models.CharField(
        max_length=255, blank=True, validators=[validate_fqdn], db_index=True
    )
    ttl = models.PositiveIntegerField(default=3600, blank=True, null=True,
                                      validators=[validate_ttl],
                                      verbose_name="Time to live")
    description = models.CharField(max_length=1000, blank=True)
    ctnr = models.ForeignKey("cyder.Ctnr", null=False,
                             verbose_name="Container")

    template = _("{reverse_domain:$lhs_just} {ttl:$ttl_just}  "
                 "{rdclass:$rdclass_just} "
                 "{rdtype:$rdtype_just} {bind_name:1}")
    search_fields = ('ip_str', 'fqdn')

    class Meta:
        app_label = 'cyder'
        db_table = 'ptr'
        unique_together = ('ip_str', 'ip_type', 'fqdn')

    def __str__(self):
        return "{0} {1} {2}".format(str(self.ip_str), 'PTR', self.fqdn)

    def __repr__(self):
        return "<{0}>".format(str(self))

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        objects = objects if objects is not None else PTR.objects
        if ctnr.name == "global":
            return objects
        objects = objects.filter(ctnr=ctnr)
        return objects

    @property
    def rdtype(self):
        return 'PTR'

    @property
    def range(self):
        rng = find_range(self.ip_str)
        return rng

    def bind_render_record(self):
        if self.ip_type == '6':
            ip = "%x" % ((self.ip_upper << 64) | self.ip_lower)
            reverse_domain = '.'.join(reversed(ip)) + ".ip6.arpa."
        else:
            reverse_domain = ('.'.join(reversed(self.ip_str.split('.'))) +
                              '.in-addr.arpa.')

        return super(PTR, self).bind_render_record(
            custom={'reverse_domain': reverse_domain})

    def save(self, *args, **kwargs):
        update_range_usage = kwargs.pop('update_range_usage', True)
        old_range = None
        if self.id is not None:
            old_ip = PTR.objects.get(id=self.id).ip_str
            old_range = find_range(old_ip)

        self.clean()
        super(PTR, self).save(*args, **kwargs)
        self.schedule_zone_rebuild()
        rng = self.range
        if rng and update_range_usage:
            rng.save()
            if old_range:
                old_range.save()

    def delete(self, *args, **kwargs):
        update_range_usage = kwargs.pop('update_range_usage', True)
        if self.reverse_domain.soa:
            self.reverse_domain.soa.schedule_rebuild()
        rng = find_range(self.ip_str)
        super(PTR, self).delete(*args, **kwargs)
        if rng and update_range_usage:
            rng.save()

    def clean(self):
        super(PTR, self).clean()
        self.clean_ip()
        # We need to check if there is a registration using our ip and name
        # because that registration will generate a ptr record.
        from cyder.cydhcp.interface.static_intr.models import StaticInterface
        if (StaticInterface.objects.filter(
                ip_upper=self.ip_upper, ip_lower=self.ip_lower).exists()):
            raise ValidationError(
                "A static interface has already used %s" % self.ip_str
            )
        rng = self.range
        if rng:
            if self.range.range_type == "dy":
                raise ValidationError("Cannot create PTRs in dynamic ranges.")
            if self.ctnr not in self.range.ctnr_set.all():
                raise ValidationError("Could not create PTR because %s is "
                                      "not in this container." % self.ip_str)

    def schedule_zone_rebuild(self):
        if self.reverse_domain.soa:
            self.reverse_domain.soa.schedule_rebuild()

    def details(self):
        """For tables."""
        data = super(PTR, self).details()
        data['data'] = [
            ('Target', 'fqdn', self.fqdn),
            ('IP', 'ip_str', str(self.ip_str)),
        ]
        return data

    @staticmethod
    def eg_metadata():
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'fqdn', 'datatype': 'string', 'editable': True},
            {'name': 'ip_str', 'datatype': 'string', 'editable': True},
        ]}
