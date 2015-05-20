import re
from gettext import gettext as _

from django.db import models
from django.core.exceptions import ValidationError

from cyder.base.utils import transaction_atomic
from cyder.cydns.models import CydnsRecord, LabelDomainMixin


is_sha1 = re.compile("[0-9a-fA-F]{40}")


def validate_sha1(sha1):
    if not is_sha1.match(sha1):
        raise ValidationError("Invalid key.")


class SSHFP(LabelDomainMixin, CydnsRecord):
    """
    >>> SSHFP(label=label, domain=domain, key=key_data,
    ... algorithm_number=algo_num, fingerprint_type=fing_type)
    """

    pretty_type = 'SSHFP'

    id = models.AutoField(primary_key=True)
    key = models.CharField(max_length=256, validators=[validate_sha1])
    algorithm_number = models.PositiveIntegerField(
        null=False, blank=False, choices=((1, 'RSA (1)'), (2, 'DSA (2)')),
        verbose_name='algorithm')
    fingerprint_type = models.PositiveIntegerField(
        null=False, blank=False, default=1, choices=((1, 'SHA-1 (1)'),))
    ctnr = models.ForeignKey("cyder.Ctnr", null=False,
                             verbose_name="Container")

    template = _("{bind_name:$lhs_just} {ttl:$ttl_just}  "
                 "{rdclass:$rdclass_just} "
                 "{rdtype:$rdtype_just} {algorithm_number} {fingerprint_type} "
                 "{key:$rhs_just}")

    search_fields = ("fqdn", "key")

    class Meta:
        app_label = 'cyder'
        db_table = 'sshfp'
        unique_together = ('domain', 'label')

    def details(self):
        """For tables."""
        algorithms = {1: 'RSA (1)', 2: 'DSA (2)'}
        fingerprint_types = {1: 'SHA-1 (1)'}
        data = super(SSHFP, self).details()
        data['data'] = [
            ('Label', 'label', self.label),
            ('Domain', 'domain', self.domain),
            ('Algorithm', 'algorithm_number',
                algorithms[self.algorithm_number]),
            ('Fingerprint Type', 'fingerprint_type',
                fingerprint_types[self.fingerprint_type]),
            ('Key', 'key', self.key),
        ]
        return data

    def __unicode__(self):
        return u'{} SSHFP {} {} {}...'.format(
            self.fqdn, self.algorithm_number, self.fingerprint_type,
            self.key[:8])

    @staticmethod
    def eg_metadata():
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'label', 'datatype': 'string', 'editable': True},
            {'name': 'domain', 'datatype': 'string', 'editable': True},
            {'name': 'algorithm', 'datatype': 'integer', 'editable': True},
            {'name': 'fingerprint_type', 'datatype': 'integer',
             'editable': True},
            {'name': 'key', 'datatype': 'string', 'editable': True},
        ]}

    @property
    def rdtype(self):
        return 'SSHFP'

    @transaction_atomic
    def save(self, *args, **kwargs):
        self.full_clean()

        super(SSHFP, self).save(*args, **kwargs)
