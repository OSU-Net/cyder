from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist

import cydns
from cyder.cydns.domain.models import Domain, _name_to_domain
from cyder.cydns.models import CydnsRecord
from cyder.cydns.validation import validate_name, find_root_domain
from cyder.cydns.search_utils import smart_fqdn_exists


class CNAME(CydnsRecord):
    """CNAMES can't point to an any other records. Said another way,
    CNAMES can't be at the samle level as any other record. This means
    that when you are creating a CNAME every other record type must be
    checked to make sure that the name about to be taken by the CNAME
    isn't taken by another record. Likewise, all other records must
    check that no CNAME exists with the same name before being created.

    >>> CNAME(label = label, domain = domain, target = target)

    """
    # TODO cite an RFC for that ^ (it's around somewhere)
    id = models.AutoField(primary_key=True)
    target = models.CharField(max_length=100, validators=[validate_name],
                              help_text="CNAME Target")
    target_domain = models.ForeignKey(Domain, null=True,
                                      related_name='target_domains', blank=True,
                                      on_delete=models.SET_NULL)

    search_fields = ('fqdn', 'target')

    class Meta:
        db_table = 'cname'
        unique_together = ('domain', 'label', 'target')

    def __str__(self):
        return "{0} CNAME {1}".format(self.fqdn, self.target)

    def details(self):
        return  (
        )

    def details(self):
        """For tables."""
        data = super(CNAME, self).details()
        data['data'] = [
            ('Domain', self.target_domain),
            ('Target', self.target),
        ]
        return data

    def eg_metadata(self):
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'fqdn', 'datatype': 'string', 'editable': True},
            {'name': 'target', 'datatype': 'string', 'editable': True},
        ]}

    @classmethod
    def get_api_fields(cls):
        return super(CNAME, cls).get_api_fields() + ['target']

    def save(self, *args, **kwargs):
        # If label, and domain have not changed, don't mark our domain for
        # rebuilding.
        if self.pk:  # We need to exist in the db first.
            db_self = CNAME.objects.get(pk=self.pk)
            if db_self.label == self.label and db_self.domain == self.domain:
                kwargs['no_build'] = True
                 # Either nothing has changed or just target_domain. We want
                 # rebuild.
        super(CNAME, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        super(CNAME, self).clean(*args, **kwargs)
        super(CNAME, self).check_for_delegation()
        self.check_SOA_condition()
        self.target_domain = _name_to_domain(self.target)
        self.existing_node_check()

    def check_SOA_condition(self):
        """We need to check if the domain is the root domain in a zone.
        If the domain is the root domain, it will have an soa, but the
        master domain will have no soa (or it will have a a different
        soa).
        """
        try:
            self.domain
        except ObjectDoesNotExist:
            return  # Validation will fail eventually
        root_domain = find_root_domain(self.domain.soa)
        if root_domain is None:
            return
        if self.fqdn == root_domain.name:
            raise ValidationError("You cannot create a CNAME that points to "
                                  "the root of a zone.")
        return

    def existing_node_check(self):
        """Make sure no other nodes exist at the level of this CNAME.

            "If a CNAME RR is present at a node, no other data should be
            present; this ensures that the data for
            a canonical name and its aliases cannot be different."

            -- `RFC 1034 <http://tools.ietf.org/html/rfc1034>`_

        For example, this would be bad::

            FOO.BAR.COM     CNAME       BEE.BAR.COM

            BEE.BAR.COM     A           128.193.1.1

            FOO.BAR.COM     TXT         "v=spf1 include:foo.com -all"

        If you queried the ``FOO.BAR.COM`` name, the class of the record
        that would be returned would be ambiguous.



        .. note::
            The following records classes are checked.
                * :class:`AddressRecord` (A and AAAA)
                * :class:`SRV`
                * :class:`TXT`
                * :class:`MX`
        """
        qset = smart_fqdn_exists(self.fqdn, cn=False)
        if qset:
            objects = qset.all()
            raise ValidationError("Objects with this name already exist: {0}".
                                  format(objects))
        MX = cydns.mx.models.MX
        if MX.objects.filter(server=self.fqdn):
            raise ValidationError("RFC 2181 says you shouldn't point MX "
                                  "records at CNAMEs")
