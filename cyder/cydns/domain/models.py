from django.db import models
from django.core.exceptions import ValidationError

from cyder.base.mixins import ObjectUrlMixin
from cyder.base.models import BaseModel
from cyder.base.utils import transaction_atomic
from cyder.cydns.validation import validate_domain_name
from cyder.cydns.search_utils import smart_fqdn_exists
from cyder.cydns.ip.utils import ip_to_reverse_name
from cyder.cydns.validation import validate_reverse_name
from cyder.cydns.domain.utils import name_to_domain, is_name_descendant_of


class Domain(BaseModel, ObjectUrlMixin):
    """A Domain is used as a foreign key for most DNS records.

    All domains in a zone share the zone's SOA.

    If two domains are part of different zones, they (and their
    subdomains) will need different SOA objects even if the data contained
    in the SOA is exactly the same.

    For example: Say we are authoritative for the domains (and zones)
    ``foo.com`` and ``baz.com``.  These zones should have different
    SOA's because they are part of two separate zones. If you had the
    subdomain ``baz.foo.com``, it could have the same SOA as the
    ``foo.com`` domain because it is in the same zone.

    Both 'forward' domains under TLD's like 'com', 'edu', and 'org' and
    'reverse' domains under the TLD's 'in-addr.arpa' and 'ip6.arpa' are stored
    in this table. At first glance it would seem like the two types of domains
    have disjoint data sets; record types that have a Foreign Key back to a
    'reverse' domain would never need to have a Foreign Key back to a 'forward'
    domain. This is not the case. The two main examples are NS and CNAME
    records. If there were two different domain tables, NS/CNAME records would
    need to a) have two different Foriegn Keys, or b) have seperate tables.

    Constraints on both 'forward' and 'reverse' Domains:

        *   A ``ValidationError`` is raised when you try to delete a
            domain that has child domains. A domain should only be deleted when
            it has no child domains.

        *   All domains should have a master (or parent) domain.  A
            ``ValidationError`` will be raised if you try to create an orphan
            domain that should have a master domain.

        *   The ``name`` field must be unique. Failing to make it unique will
            raise a ``ValidationError``.

    Constraints on 'reverse' Domains:

        *   A 'reverse' domain should have ``is_reverse`` set to True.

        *   A 'reverse' domain's name should end in either 'in-addr.arpa' or
            'ip6.arpa'

        *   When a PTR is added it is pointed back to a 'reverse' domain. This
            is done by converting the IP address to the connonical DNS form and
            then doing a longest prefix match against all domains that have
            is_reverse set to True.

    This last point is worth looking at further. When adding a new reverse
    domain, all records in the PTR table should be checked for a more
    appropriate domain. Also, when a domain is deleted, all PTR objects should
    be passed down to the parent domain.


    .. warning::

        Deleting a domain will delete all records associated to that domain.

    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True,
                            validators=[validate_domain_name])
    master_domain = models.ForeignKey("self", null=True,
                                      default=None, blank=True)
    soa = models.ForeignKey("cyder.SOA", null=True, default=None,
                            blank=True, verbose_name='SOA',
                            on_delete=models.SET_NULL)
    is_reverse = models.BooleanField(default=False)
    # This indicates if this domain (and zone) needs to be rebuilt
    dirty = models.BooleanField(default=False)
    # Read about the label and domain paradigm
    purgeable = models.BooleanField(default=False)
    delegated = models.BooleanField(default=False, null=False, blank=True)

    search_fields = ('name',)
    sort_fields = ('name',)

    class Meta:
        app_label = 'cyder'
        db_table = 'domain'

    def __unicode__(self):
        return self.name

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        if objects:
            return ctnr.domains.filter(pk__in=objects)
        else:
            return ctnr.domains.all()

    @property
    def rdtype(self):
        return 'DOMAIN'

    def details(self):
        """For tables."""
        data = super(Domain, self).details()
        data['data'] = [
            ('Name', 'name', self),
            ('SOA', 'soa__root_domain__name', self.soa),
            ('Master Domain', 'master_domain__name', self.master_domain),
            ('Delegated', 'delegated', self.delegated),
        ]
        return data

    @staticmethod
    def eg_metadata():
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'name', 'datatype': 'string', 'editable': True},
            {'name': 'master_domain', 'datatype': 'string', 'editable': False},
            {'name': 'soa', 'datatype': 'string', 'editable': False},
            {'name': 'delegated', 'datatype': 'boolean', 'editable': True},
        ]}

    @classmethod
    @transaction_atomic
    def create_recursive(cls, name, commit=True):
        first_dot = name.find('.')
        if first_dot >= 0:  # not a TLD
            rest = name[(first_dot + 1):]
            cls.create_recursive(name=rest)
        domain, created = cls.objects.get_or_create(name=name)
        return domain

    @transaction_atomic
    def delete(self, *args, **kwargs):
        self.check_for_children()
        if self.has_record_set():
            raise ValidationError("There are records associated with this "
                                  "domain. Delete them before deleting this "
                                  "domain.")

        super(Domain, self).delete(*args, **kwargs)

    @transaction_atomic
    def save(self, *args, **kwargs):
        self.full_clean()

        super(Domain, self).save(*args, **kwargs)

        # Ensure all descendants in this zone have the same SOA as this domain.
        bad_children = self.domain_set.filter(
            root_of_soa=None).exclude(soa=self.soa)
        for child in bad_children:
            child.soa = self.soa
            child.save(commit=False)  # Recurse.

    @property
    def ip_type(self):
        if self.name.endswith('in-addr.arpa'):
            return '4'
        elif self.name.endswith('ip6.arpa'):
            return '6'
        else:
            return None

    def set_soa(self):
        from cyder.cydns.soa.models import SOA

        try:  # Assume domain is a root domain.
            self.soa = self.root_of_soa.get()
        except SOA.DoesNotExist:  # Domain is not a root domain.
            if self.master_domain:
                self.soa = self.master_domain.soa
            else:
                self.soa = None

    def clean(self, *args, **kwargs):
        super(Domain, self).clean(*args, **kwargs)

        is_new = self.pk is None

        if self.name.endswith('arpa'):
            self.is_reverse = True
        self.master_domain = name_to_master_domain(self.name)

        if self.master_domain and self.master_domain.delegated:
            raise ValidationError(
                '{} is delegated, so it cannot have subdomains.'.format(
                    self.master_domain.name))

        self.set_soa()

        if self.delegated and not self.soa:
            raise ValidationError(
                '{} is delegated, so it must be in a zone.'.format(self.name))

        # If the domain is new, its pk is None, so self.domain_set will contain
        # the top-level domains rather than an empty queryset.
        if not is_new and self.domain_set.filter(soa=self.soa).exclude(
                root_of_soa=None).exists():
            raise ValidationError("The root of this domain's zone is below "
                                  "it.")

        if is_new:
            # The object doesn't exist in the db yet. Make sure we don't
            # conflict with existing objects. We may want to move to a more
            # automatic solution where the creation of a new domain will
            # automatically move objects around (see the ensure_domain
            # function).
            qset = smart_fqdn_exists(self.name)
            if qset:
                objects = qset.all()
                raise ValidationError("Objects with this name already "
                                      "exist: {0}".format(
                    ', '.join(unicode(object) for object in objects))
                )
        else:
            db_self = Domain.objects.get(pk=self.pk)

            if db_self.name != self.name and self.domain_set.exists():
                raise ValidationError("Child domains rely on this domain's "
                                      "name remaining the same.")

            # Raise an exception...
            # If our soa is different AND it's non-null AND we have records in
            # this domain AND the new soa has a record domain with no
            # nameservers.
            if db_self.soa != self.soa and self.soa and self.has_record_set():
                if not self.soa.root_domain.nameserver_set.exists():
                    raise ValidationError("By changing this domain's SOA you "
                                          "are attempting to create a zone "
                                          "whose root domain has no NS "
                                          "record.")

    def check_for_children(self):
        if self.domain_set.exists():
            raise ValidationError("Before deleting this domain, please "
                                  "remove its children.")

    def get_children_recursive(self):
        children = set(self.domain_set.all())
        for child in list(children):
            children |= child.get_children_recursive()

        return children

    def has_record_set(self, view=None, exclude_ns=False):
        object_sets = [
            self.addressrecord_set,
            self.cname_set,
            self.mx_set,
            self.srv_set,
            self.sshfp_set,
            self.staticinterface_set,
            self.txt_set,
            self.reverse_ptr_set
        ]
        if not view:
            for object_set in object_sets:
                if object_set.exists():
                    return True
            if not exclude_ns and self.nameserver_set.exists():
                return True
        else:
            for object_set in object_sets:
                if object_set.filter(views=view).exists():
                    return True
            if (not exclude_ns and
                    self.nameserver_set.filter(views=view).exists()):
                return True

    @property
    def is_root_domain(self):
        return self.root_of_soa.exists()

    @property
    def zone_root_domain(self):
        if self.soa:
            return self.soa.root_domain
        else:
            return None

    def is_descendant_of(self, other):
        return is_name_descendant_of(self.name, other.name)


# A handy function that would cause circular dependencies if it were in
# another file.
def name_to_master_domain(name):
    """Given an domain name, this function returns the appropriate
    master domain.

    :param name: The domain for which we are using to search for a
        master domain.
    :type name: str
    :returns: domain -- Domain object
    :raises: ValidationError
    """
    tokens = name.split('.')
    master_domain = None
    for i in reversed(xrange(len(tokens) - 1)):
        parent_name = '.'.join(tokens[i + 1:])
        possible_master_domain = Domain.objects.filter(name=parent_name)
        if not possible_master_domain:
            raise ValidationError("Master Domain for domain {0} not "
                                  "found.".format(name))
        else:
            master_domain = possible_master_domain[0]
    return master_domain
