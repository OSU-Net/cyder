from gettext import gettext as _

from django.db import models
from django.core.exceptions import ValidationError

from cyder.base.constants import IP_TYPE_6, IP_TYPE_4
from cyder.base.utils import transaction_atomic
from cyder.cydhcp.range.utils import find_range
from cyder.cydns.cname.models import CNAME
from cyder.cydns.ip.models import Ip
from cyder.cydns.models import CydnsRecord, LabelDomainMixin


class BaseAddressRecord(Ip, LabelDomainMixin, CydnsRecord):
    """
    AddressRecord is the class that generates A and AAAA records

        >>> AddressRecord(label=label, domain=domain_object, ip_str=ip_str,
        ... ip_type=ip_type)

    """
    search_fields = ('fqdn', 'ip_str')
    sort_fields = ('fqdn', 'ip_str')

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'{} {} {}'.format(self.fqdn, self.rdtype, self.ip_str)

    @property
    def rdtype(self):
        if self.ip_type == IP_TYPE_6:
            return 'AAAA'
        return 'A'

    @staticmethod
    def eg_metadata():
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'label', 'datatype': 'string', 'editable': True},
            {'name': 'domain', 'datatype': 'string', 'editable': True},
            {'name': 'obj_type', 'datatype': 'string', 'editable': False},
            {'name': 'ip_str', 'datatype': 'string', 'editable': True},
        ]}

    def clean(self, *args, **kwargs):
        ignore_intr = kwargs.pop("ignore_intr", False)
        validate_glue = kwargs.pop("validate_glue", True)

        super(BaseAddressRecord, self).clean(*args, **kwargs)

        self.clean_ip()
        self.check_name_ctnr_collision()
        if validate_glue:
            self.check_glue_status()
        if not ignore_intr:
            self.check_intr_collision()

    def delete(self, *args, **kwargs):
        """
        Address Records that are glue records or that are pointed to
        by a CNAME should not be removed from the database.
        """
        if kwargs.pop('validate_glue', True):
            if self.nameserver_set.exists():
                raise ValidationError(
                    'Cannot delete this address record. It is a glue record.')
        if kwargs.pop('check_cname', True):
            if CNAME.objects.filter(target=self.fqdn):
                raise ValidationError(
                    'A CNAME points to this address record. Change the CNAME '
                    'before deleting this record.')
        super(BaseAddressRecord, self).delete(*args, **kwargs)

    def check_name_ctnr_collision(self):
        """
        Allow ARs with the same name iff they have the same container.
        Allow ARs to share a name with a static interface iff they have the
            same container.
        """

        from cyder.cydhcp.interface.static_intr.models import StaticInterface
        from cyder.core.ctnr.models import Ctnr
        assert self.fqdn
        try:
            self.ctnr
        except Ctnr.DoesNotExist:
            # By this point, Django will already have encountered a
            # Validation error about the ctnr field, so there's no need to
            # raise another one.
            return

        ars = (AddressRecord.objects.filter(fqdn=self.fqdn)
                                    .exclude(ctnr=self.ctnr))
        sis = (StaticInterface.objects.filter(fqdn=self.fqdn)
                                      .exclude(ctnr=self.ctnr))

        if isinstance(self, AddressRecord):
            ars = ars.exclude(pk=self.pk)
        elif isinstance(self, StaticInterface):
            sis = sis.exclude(pk=self.pk)

        if ars.exists():
            raise ValidationError("Cannot create this object because an "
                                  "Address Record with the name %s exists "
                                  "in a different container." % self.fqdn)
        elif sis.exists():
            raise ValidationError("Cannot create this object because a "
                                  "Static Interface with the name %s exists "
                                  "in a different container." % self.fqdn)

    def check_intr_collision(self):
        from cyder.cydhcp.interface.static_intr.models import StaticInterface
        if StaticInterface.objects.filter(
                fqdn=self.fqdn, ip_upper=self.ip_upper,
                ip_lower=self.ip_lower).exists():
            raise ValidationError(
                "A Static Interface with %s and %s already exists" %
                (self.fqdn, self.ip_str)
            )

    def validate_delegation_conditions(self):
        """
        If our domain is delegated then an A record can only have a
        name that is the same as a nameserver in that domain (glue).
        """
        if not (self.domain and self.domain.delegated):
            return
        if self.domain.nameserver_set.filter(server=self.fqdn).exists():
            return
        else:
            # Confusing error messege?
            raise ValidationError(
                "You can only create A records in a delegated domain that "
                "have an NS record pointing to them."
            )

    def check_glue_status(self):
        """
        If this record is a "glue" record for a Nameserver instance,
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
        from cyder.cydns.nameserver.models import Nameserver
        if Nameserver.objects.filter(addr_glue=self).exists():
            raise ValidationError(
                "This record is a glue record for a Nameserver. Change the "
                "Nameserver to edit this record."
            )


class AddressRecord(BaseAddressRecord):
    """
    AddressRecord is the class that generates A and AAAA records

        >>> AddressRecord(label=label, domain=domain_object, ip_str=ip_str,
        ... ip_type=ip_type)

    """
    pretty_type = 'address record'

    id = models.AutoField(primary_key=True)

    template = _("{bind_name:$lhs_just} {ttl:$ttl_just}  "
                 "{rdclass:$rdclass_just} "
                 "{rdtype:$rdtype_just} {ip_str:$rhs_just}")

    class Meta:
        app_label = 'cyder'
        db_table = "address_record"
        unique_together = ("label", "domain", "fqdn", "ip_upper", "ip_lower",
                           "ip_type")

    def details(self):
        """For tables."""
        data = super(AddressRecord, self).details()
        data['data'] = [
            ('Label', 'label', self.label),
            ('Domain', 'domain__name', self.domain),
            ('IP', 'ip_str', str(self.ip_str)),
        ]
        return data

    def cyder_unique_error_message(self, model_class, unique_check):
        if unique_check == ('label', 'domain', 'fqdn', 'ip_upper', 'ip_lower',
                            'ip_type'):
            return (
                'Address record with this label, domain, and IP address '
                'already exists.')
        else:
            return super(AddressRecord, self).unique_error_message(
                model_class, unique_check)

    @transaction_atomic
    def save(self, *args, **kwargs):
        self.full_clean()

        update_range_usage = kwargs.pop('update_range_usage', True)
        old_range = None
        if self.id is not None:
            old_ip = AddressRecord.objects.get(id=self.id).ip_str
            old_range = find_range(old_ip)
        super(AddressRecord, self).save(*args, **kwargs)
        rng = find_range(self.ip_str)
        if rng and update_range_usage:
            rng.save(commit=False)
            if old_range:
                old_range.save(commit=False)

    @transaction_atomic
    def delete(self, *args, **kwargs):
        update_range_usage = kwargs.pop('update_range_usage', True)
        rng = find_range(self.ip_str)
        super(AddressRecord, self).delete(*args, **kwargs)
        if rng and update_range_usage:
            rng.save(commit=False)
