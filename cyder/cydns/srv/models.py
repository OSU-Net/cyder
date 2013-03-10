from gettext import gettext as _

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models

import cydns
from cyder.base.mixins import ObjectUrlMixin
from cyder.cydns.domain.models import Domain
from cyder.cydns.soa.utils import update_soa
from cyder.cydns.validation import (validate_srv_label, validate_srv_port,
                                    validate_srv_priority, validate_srv_weight,
                                    validate_srv_name, validate_ttl,
                                    validate_srv_target)
from cyder.cydns.view.models import View

#import reversion

# Rhetorical Question: Why is SRV not a common record?  SRV records have
# a '_' in their label. Most domain names do not allow this.  Cydns
# record has a validator that would raise an exception when validating
# it's label.  TODO, verify this.


class SRV(models.Model, ObjectUrlMixin):
    """
    >>> SRV(label=label, domain=domain, target=target, port=port,
    ... priority=priority, weight=weight, ttl=ttl)
    """
    id = models.AutoField(primary_key=True)
    label = models.CharField(
        max_length=63, blank=True, null=True, validators=[validate_srv_label],
        help_text='Short name of the FQDN')
    domain = models.ForeignKey(Domain, null=False, help_text="FQDN of the "
                               "domain after the short hostname. "
                               "(Ex: <i>Vlan</i>.<i>DC</i>.mozilla.com)")
    fqdn = models.CharField(max_length=255, blank=True, null=True,
                            validators=[validate_srv_name])
    views = models.ManyToManyField(View, blank=True)

    target = models.CharField(max_length=100,
                              validators=[validate_srv_target])

    port = models.PositiveIntegerField(null=False,
                                       validators=[validate_srv_port])

    priority = models.PositiveIntegerField(null=False,
                                           validators=[validate_srv_priority])

    weight = models.PositiveIntegerField(null=False,
                                         validators=[validate_srv_weight])
    ttl = models.PositiveIntegerField(default=3600, blank=True, null=True,
                                      validators=[validate_ttl],
                                      help_text="Time to Live of this record")
    description = models.CharField(max_length=1000, blank=True, null=True)
    template = _("{bind_name:$lhs_just} {ttl} {rdclass:$rdclass_just} "
                 "{rdtype:$rdtype_just} {priority:$prio_just} "
                 "{weight:$extra_just} {port:$extra_just} "
                 "{target:$extra_just}.")

    search_fields = ("fqdn", "target")

    class Meta:
        db_table = "srv"
        unique_together = ("label", "domain", "target", "port")

    def __str__(self):
        return "{0} {1} {2} {3} {4} {5} {6}".format(self.fqdn, "IN", "SRV",
                                                    self.priority, self.weight,
                                                    self.port, self.target)

    def __repr__(self):
        return "<SRV '{0}'>".format(str(self))

    def details(self):
        """For tables."""
        data = super(SRV, self).details()
        data['data'] = [
            ('Domain', 'domain__name', self.domain),
            ('Target', 'target', self.target),
            ('Port', 'port', self.port),
            ('Priority', 'priority', self.priority),
            ('Weight', 'weight', self.weight),
        ]
        return data

    def eg_metadata(self):
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'fqdn', 'datatype': 'string', 'editable': True},
            {'name': 'target', 'datatype': 'string', 'editable': True},
            {'name': 'port', 'datatype': 'integer', 'editable': True},
            {'name': 'priority', 'datatype': 'integer', 'editable': True},
            {'name': 'weight', 'datatype': 'integer', 'editable': True},
        ]}

    @classmethod
    def get_api_fields(cls):
        return ['label', 'fqdn', 'domain', 'views', 'port', 'ttl', 'weight',
                'priority', 'target', 'description']

    @property
    def rdtype(self):
        return 'SRV'

    def delete(self, *args, **kwargs):
        from cyder.cydns.utils import prune_tree
        objs_domain = self.domain
        super(SRV, self).delete(*args, **kwargs)
        prune_tree(objs_domain)

    def save(self, *args, **kwargs):
        self.full_clean()
        update_soa(self)
        if self.pk:
            # We need to get the domain from the db. If it's not our current
            # domain, call prune_tree on the domain in the db later.
            db_domain = self.__class__.objects.get(pk=self.pk).domain
            if self.domain == db_domain:
                db_domain = None
        else:
            db_domain = None
        super(SRV, self).save(*args, **kwargs)
        if db_domain:
            from cyder.cydns.utils import prune_tree
            prune_tree(db_domain)

    def clean(self):
        self.set_fqdn()
        self.check_for_cname()
        self.check_for_delegation()

    def set_fqdn(self):
        try:
            if self.label == "":
                self.fqdn = self.domain.name
            else:
                self.fqdn = "{0}.{1}".format(self.label, self.domain.name)
        except ObjectDoesNotExist:
            return

    def check_for_delegation(self):
        """If an object's domain is delegated it should not be able to
        be changed.  Delegated domains cannot have objects created in
        them.
        """
        if not self.domain.delegated:
            return
        if not self.pk:  # We don't exist yet.
            raise ValidationError("No objects can be created in the {0}"
                                  "domain. It is delegated.".
                                  format(self.domain.name))

    def check_for_cname(self):
        """"If a CNAME RR is preent at a node, no other data should be
        present; this ensures    that the data for a canonical name and
        its aliases cannot be different."

        -- `RFC 1034 <http://tools.ietf.org/html/rfc1034>`_

        Call this function in models that can't overlap with an existing
        CNAME.
        """
        CNAME = cydns.cname.models.CNAME
        if CNAME.objects.filter(fqdn=self.fqdn).exists():
            raise ValidationError("A CNAME with this name already exists.")

#reversion.(SRV)
