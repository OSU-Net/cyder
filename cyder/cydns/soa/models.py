import time
from gettext import gettext as _
from string import Template

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models

from cyder.base.mixins import ObjectUrlMixin, DisplayMixin
from cyder.cydhcp.keyvalue.models import KeyValue
from cyder.cydhcp.keyvalue.utils import AuxAttr
from cyder.cydns.validation import (validate_fqdn, validate_ttl,
                                    validate_minimum)
from cyder.core.task.models import Task

# import reversion


#TODO, put these defaults in a config file.
ONE_WEEK = 604800
DEFAULT_EXPIRE = ONE_WEEK * 2
DEFAULT_RETRY = ONE_WEEK / 7  # One day
DEFAULT_REFRESH = 180  # 3 min
DEFAULT_MINIMUM = 180  # 3 min


class SOA(models.Model, ObjectUrlMixin, DisplayMixin):
    """
    SOA stands for Start of Authority

        "An SOA record is required in each *db.DOMAIN* and *db.ADDR* file."

        -- O'Reilly DNS and BIND

    The structure of an SOA::

        <name>  [<ttl>]  [<class>]  SOA  <origin>  <person>  (
                           <serial>
                           <refresh>
                           <retry>
                           <expire>
                           <minimum> )


        >>> SOA(primary=primary, contact=contact, retry=retry,
        ... refresh=refresh, description=description)

    Each DNS zone must have it's own SOA object. Use the description field to
    remind yourself which zone an SOA corresponds to if different SOA's have a
    similar ``primary`` and ``contact`` value.
    """

    id = models.AutoField(primary_key=True)
    ttl = models.PositiveIntegerField(default=3600, blank=True, null=True,
                                      validators=[validate_ttl],
                                      help_text="Time to Live of this record")
    primary = models.CharField(max_length=100, validators=[validate_fqdn])
    contact = models.CharField(max_length=100, validators=[validate_fqdn])
    serial = models.PositiveIntegerField(null=False, default=int(time.time()))
    # Indicates when the zone data is no longer authoritative. Used by slave.
    expire = models.PositiveIntegerField(null=False, default=DEFAULT_EXPIRE)
    # The time between retries if a slave fails to contact the master
    # when refresh (below) has expired.
    retry = models.PositiveIntegerField(null=False, default=DEFAULT_RETRY)
    # The time when the slave will try to refresh the zone from the master
    refresh = models.PositiveIntegerField(null=False, default=DEFAULT_REFRESH)
    minimum = models.PositiveIntegerField(null=False, default=DEFAULT_MINIMUM,
                                          validators=[validate_minimum])
    description = models.CharField(max_length=200, blank=True)
    root_domain = models.ForeignKey("domain.Domain", null=False, unique=True,
                                    related_name="root_soa")
    # This indicates if this SOA's zone needs to be rebuilt
    dirty = models.BooleanField(default=False)
    is_signed = models.BooleanField(default=False)
    dns_enabled = models.BooleanField(default=True)

    search_fields = ('primary', 'contact', 'description', 'root_domain__name')
    display_fields = ('root_domain__name',)
    template = _("{root_domain}. {ttl} {rdclass:$rdclass_just} "
                 "{rdtype:$rdtype_just}" "{primary}. {contact}. ({serial} "
                 "{refresh} {retry} {expire})")

    attrs = None

    class Meta:
        db_table = 'soa'
        # We are using the description field here to stop the same SOA from
        # being assigned to multiple zones. See the documentation in the
        # Domain models.py file for more info.

    def bind_render_record(self):
        template = Template(self.template).substitute(**self.justs)
        return template.format(root_domain=self.root_domain,
                               rdtype=self.rdtype, rdclass='IN',
                               **self.__dict__)

    def update_attrs(self):
        self.attrs = AuxAttr(SOAKeyValue, self, 'soa')

    attrs = None

    def __str__(self):
        return self.root_domain.name

    def __repr__(self):
        return "<'{0}'>".format(str(self))

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        objects = objects or SOA.objects
        domains = ctnr.domains.values_list('soa')
        return objects.filter(id__in=domains)

    @property
    def rdtype(self):
        return 'SOA'

    def details(self):
        """For tables."""
        data = super(SOA, self).details()
        data['data'] = [
            ('Root Domain', 'root_domain__name', self.root_domain),
            ('Primary', 'primary', self.primary),
            ('Contact', 'contact', self.contact),
            ('Serial', 'serial', self.serial),
            ('Enabled', 'dns_enabled', self.dns_enabled),
        ]
        return data

    @staticmethod
    def eg_metadata():
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'description', 'datatype': 'string', 'editable': True},
            {'name': 'primary', 'datatype': 'string', 'editable': True},
            {'name': 'contact', 'datatype': 'string', 'editable': True},
            {'name': 'serial', 'datatype': 'integer', 'editable': True},
            {'name': 'expire', 'datatype': 'integer', 'editable': True},
            {'name': 'retry', 'datatype': 'integer', 'editable': True},
            {'name': 'refresh', 'datatype': 'integer', 'editable': True},
        ]}

    def get_debug_build_url(self):
        return reverse('build-debug', args=[self.pk])

    def delete(self, *args, **kwargs):
        if self.domain_set.exists():
            raise ValidationError(
                "Domains exist in this SOA's zone. Delete "
                "those domains or remove them from this zone before "
                "deleting this SOA.")
        super(SOA, self).delete(*args, **kwargs)

    def has_record_set(self, view=None, exclude_ns=False):
        for domain in self.domain_set.all():
            if domain.has_record_set(view=view, exclude_ns=exclude_ns):
                return True
        return False

    def schedule_rebuild(self, commit=True):
        Task.schedule_zone_rebuild(self)
        self.dirty = True
        if commit:
            self.save()

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.pk:
            new = True
            self.dirty = True
        elif self.dirty:
            new = False
        else:
            new = False
            db_self = SOA.objects.get(pk=self.pk)
            fields = [
                'primary', 'contact', 'expire', 'retry', 'refresh',
                'description'
            ]
            # Leave out serial and dirty so rebuilds don't cause a never ending
            # build cycle
            for field in fields:
                if getattr(db_self, field) != getattr(self, field):
                    self.schedule_rebuild(commit=False)

        super(SOA, self).save(*args, **kwargs)

        if new:
            # Need to call this after save because new objects won't have a pk
            self.schedule_rebuild(commit=False)


class SOAKeyValue(KeyValue):
    soa = models.ForeignKey(SOA, related_name='keyvalue_set', null=False)

    class Meta:
        db_table = 'soa_kv'


    def _aa_disabled(self):
        """
        Disabled - The Value of this Key determines whether or not an SOA will
        be asked to build a zone file. Values that represent true are 'True,
        TRUE, true, 1' and 'yes'. Values that represent false are 'False,
        FALSE, false, 0' and 'no'.
        """
        true_values = ["true", "1", "yes"]
        false_values = ["false", "0", "no"]
        if self.value.lower() in true_values:
            self.value = "True"
        elif self.value.lower() in false_values:
            self.value = "False"
        else:
            raise ValidationError(
                "Disabled should be set to either {0} OR {1}".format(
                    ", ".join(true_values), ", ".join(false_values)
                )
            )
