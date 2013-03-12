from gettext import gettext as _

from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist

import cydns
from cyder.cydns.cname.models import CNAME
from cyder.cydns.view.models import View
from cyder.cydns.ip.models import Ip
from cyder.cydns.models import set_fqdn, check_for_cname
from cyder.cydns.models import check_TLD_condition
from cyder.cydns.validation import (validate_first_label, validate_name,
                                    validate_ttl)
from cyder.cydns.domain.models import Domain
from cyder.base.mixins import ObjectUrlMixin, DisplayMixin
from cyder.cydns.soa.utils import update_soa

# import reversion


class BaseAddressRecord(Ip, ObjectUrlMixin, DisplayMixin):
    """AddressRecord is the class that generates A and AAAA records

        >>> AddressRecord(label=label, domain=domain_object, ip_str=ip_str,
        ... ip_type=ip_type)

    """
    label = models.CharField(
        max_length=63, blank=True, null=True,
        validators=[validate_first_label],
        help_text='The short hostname goes here. If this is a '
        'record ' 'for the selected domain, leave this field '
        'blank')
    domain = models.ForeignKey(Domain, null=False, help_text='FQDN of the '
                               'domain after the short hostname. '
                               '(Ex: <i>Vlan</i>.<i>DC</i>.mozilla.com)')
    fqdn = models.CharField(max_length=255, blank=True, null=True,
                            validators=[validate_name])
    ttl = models.PositiveIntegerField(default=3600, blank=True, null=True,
                                      validators=[validate_ttl],
                                      help_text='Time to Live of the record')
    description = models.CharField(max_length=1000, blank=True, null=True,
                                   help_text="A description of this record.")
    views = models.ManyToManyField(View, blank=True)

    search_fields = ('fqdn', 'ip_str')

    class Meta:
        abstract = True

    def __str__(self):
        return '{0} {1} {2}'.format(self.fqdn,
                                    self.record_type(), str(self.ip_str))

    def __repr__(self):
        return '<Address Record "{0}">'.format(str(self))

    def details(self):
        """For tables."""
        data = super(BaseAddressRecord, self).details()
        data['data'] = [
            ('Domain', 'domain__name', self.domain),
            ('Record Type', 'record_type', self.record_type()),
            ('IP', 'ip_str', str(self.ip_str)),
            ('Name', 'fqdn', self.fqdn),
        ]
        return data

    def eg_metadata(self):
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'fqdn', 'datatype': 'string', 'editable': True},
            {'name': 'record_type', 'datatype': 'string', 'editable': False},
            {'name': 'ip_str', 'datatype': 'string', 'editable': True},
        ]}

    @property
    def rdtype(self):
        if self.ip_type == '6':
            return 'AAAA'
        return 'A'

    @classmethod
    def get_api_fields(cls):
        return ['fqdn', 'ip_str', 'ip_type', 'description', 'ttl']

    def save(self, *args, **kwargs):
        self.full_clean()
        set_fqdn(self)
        check_TLD_condition(self)
        update_soa(self)
        if self.pk:
            # We need to get the domain from the db. If it's not our current
            # domain, call prune_tree on the domain in the db later.
            db_domain = self.__class__.objects.get(pk=self.pk).domain
            if self.domain == db_domain:
                db_domain = None
        else:
            db_domain = None
        super(BaseAddressRecord, self).save(*args, **kwargs)
        if db_domain:
            from cyder.cydns.utils import prune_tree
            prune_tree(db_domain)

    def clean(self, *args, **kwargs):
        validate_glue = kwargs.pop('validate_glue', True)
        if validate_glue:
            self.check_glue_status()
        set_fqdn(self)
        check_TLD_condition(self)
        try:
            if self.domain and self.domain.delegated:
                self.validate_delegation_conditions()
        except ObjectDoesNotExist:
            pass
        check_for_cname(self)

        urd = kwargs.pop('update_reverse_domain', False)
        self.clean_ip(update_reverse_domain=urd)

        from cyder.cydhcp.interface.static_intr.models import StaticInterface
        if not kwargs.pop('ignore_interface', False):
            if StaticInterface.objects.filter(fqdn=self.fqdn,
                                              ip_upper=self.ip_upper,
                                              ip_lower=self.ip_lower).exists():
                raise ValidationError('A Static Interface has already '
                                      'reserved this A record.')

    def delete(self, *args, **kwargs):
        """Address Records that are glue records or that are pointed to
        by a CNAME should not be removed from the database.
        """
        if kwargs.pop('validate_glue', True):
            if self.nameserver_set.exists():
                raise ValidationError(
                    "Cannot delete the record {0}. It is a ' 'glue record."
                    .format(self.record_type()))
        if kwargs.pop('check_cname', True):
            if CNAME.objects.filter(target=self.fqdn):
                raise ValidationError('A CNAME points to this {0} record. '
                                      'Change the CNAME before deleting this '
                                      'record.'.format(self.record_type()))

        from cyder.cydns.utils import prune_tree
        objs_domain = self.domain
        super(BaseAddressRecord, self).delete(*args, **kwargs)
        prune_tree(objs_domain)

    def set_fqdn(self):
        set_fqdn(self)

    def validate_delegation_conditions(self):
        """If our domain is delegated then an A record can only have a
        name that is the same as a nameserver in that domain (glue)."""
        if self.domain.nameserver_set.filter(server=self.fqdn).exists():
            return
        else:
            # Confusing error messege?
            raise ValidationError('You can only create A records in a '
                                  'delegated domain that have an NS record '
                                  'pointing to them.')

    def check_glue_status(self):
        """If this record is a "glue" record for a Nameserver instance,
        do not allow modifications to this record. The Nameserver will
        need to point to a different record before this record can
        be updated.
        """
        if self.pk is None:
            return
        # First get this object from the database.cydns and compare it to the
        # nameserver.nameserver.  object about to be saved.
        db_self = AddressRecord.objects.get(pk=self.pk)
        if db_self.label == self.label and db_self.domain == self.domain:
            return
        # The label of the domain changed. Make sure it's not a glue record
        Nameserver = cydns.nameserver.models.Nameserver
        if Nameserver.objects.filter(addr_glue=self).exists():
            raise ValidationError('This record is a glue record for a '
                                  'Nameserver. Change the Nameserver to '
                                  'edit this record.')

    def record_type(self):
        # If PTR didn't share this field, we would use 'A' and 'AAAA'
        # instead of '4' and '6'.
        if self.ip_type == '4':
            return 'A'
        else:
            return 'AAAA'


class AddressRecord(BaseAddressRecord):
    """AddressRecord is the class that generates A and AAAA records

        >>> AddressRecord(label=label, domain=domain_object, ip_str=ip_str,
        ... ip_type=ip_type)

    """
    id = models.AutoField(primary_key=True)
    reverse_domain = models.ForeignKey(Domain, null=True, blank=True,
                                       related_name='addressrecordomain_set')

    template = _("{bind_name:$lhs_just} {ttl} {rdclass:$rdclass_just} "
                 "{rdtype:$rdtype_just} {ip_str:$rhs_just}")

    class Meta:
        db_table = 'address_record'
        unique_together = ('label', 'domain', 'fqdn', 'ip_upper', 'ip_lower',
                           'ip_type')

## reversion.(AddressRecord)
