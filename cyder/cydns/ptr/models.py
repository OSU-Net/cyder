from gettext import gettext as _

from django.db import models
from django.core.exceptions import ValidationError

from cyder.cydns.domain.models import Domain, name_to_domain
from cyder.cydns.ip.models import Ip
from cyder.cydns.ip.utils import ip_to_dns_form, ip_to_domain_name, nibbilize
from cyder.cydns.cname.models import CNAME
from cyder.cydns.models import CydnsRecord, LabelDomainMixin
from cyder.cydns.view.validation import check_no_ns_soa_condition


class BasePTR(object):
    urd = True

    def clean_reverse(self, update_reverse_domain=None):
        # This indirection is so StaticInterface can call this function
        if self.urd or update_reverse_domain:
            self.update_reverse_domain()
            self.urd = False
        check_no_ns_soa_condition(self.reverse_domain)
        self.reverse_validate_no_cname()

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

    def update_reverse_domain(self):
        # We are assuming that self.clean_ip has been called already
        rvname = nibbilize(self.ip_str) if self.ip_type == '6' else self.ip_str
        rvname = ip_to_domain_name(rvname, ip_type=self.ip_type)
        self.reverse_domain = name_to_domain(rvname)
        if (self.reverse_domain is None or self.reverse_domain.name in
                ('arpa', 'in-addr.arpa', 'ip6.arpa')):
            raise ValidationError(
                "No reverse Domain found for {0} ".format(self.ip_str)
            )

    def rebuild_reverse(self):
        if self.reverse_domain and self.reverse_domain.soa:
            self.reverse_domain.soa.schedule_rebuild()

    def dns_name(self):
        """
        Return the cononical name of this ptr that can be placed in a
        reverse zone file.
        """
        return ip_to_dns_form(self.ip_str)


class PTR(BasePTR, Ip, CydnsRecord, LabelDomainMixin):
    """
    A PTR is used to map an IP to a domain name.

    >>> PTR(ip_str=ip_str, fqdn=fqdn, ip_type=ip_type)

    """
    id = models.AutoField(primary_key=True)
    reverse_domain = models.ForeignKey(Domain, null=False, blank=True,
                                       related_name='reverse_ptr_set')

    template = _("{ip_str:$lhs_just} {ttl:$ttl_just}  "
                 "{rdclass:$rdclass_just} "
                 "{rdtype:$rdtype_just} {bind_name:1}")
    search_fields = ('ip_str', 'fqdn')

    class Meta:
        db_table = 'ptr'
        unique_together = ('ip_str', 'ip_type', 'fqdn')

    def __str__(self):
        return "{0} {1} {2}".format(str(self.ip_str), 'PTR', self.fqdn)

    def __repr__(self):
        return "<{0}>".format(str(self))

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        objects = objects or PTR.objects
        objects = objects.filter(reverse_domain__in=ctnr.domains.all())
        return objects

    @property
    def rdtype(self):
        return 'PTR'

    def save(self, *args, **kwargs):
        self.urd = kwargs.pop('update_reverse_domain', True)
        self.clean()
        super(PTR, self).save(*args, **kwargs)
        self.rebuild_reverse()

    def delete(self, *args, **kwargs):
        if self.reverse_domain.soa:
            self.reverse_domain.soa.schedule_rebuild()
        super(PTR, self).delete(*args, **kwargs)

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
        self.clean_reverse()

    def details(self):
        """For tables."""
        data = super(PTR, self).details()
        data['data'] = [
            ('Label', 'label', self.label),
            ('Domain', 'domain', self.domain),
            ('IP', 'ip_str', str(self.ip_str)),
        ]
        return data

    @staticmethod
    def eg_metadata():
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'label', 'datatype': 'string', 'editable': True},
            {'name': 'domain', 'datatype': 'string', 'editable': True},
            {'name': 'ip_str', 'datatype': 'string', 'editable': True},
        ]}
