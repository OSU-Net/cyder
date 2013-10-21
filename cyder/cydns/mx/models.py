from django.db import models
from django.core.exceptions import ValidationError

from cyder.cydns.models import CydnsRecord
from cyder.cydns.cname.models import CNAME

from cyder.cydns.validation import validate_mx_priority
from cyder.cydns.validation import validate_fqdn
from cyder.cydns.models import LabelDomainMixin

# import reversion

from gettext import gettext as _


class MX(LabelDomainMixin, CydnsRecord):
    """
    >>> MX(label=label, domain=domain, server=server, priority=prio,
    ...     ttl=tll)
    """
    id = models.AutoField(primary_key=True)
    # The mail server this record should point to.
    server = models.CharField(max_length=100, validators=[validate_fqdn],
                              help_text="The name of the mail server this "
                              "record points to.")
    priority = models.PositiveIntegerField(null=False,
                                           validators=[validate_mx_priority])
    template = _("{bind_name:$lhs_just} {ttl:$ttl_just}  "
                 "{rdclass:$rdclass_just} "
                 "{rdtype:3} {priority:$prio_just}  "
                 "{server:$rhs_just}.")
    search_fields = ('fqdn', 'server')

    class Meta:
        db_table = 'mx'
        # label and domain in CydnsRecord
        unique_together = ('domain', 'label', 'server', 'priority')

    def __str__(self):
        return "{0} {1} {3} {4} {5}".format(self.fqdn, self.ttl, 'IN', 'MX',
                                            self.priority, self.server)

    def __repr__(self):
        return "<MX '{0}'>".format(str(self))

    def details(self):
        """For tables."""
        data = super(MX, self).details()
        data['data'] = [
            ('Label', 'label', self.label),
            ('Domain', 'domain', self.domain),
            ('Server', 'server', self.server),
            ('Priority', 'priority', self.priority),
            ('TTL', 'ttl', self.ttl)
        ]
        return data

    @staticmethod
    def eg_metadata():
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'label', 'datatype': 'string', 'editable': True},
            {'name': 'domain', 'datatype': 'string', 'editable': True},
            {'name': 'server', 'datatype': 'string', 'editable': True},
            {'name': 'priority', 'datatype': 'integer', 'editable': True},
            {'name': 'ttl', 'datatype': 'integer', 'editable': True},
        ]}

    @property
    def rdtype(self):
        return 'MX'

    def save(self, *args, **kwargs):
        self.full_clean()
        super(MX, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        super(MX, self).clean(*args, **kwargs)
        super(MX, self).check_for_cname()
        self.no_point_to_cname()

    def no_point_to_cname(self):
        """MX records should not point to CNAMES."""
        # TODO, cite an RFC.
        if CNAME.objects.filter(fqdn=self.server):
            raise ValidationError("MX records should not point to CNAMES.")
