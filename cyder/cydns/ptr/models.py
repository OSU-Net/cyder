from gettext import gettext as _

from django.db import models
from django.core.exceptions import ValidationError

from cyder.cydns.models import ViewMixin, DisplayMixin
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.models import Ip
from cyder.cydns.ip.utils import ip_to_dns_form
from cyder.cydns.validation import validate_name, validate_ttl
from cyder.base.mixins import ObjectUrlMixin
from cyder.cydns.cname.models import CNAME
from cyder.cydhcp.interface.static_intr.models import StaticInterface


class PTR(Ip, ViewMixin, ObjectUrlMixin, DisplayMixin):
    """
    A PTR is used to map an IP to a domain name.

    >>> PTR(ip_str=ip_str, name=fqdn, ip_type=ip_type)

    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, validators=[validate_name],
                            help_text="The name that this record points to.")
    ttl = models.PositiveIntegerField(default=3600, blank=True, null=True,
                                      validators=[validate_ttl])
    reverse_domain = models.ForeignKey(Domain, null=False, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    template = _("{bind_name:$lhs_just} {ttl} {rdclass:$rdclass_just} "
                 "{rdtype:$rdtype_just} {name:1}.")
    search_fields = ('ip_str', 'name')

    class Meta:
        db_table = 'ptr'
        unique_together = ('ip_str', 'ip_type', 'name')

    def __str__(self):
        return "{0} {1} {2}".format(str(self.ip_str), 'PTR', self.name)

    def __repr__(self):
        return "<{0}>".format(str(self))

    @classmethod
    def get_api_fields(cls):
        return ['ip_str', 'ip_type', 'name', 'ttl', 'description']

    def details(self):
        """For tables."""
        data = super(PTR, self).details()
        data['data'] = [
            ('Name', 'name', self.name),
            ('IP', 'ip_str', str(self.ip_str)),
        ]
        return data

    def eg_metadata(self):
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'name', 'datatype': 'string', 'editable': True},
            {'name': 'ip_str', 'datatype': 'string', 'editable': True},
        ]}

    @property
    def rdtype(self):
        return 'PTR'

    def bind_render_record(self, pk=False, **kwargs):
        self.fqdn = self.dns_name().strip('.')
        return super(PTR, self).bind_render_record(pk=pk, **kwargs)

    def save(self, *args, **kwargs):
        self.clean(update_reverse_domain=kwargs.pop('update_reverse_domain',
                                                    True))
        if self.reverse_domain and self.reverse_domain.soa:
            self.reverse_domain.soa.schedule_rebuild()
            # The reverse_domain field is in the Ip class.
        super(PTR, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.reverse_domain.soa:
            self.reverse_domain.soa.schedule_rebuild()
        super(PTR, self).delete(*args, **kwargs)

    def validate_no_cname(self):
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
        return
        # There are preexisting records that break this rule. We can't support
        # this requirement until those records are fixed
        if CNAME.objects.filter(fqdn=self.name).exists():
            raise ValidationError("PTR records must point back to a valid A "
                                  "record, not a alias defined by a CNAME."
                                  " -- RFC 1034")

    def clean(self, *args, **kwargs):
        self.validate_no_cname()
        self.clean_ip()
        # We need to check if there is an interface using our ip and name
        # because that interface will generate a ptr record.
        if (StaticInterface.objects.filter(fqdn=self.name,
                                           ip_upper=self.ip_upper,
                                           ip_lower=self.ip_lower).exists()):
            raise ValidationError("An Interface has already used this IP and "
                                  "Name.")
        if kwargs.pop('update_reverse_domain', True):
            self.update_reverse_domain()
        self.check_no_ns_soa_condition(self.reverse_domain)

    def dns_name(self):
        """
        Return the cononical name of this ptr that can be placed in a
        reverse zone file.
        """
        return ip_to_dns_form(self.ip_str)
