from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import get_model

from cyder.base.models import BaseModel
from cyder.cydns.domain.models import Domain
from cyder.base.mixins import ObjectUrlMixin, DisplayMixin
from cyder.cydns.view.models import View
from cyder.cydns.validation import validate_first_label, validate_fqdn
from cyder.cydns.validation import validate_ttl
from cyder.cydns.view.validation import check_no_ns_soa_condition


class LabelDomainUtilsMixin(models.Model):
    """
    This class provides common functionality that many DNS record
    classes share.

    If you plan on using the ``unique_together`` constraint on a Model
    that inherits from ``LabelDomainUtilsMixin`` or ``LabelDomainMixin``, you
    must include ``domain`` and ``label`` explicitly if you need them to.

    All common records have an ``fqdn`` field. This field is updated
    every time the object is saved::

        fqdn = name + domain.name

        or if name == ''

        fqdn = domain.name

    This field makes searching for records much easier. Instead of
    looking at ``obj.label`` together with ``obj.domain.name``, you can
    just search the ``obj.fqdn`` field.

    "the total number of octets that represent a name (i.e., the sum of
    all label octets and label lengths) is limited to 255" - RFC 4471
    """
    @property
    def pretty_name(self):
        return self.fqdn

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(LabelDomainUtilsMixin, self).__init__(*args, **kwargs)
        if self.fqdn:
            self.label_domain_from_fqdn()

    def label_domain_from_fqdn(self):
        try:
            self.domain = Domain.objects.get(name=self.fqdn)
            self.label = ''
        except Domain.DoesNotExist:
            parts = self.fqdn.split('.', 1)
            if len(parts) == 2:
                self.label = parts[0]
                self.domain = Domain.objects.get(name=parts[1])
            else:
                self.label = ''
                self.domain = Domain.objects.get(name=parts[0])

    def clean(self, *args, **kwargs):
        try:
            self.domain
        except Domain.DoesNotExist:
            # clean_fields has already seen `domain`'s own ValidationError.
            raise ValidationError('')
        self.set_fqdn()
        super(LabelDomainUtilsMixin, self).clean(*args, **kwargs)

    def set_fqdn(self):
        if self.label:
            self.fqdn = self.label + '.' + self.domain.name
        else:
            self.fqdn = self.domain.name


class LabelDomainMixin(LabelDomainUtilsMixin):
    class Meta:
        abstract = True

    domain = models.ForeignKey(Domain, null=False)
    # "The length of any one label is limited to between 1 and 63 octets."
    # -- RFC218
    label = models.CharField(
        max_length=63, blank=True, validators=[validate_first_label],
        help_text="Short name of the FQDN",
    )
    fqdn = models.CharField(
        max_length=255, blank=True, validators=[validate_fqdn], db_index=True
    )


class ViewMixin(models.Model):

    def validate_views(instance, views):
        instance.clean_views(views)

    views = models.ManyToManyField(
        View, blank=True, validators=[validate_views]
    )

    class Meta:
        abstract = True

    def clean_views(self, views):
        """cleaned_data is the data that is going to be called with for
        updating an existing or creating a new object. Classes should implement
        this function according to their specific needs.
        """
        for view in views:
            if hasattr(self, 'domain'):
                check_no_ns_soa_condition(self.domain, view=view)
            if hasattr(self, 'reverse_domain'):
                check_no_ns_soa_condition(self.reverse_domain, view=view)


class CydnsRecord(BaseModel, ViewMixin, DisplayMixin, ObjectUrlMixin):
    ttl = models.PositiveIntegerField(default=3600, blank=True, null=True,
                                      validators=[validate_ttl],
                                      verbose_name="Time to live")
    description = models.CharField(max_length=1000, blank=True)
    ctnr = models.ForeignKey("cyder.Ctnr", null=False,
                             verbose_name="Container")

    class Meta:
        abstract = True

    def __str__(self):
        self.label_domain_from_fqdn()
        return self.bind_render_record()

    def __repr__(self):
        return "<{0} '{1}'>".format(self.rdtype, str(self))

    @classmethod
    def filter_by_ctnr(cls, ctnr, objects=None):
        objects = objects or cls.objects
        if ctnr.name == "global":
            return objects

        objects = objects.filter(ctnr=ctnr)
        return objects

    def check_in_ctnr(self, ctnr):
        if hasattr(self, "domain"):
            return self.domain in ctnr.domains.all()

    @classmethod
    def get_api_fields(cls):
        """
        The purpose of this is to help the API decide which fields to expose
        to the user when they are creating and updating an Object. This
        function should be implemented in inheriting models and overriden to
        provide additional fields. Tastypie ignores any relational fields on
        the model. See the ModelResource definitions for view and domain
        fields.
        """
        return ['fqdn', 'ttl', 'description', 'views']

    def clean(self, *args, **kwargs):
        super(CydnsRecord, self).clean(*args, **kwargs)

        self.check_TLD_condition()
        check_no_ns_soa_condition(self.domain)
        self.check_domain_ctnr()
        self.check_for_delegation()
        if self.rdtype != 'CNAME':
            self.check_for_cname()

    def delete(self, *args, **kwargs):
        self.schedule_zone_rebuild()

        from cyder.cydns.utils import prune_tree
        call_prune_tree = kwargs.pop('call_prune_tree', True)
        objs_domain = self.domain

        super(CydnsRecord, self).delete(*args, **kwargs)

        if call_prune_tree:
            prune_tree(objs_domain)

    def save(self, *args, **kwargs):
        if self.pk:
            # We need to get the domain from the db. If it's not our current
            # domain, call prune_tree on the domain in the db later.
            db_domain = self.__class__.objects.get(pk=self.pk).domain
            if self.domain == db_domain:
                db_domain = None
        else:
            db_domain = None

        no_build = kwargs.pop("no_build", False)
        super(CydnsRecord, self).save(*args, **kwargs)

        if not no_build:
            self.schedule_zone_rebuild()

        if db_domain:
            from cyder.cydns.utils import prune_tree
            prune_tree(db_domain)

    def schedule_zone_rebuild(self):
        if self.domain.soa:
            self.domain.soa.schedule_rebuild()

    def check_domain_ctnr(self):
        """
        Validate name uses domain allowed in record's container.
        """
        if hasattr(self, 'ctnr') and hasattr(self, 'domain'):
            if not self.domain.ctnr_set.filter(pk=self.ctnr.pk).exists():
                raise ValidationError("Cannot create this record because its "
                                      "ctnr does not match its domain.")

    def check_for_cname(self):
        """
        "If a CNAME RR is preent at a node, no other data should be
        present; this ensures that the data for a canonical name and its
        aliases cannot be different."

        -- `RFC 1034 <http://tools.ietf.org/html/rfc1034>`_

        Call this function in models that can't overlap with an existing
        CNAME.
        """
        from cyder.cydns.cname.models import CNAME
        if hasattr(self, 'label'):
            if CNAME.objects.filter(domain=self.domain,
                                    label=self.label).exists():
                raise ValidationError("A CNAME with this name already exists.")
        else:
            if CNAME.objects.filter(label='', domain=self.domain).exists():
                raise ValidationError("A CNAME with this name already exists.")

    def check_for_delegation(self):
        """
        If an object's domain is delegated it should not be able to
        be changed.  Delegated domains cannot have objects created in
        them.
        """
        if not (self.domain and self.domain.delegated):
            return
        if self.domain.nameserver_set.filter(server=self.fqdn).exists():
            return
        else:
            # Confusing error message?
            raise ValidationError(
                "You can only create a record in a delegated domain that has "
                "an NS record pointing at it."
            )

    def check_TLD_condition(self):
        domains = Domain.objects.filter(name=self.fqdn)
        if domains:
            domain = domains[0]
            PTR = get_model('cyder', 'ptr')
            if not domain.master_domain and not isinstance(self, PTR):
                raise ValidationError("You cannot create a record that points "
                                      "to the top level of another domain.")
            elif self.label:
                # blank label allowed
                self.label = ''
                self.domain = domain
