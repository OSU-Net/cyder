from gettext import gettext as _

from django.db import models
from django.core.exceptions import ValidationError

import cydns
from cyder.cydns.cname.models import CNAME
from cyder.cydns.ip.models import Ip
from cyder.cydns.models import CydnsRecord, LabelDomainMixin
from cyder.base.constants import IP_TYPE_6, IP_TYPE_4


class BaseAddressRecord(Ip, LabelDomainMixin, CydnsRecord):
    """
    AddressRecord is the class that generates A and AAAA records

        >>> AddressRecord(label=label, domain=domain_object, ip_str=ip_str,
        ... ip_type=ip_type)

    """
    search_fields = ("fqdn", "ip_str")

    class Meta:
        abstract = True

    def __str__(self):
        return '{0} {1} {2}'.format(self.fqdn,
                                    self.rdtype, str(self.ip_str))

    def __repr__(self):
        return "<Address Record '{0}'>".format(str(self))

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
        self.clean_ip()
        ignore_intr = kwargs.pop("ignore_intr", False)
        validate_glue = kwargs.pop("validate_glue", True)

        super(BaseAddressRecord, self).clean(*args, **kwargs)

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
                    "Cannot delete the record {0}. It is a glue "
                    "record.".format(self.record_type()))
        if kwargs.pop('check_cname', True):
            if CNAME.objects.filter(target=self.fqdn):
                raise ValidationError(
                    "A CNAME points to this {0} record. Change the CNAME "
                    "before deleting this record.".format(self.record_type()))

        super(BaseAddressRecord, self).delete(*args, **kwargs)

    def check_intr_collision(self):
        from cyder.cydhcp.interface.static_intr.models import StaticInterface
        if StaticInterface.objects.filter(
                fqdn=self.fqdn, ip_upper=self.ip_upper,
                ip_lower=self.ip_lower).exists():
            raise ValidationError(
                "A Static Interface has already reserved this A record."
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
        Nameserver = cydns.nameserver.models.Nameserver
        if Nameserver.objects.filter(addr_glue=self).exists():
            raise ValidationError(
                "This record is a glue record for a Nameserver. Change the "
                "Nameserver to edit this record."
            )

    def record_type(self):
        if self.ip_type == IP_TYPE_4:
            return 'A'
        else:
            return 'AAAA'


class AddressRecord(BaseAddressRecord):
    """
    AddressRecord is the class that generates A and AAAA records

        >>> AddressRecord(label=label, domain=domain_object, ip_str=ip_str,
        ... ip_type=ip_type)

    """
    id = models.AutoField(primary_key=True)

    template = _("{bind_name:$lhs_just} {ttl:$ttl_just}  "
                 "{rdclass:$rdclass_just} "
                 "{rdtype:$rdtype_just} {ip_str:$rhs_just}")

    class Meta:
        db_table = "address_record"
        unique_together = ("label", "domain", "fqdn", "ip_upper", "ip_lower",
                           "ip_type")

    def details(self):
        """For tables."""
        data = super(AddressRecord, self).details()
        data['data'] = [
            ('Label', 'label', self.label),
            ('Domain', 'domain__name', self.domain),
            ('Record Type', 'obj_type', self.rdtype),
            ('IP', 'ip_str', str(self.ip_str)),
        ]
        return data
