import time
from gettext import gettext as _
from string import Template

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q, F
from django.db import models

from cyder.base.eav.constants import ATTRIBUTE_INFORMATIONAL
from cyder.base.eav.models import Attribute, EAVBase
from cyder.base.mixins import ObjectUrlMixin, DisplayMixin
from cyder.base.helpers import get_display
from cyder.cydhcp.keyvalue.models import KeyValue
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
    # This indicates if this SOA's zone needs to be rebuilt
    dirty = models.BooleanField(default=False)
    is_signed = models.BooleanField(default=False)
    search_fields = ('primary', 'contact', 'description')
    display_fields = ('description',)
    template = _("{root_domain}. {ttl} {rdclass:$rdclass_just} "
                 "{rdtype:$rdtype_just}" "{primary}. {contact}. ({serial} "
                 "{refresh} {retry} {expire})")

    attrs = None

    class Meta:
        db_table = 'soa'
        # We are using the description field here to stop the same SOA from
        # being assigned to multiple zones. See the documentation in the
        # Domain models.py file for more info.
        unique_together = ('primary', 'contact', 'description')

    def bind_render_record(self):
        template = Template(self.template).substitute(**self.justs)
        return template.format(root_domain=self.root_domain,
                               rdtype=self.rdtype, rdclass='IN',
                               **self.__dict__)

    def __str__(self):
        return get_display(self)

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

    @property
    def root_domain(self):
        try:
            return self.domain_set.get(~Q(master_domain__soa=F('soa')),
                                       soa__isnull=False)
        except ObjectDoesNotExist:
            return None

    def details(self):
        """For tables."""
        data = super(SOA, self).details()
        data['data'] = [
            ('Description', 'description', self),
            ('Primary', 'primary', self.primary),
            ('Contact', 'contact', self.contact),
            ('Serial', 'serial', self.serial),
            ('Expire', 'expire', self.expire),
            ('Retry', 'retry', self.retry),
            ('Refresh', 'refresh', self.refresh),
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


class SOAAV(EAVBase):
    class Meta:
        db_table = 'soa_av'


    soa = models.ForeignKey(SOA)
    attribute = models.ForeignKey(Attribute,
            limit_choices_to={'attribute_type': ATTRIBUTE_INFORMATIONAL})
