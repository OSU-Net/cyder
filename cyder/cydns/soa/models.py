import time
from gettext import gettext as _
from itertools import chain
from string import Template

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models, transaction

from cyder.base.eav.constants import ATTRIBUTE_INVENTORY
from cyder.base.eav.fields import EAVAttributeField
from cyder.base.eav.models import Attribute, EAVBase
from cyder.base.mixins import ObjectUrlMixin, DisplayMixin
from cyder.base.models import BaseModel
from cyder.base.utils import safe_delete, safe_save
from cyder.cydns.validation import (validate_fqdn, validate_ttl,
                                    validate_minimum)
from cyder.core.task.models import Task
from cyder.settings import MIGRATING

# import reversion


#TODO, put these defaults in a config file.
ONE_WEEK = 604800
DEFAULT_EXPIRE = ONE_WEEK * 2
DEFAULT_RETRY = ONE_WEEK / 7  # One day
DEFAULT_REFRESH = 180  # 3 min
DEFAULT_MINIMUM = 180  # 3 min


class SOA(BaseModel, ObjectUrlMixin, DisplayMixin):
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

    pretty_type = 'SOA'

    id = models.AutoField(primary_key=True)
    ttl = models.PositiveIntegerField(default=3600, blank=True, null=True,
                                      validators=[validate_ttl],
                                      verbose_name="Time to live")
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
    root_domain = models.ForeignKey("cyder.Domain", null=False, unique=True,
                                    related_name="root_of_soa")
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
        app_label = 'cyder'
        db_table = 'soa'
        # We are using the description field here to stop the same SOA from
        # being assigned to multiple zones. See the documentation in the
        # Domain models.py file for more info.

    def bind_render_record(self):
        template = Template(self.template).substitute(**self.justs)
        return template.format(root_domain=self.root_domain,
                               rdtype=self.rdtype, rdclass='IN',
                               **self.__dict__)

    def __str__(self):
        return self.root_domain.name

    def __repr__(self):
        return "<'{0}'>".format(str(self))

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        objects = objects or SOA.objects
        domains = ctnr.domains.values_list('soa')
        return objects.filter(root_domain__id__in=domains)

    def check_in_ctnr(self, ctnr):
        return self.root_domain in ctnr.domains.all()

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

    @safe_delete
    def delete(self, *args, **kwargs):
        root_domain = self.root_domain
        super(SOA, self).delete(*args, **kwargs)
        root_domain.save()
        reassign_reverse_records(root_domain, None)

    def has_record_set(self, view=None, exclude_ns=False):
        for domain in self.domain_set.all():
            if domain.has_record_set(view=view, exclude_ns=exclude_ns):
                return True
        return False

    def schedule_rebuild(self, commit=True, force=False):
        if MIGRATING and not force:
            return

        Task.schedule_zone_rebuild(self)
        self.dirty = True
        if commit:
            self.save()

    @safe_save
    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if is_new:
            self.dirty = True
        else:
            db_self = SOA.objects.get(pk=self.pk)
            if not self.dirty:
                fields = [
                    'primary', 'contact', 'expire', 'retry', 'refresh',
                    'root_domain',
                ]
                # Leave out serial and dirty so rebuilds don't cause a
                # never-ending build cycle.
                for field in fields:
                    if getattr(db_self, field) != getattr(self, field):
                        self.schedule_rebuild(commit=False)

        super(SOA, self).save(*args, **kwargs)

        if is_new:
            # Need to call this after save because new objects won't have a pk.
            self.schedule_rebuild(commit=False)
            self.root_domain.save()
            reassign_reverse_records(None, self.root_domain)
        else:
            if db_self.root_domain != self.root_domain:
                from cyder.cydns.domain.models import Domain

                self.root_domain.save()
                db_self.root_domain.save()
                self.root_domain = Domain.objects.get(pk=self.root_domain.pk)
                reassign_reverse_records(db_self.root_domain, self.root_domain)


class SOAAV(EAVBase):
    class Meta(EAVBase.Meta):
        app_label = 'cyder'
        db_table = 'soa_av'


    entity = models.ForeignKey(SOA)
    attribute = EAVAttributeField(Attribute,
        type_choices=(ATTRIBUTE_INVENTORY,))


def ip_str_to_name(ip_str, ip_type):
    from cyder.cydns.ip.utils import ip_to_domain_name, nibbilize

    if ip_type == '6':
        ip_str = nibbilize(ip_str)
    return ip_to_domain_name(ip_str, ip_type=ip_type)


def reassign_reverse_records(old_domain, new_domain):
    up = (None, None)  # from, to
    down = (None, None)  # from, to
    if new_domain:
        if (old_domain and new_domain.is_descendant_of(old_domain) and
                old_domain.soa == new_domain.master_domain.soa):
            # new_domain is below old_domain and there is no root domain
            # between them, so we can take a shortcut.
            down = (old_domain, new_domain)
        else:
            down = (new_domain.master_domain.zone_root_domain, new_domain)
    if old_domain:
        up = (old_domain, old_domain.zone_root_domain)

    if all(down):
        from cyder.cydns.domain.utils import is_name_descendant_of

        for obj in chain(down[0].reverse_ptr_set.all(),
                         down[0].reverse_staticintr_set.all()):
            if is_name_descendant_of(
                    ip_str_to_name(obj.ip_str, ip_type=obj.ip_type),
                    down[1].name):
                obj.reverse_domain = down[1]
                obj.save()
    if all(up):
        for obj in chain(up[0].reverse_ptr_set.all(),
                         up[0].reverse_staticintr_set.all()):
            obj.reverse_domain = up[1]
            obj.save()

    if old_domain:
        still_there = [unicode(x) for x in
                       chain(old_domain.reverse_ptr_set.all(),
                             old_domain.reverse_staticintr_set.all())]
        if still_there:
            raise ValidationError(
                u'No reverse domain found for the following objects: ' +
                u', '.join(still_there))
