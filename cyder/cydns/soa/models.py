import os
import time
from gettext import gettext as _
from string import Template

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db.models import Q, F
from django.db import models

from cyder.base.mixins import ObjectUrlMixin, DisplayMixin
from cyder.cydhcp.keyvalue.models import KeyValue
from cyder.cydhcp.keyvalue.utils import AuxAttr
from cyder.cydns.validation import validate_name, validate_ttl

#import reversion


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
    primary = models.CharField(max_length=100, validators=[validate_name])
    contact = models.CharField(max_length=100, validators=[validate_name])
    serial = models.PositiveIntegerField(null=False, default=int(time.time()))
    # Indicates when the zone data is no longer authoritative. Used by slave.
    expire = models.PositiveIntegerField(null=False, default=DEFAULT_EXPIRE)
    # The time between retries if a slave fails to contact the master
    # when refresh (below) has expired.
    retry = models.PositiveIntegerField(null=False, default=DEFAULT_RETRY)
    # The time when the slave will try to refresh the zone from the master
    refresh = models.PositiveIntegerField(null=False, default=DEFAULT_REFRESH)
    minimum = models.PositiveIntegerField(null=False, default=DEFAULT_MINIMUM)
    description = models.CharField(max_length=200, null=True, blank=True)
    # This indicates if this SOA's zone needs to be rebuilt
    dirty = models.BooleanField(default=False)
    search_fields = ('primary', 'contact', 'description')
    template = _("{root_domain}. {ttl} {rdclass:$rdclass_just} "
                 "{rdtype:$rdtype_just}" "{primary}. {contact}. ({serial} "
                 "{refresh} {retry} {expire})")

    attrs = None

    def bind_render_record(self):
        template = Template(self.template).substitute(**self.justs)
        return template.format(root_domain=self.root_domain,
                               rdtype=self.rdtype, rdclass='IN',
                               **self.__dict__)

    def update_attrs(self):
        self.attrs = AuxAttr(SOAKeyValue, self, 'soa')

    attrs = None

    class Meta:
        db_table = 'soa'
        # We are using the description field here to stop the same SOA from
        # being assigned to multiple zones. See the documentation in the
        # Domain models.py file for more info.
        unique_together = ('primary', 'contact', 'description')

    def __str__(self):
        return "{0}".format(str(self.description))

    def __repr__(self):
        return "<'{0}'>".format(str(self))

    @property
    def rdtype(self):
        return 'SOA'

    @property
    def root_domain(self):
        try:
            return self.domain_set.get(~Q(master_domain__soa=F('soa')),
                    soa__isnull=False)
        except SOA.DoesNotExist:
            return None

    def details(self):
        """For tables."""
        data = super(SOA, self).details()
        data['data'] = [
            ('Primary', 'primary', self.primary),
            ('Contact', 'contact', self.contact),
            ('Serial', 'serial', self.serial),
            ('Expire', 'expire', self.expire),
            ('Retry', 'retry', self.retry),
            ('Refresh', 'refresh', self.refresh),
            ('Description', 'description', self.description),
        ]
        return data

    def eg_metadata(self):
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'primary', 'datatype': 'string', 'editable': True},
            {'name': 'contact', 'datatype': 'string', 'editable': True},
            {'name': 'serial', 'datatype': 'integer', 'editable': True},
            {'name': 'expire', 'datatype': 'integer', 'editable': True},
            {'name': 'retry', 'datatype': 'integer', 'editable': True},
            {'name': 'refresh', 'datatype': 'integer', 'editable': True},
            {'name': 'description', 'datatype': 'string', 'editable': True},
        ]}

    def get_debug_build_url(self):
        return reverse('build-debug', args=[self.pk])

    def delete(self, *args, **kwargs):
        super(SOA, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        # Look a the value of this object in the db. Did anything change? If
        # yes, mark yourself as 'dirty'.
        self.full_clean()
        if self.pk:
            db_self = SOA.objects.get(pk=self.pk)
            fields = ['primary', 'contact', 'expire', 'retry',
                      'refresh', 'description']
            # Leave out serial for obvious reasons
            for field in fields:
                if getattr(db_self, field) != getattr(self, field):
                    self.dirty = True
        super(SOA, self).save(*args, **kwargs)


#reversion.(SOA)

class SOAKeyValue(KeyValue):
    soa = models.ForeignKey(SOA, null=False)

    def _aa_dir_path(self):
        """Filepath - Where should the build scripts put the zone file for this
        zone?"""
        if not os.access(self.value, os.R_OK):
            raise ValidationError("Couldn't find {0} on the system running "
                                  "this code. Please create this path.".
                                  format(self.value))

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
            raise ValidationError("Disabled should be set to either {0} OR "
                                  "{1}".format(", ".join(true_values),
                                               ", ".join(false_values)))

#reversion.(SOAKeyValue)
