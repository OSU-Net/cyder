from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import m2m_changed

import cydns
from cyder.cydns.domain.models import Domain, _check_TLD_condition
from cyder.cydns.view.models import View
from cyder.base.mixins import ObjectUrlMixin
from cyder.cydns.validation import validate_first_label, validate_name
from cyder.cydns.validation import validate_ttl, is_rfc1918, is_rfc4193
from django.conf import settings

import pdb


@receiver(m2m_changed)
def views_handler(sender, **kwargs):
    """ This function catches any changes to a manymany relationship and just nukes
    the relationship to the "private" view if one exists.

    One awesome side affect of this hack is there is NO way for this function
    to relay that there was an error to the user. If we want to tell the user
    that we nuked the record's relationship to the public view we will need to
    do that in a form.
    """
    if kwargs["action"] != "post_add":
        return
    instance = kwargs.pop("instance", None)
    if (not instance or not hasattr(instance, "ip_str") or
            not hasattr(instance, "ip_type")):
        return
    model = kwargs.pop("model", None)
    if not View == model:
        return
    if instance.views.filter(name="public").exists():
        if instance.ip_type == '4' and is_rfc1918(instance.ip_str):
            instance.views.remove(View.objects.get(name="public"))
        elif instance.ip_type == '6' and is_rfc4193(instance.ip_str):
            instance.views.remove(View.objects.get(name="public"))


class CydnsRecord(models.Model, ObjectUrlMixin):
    """
    This class provides common functionality that many DNS record
    classes share.  This includes a foreign key to the ``domain`` table
    and a ``label`` CharField.  This class also inherits from the
    ``ObjectUrlMixin`` class to provide the ``get_absolute_url``,
    ``get_update_url``, and ``get_delete_url`` functions.

    This class does validation on the ``label`` field. Call
    ``clean_all`` to trigger the validation functions. Failure to
    validate will raise a ``ValidationError``.

    If you plan on using the ``unique_together`` constraint on a Model
    that inherits from ``CydnsRecord``, you must include ``domain`` and
    ``label`` explicitly if you need them to.  ``CydnsRecord`` will not
    enforce uniqueness for you.

    All common records have a ``fqdn`` field. This field is updated
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

    domain = models.ForeignKey(Domain, null=False, help_text="FQDN of the "
                               "domain after the short hostname. "
                               "(Ex: <i>Vlan</i>.<i>DC</i>.mozilla.com)")
    # "The length of any one label is limited to between 1 and 63 octets."
    # RFC218
    label = models.CharField(max_length=63, blank=True, null=True,
                             validators=[validate_first_label],
                             help_text="Short name of the fqdn")
    fqdn = models.CharField(max_length=255, blank=True, null=True,
                            validators=[validate_name], db_index=True)
    ttl = models.PositiveIntegerField(default=3600, blank=True, null=True,
                                      validators=[validate_ttl],
                                      help_text="Time to Live of this record")
    views = models.ManyToManyField(View, blank=True)
    comment = models.CharField(max_length=1000, blank=True, null=True,
                               help_text="Comments about this record.")
    # fqdn = label + domain.name <--- see set_fqdn

    class Meta:
        abstract = True

    @classmethod
    def get_api_fields(cls):
        """The purpose of this is to help the API decide which fields to expose
        to the user when they are creating and updateing an Object. This
        function should be implemented in inheriting models and overriden to
        provide additional fields. Tastypie ignores any relational fields on
        the model. See the ModelResource definitions for view and domain
        fields.
        """
        return ['label', 'ttl', 'comment']

    def clean(self):
        set_fqdn(self)
        check_TLD_condition(self)

    def delete(self, *args, **kwargs):
        from cyder.cydns.utils import prune_tree
        objs_domain = self.domain
        super(CydnsRecord, self).delete(*args, **kwargs)
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
        if no_build:
            pass
        else:
            # Mark the soa
            if self.domain.soa:
                self.domain.soa.dirty = True
                self.domain.soa.save()
        if db_domain:
            from cyder.cydns.utils import prune_tree
            prune_tree(db_domain)

    def set_fqdn(self):
        set_fqdn(self)

    def check_for_cname(self):
        check_for_cname(self)

    def check_for_delegation(self):
        check_for_delegation(self)

    def check_TLD_condition(self):
        _check_TLD_condition(self)


#####
def set_fqdn(record):
    try:
        if record.label == '':
            record.fqdn = record.domain.name
        else:
            record.fqdn = "{0}.{1}".format(record.label, record.domain.name)
    except ObjectDoesNotExist:
        return


def check_for_cname(record):
    """"
    If a CNAME RR is present at a node, no other data should be
    present; this ensures that the data for a canonical name and its
    aliases cannot be different."

    -- `RFC 1034 <http://tools.ietf.org/html/rfc1034>`_

    Call this function in models that can't overlap with an existing
    CNAME.
    """
    CNAME = cydns.cname.models.CNAME
    if hasattr(record, 'label'):
        if CNAME.objects.filter(domain=record.domain,
                                label=record.label).exists():
            raise ValidationError("A CNAME with this name already exists.")
    else:
        if CNAME.objects.filter(label='', domain=record.domain).exists():
            raise ValidationError("A CNAME with this name already exists.")


def check_for_delegation(record):
    """
    If an object's domain is delegated it should not be able to
    be changed.  Delegated domains cannot have objects created in
    them.
    """
    try:
        if not record.domain.delegated:
            return
    except ObjectDoesNotExist:
        return
    if not record.pk:  # We don't exist yet.
        raise ValidationError("No objects can be created in the {0}"
                              "domain. It is delegated."
                              .format(record.domain.name))


def check_TLD_condition(record):
    _check_TLD_condition(record)
