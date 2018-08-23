from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, FieldError
from django.db import models
from django.db.models import Q
from django.db.models.loading import get_model
from django.db.models.signals import m2m_changed
from django.forms import ModelForm

from cyder.base.constants import LEVELS, get_klasses
from cyder.base.mixins import ObjectUrlMixin
from cyder.base.models import BaseModel
from cyder.base.validators import validate_integer_field
from cyder.base.utils import transaction_atomic
from cyder.cydns.domain.models import Domain
from cyder.cydhcp.constants import DYNAMIC
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.workgroup.models import Workgroup
from cyder.cydns.ptr.models import BasePTR
from cyder.core.validation import validate_ctnr_name


class Ctnr(BaseModel, ObjectUrlMixin):
    pretty_type = 'container'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True,
                            validators=[validate_ctnr_name])
    users = models.ManyToManyField(User, null=False, related_name='ctnrs',
                                   through='CtnrUser', blank=True)
    domains = models.ManyToManyField(Domain, null=False, blank=True)
    ranges = models.ManyToManyField(Range, null=False, blank=True)
    workgroups = models.ManyToManyField(Workgroup, null=False, blank=True)
    description = models.CharField(max_length=200, blank=True)
    email_contact = models.CharField(max_length=75, blank=True)

    search_fields = ('name', 'description', 'email_contact')
    sort_fields = ('name',)

    class Meta:
        app_label = 'cyder'
        db_table = 'ctnr'

    @transaction_atomic
    def save(self, *args, **kwargs):
        self.full_clean()

        super(Ctnr, self).save(*args, **kwargs)


    @transaction_atomic
    def delete(self, *args, **kwargs):
        UserProfile = get_model('cyder','userprofile')
        for user_profile in UserProfile.objects.filter(default_ctnr_id=self.id):
            user_profile.default_ctnr_id = 1
            user_profile.save()
        super(Ctnr, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.name

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        return Ctnr.objects.filter(pk=ctnr.pk)

    def check_contains_obj(self, obj):
        if self.name == "global":
            return True

        if hasattr(obj, 'check_in_ctnr'):
            return obj.check_in_ctnr(self)

        if isinstance(obj, Ctnr):
            return obj == self

        if hasattr(obj, 'ctnr'):
            return obj.ctnr == self

        for f in [self.users, self.domains, self.ranges, self.workgroups]:
            m = f.model
            if isinstance(obj, m):
                return f.filter(pk=obj.pk).exists()

        raise Exception("Permissions check on unknown object type: %s" % type(obj))

    def details(self):
        data = super(Ctnr, self).details()
        data['data'] = (
            ('Name', 'name', self),
            ('Description', 'description', self.description),
        )
        return data

    @staticmethod
    def eg_metadata():
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'name', 'datatype': 'string', 'editable': True},
            {'name': 'description', 'datatype': 'string', 'editable': True},
        ]}

    def build_legacy_classes(self, ip_type):
        if ip_type == '4':
            ranges = self.ranges.filter(
                Q(range_type=DYNAMIC, dhcp_enabled=True) |
                Q(start_str='10.255.255.255'), ip_type='4')
        elif ip_type == '6':
            ranges = self.ranges.filter(
                ip_type='6', range_type=DYNAMIC, dhcp_enabled=True)

        build_str = ""
        for range_ in ranges:
            classname = '{0}:{1}:{2}'.format(
                self.name, range_.start_str, range_.end_str)
            build_str += (
                'class "{0}" {{\n'
                '\tmatch hardware;\n'
                '}}\n'.format(classname))
            clients = range_.dynamicinterface_set.filter(
                system__ctnr=self, dhcp_enabled=True).exclude(mac=None)
            for client in clients:
                build_str += client.build_subclass(classname)
        return build_str


class CtnrUser(BaseModel, ObjectUrlMixin):
    user = models.ForeignKey(User)
    ctnr = models.ForeignKey(Ctnr)
    level = models.IntegerField(
        validators=[validate_integer_field])

    class Meta:
        app_label = 'cyder'
        db_table = 'ctnr_users'
        unique_together = ('ctnr', 'user')

    def __str__(self):
        return self.ctnr.name

    def get_detail_url(self):
        return self.ctnr.get_detail_url()

    def details(self):
        data = super(CtnrUser, self).details()
        data['data'] = (
            ('Container', 'ctnr', self),
            ('User', 'user', self.user),
            ('Level', 'level', LEVELS[self.level]),
        )
        return data


def objects_removed(ctnr, objects, objtype="domain"):
    for obj in objects:
        for klass, _ in get_klasses():
            if klass is Domain or klass is Range:
                continue
            if ((hasattr(klass, objtype) or hasattr(klass, "%s_set" % objtype))
                    and (hasattr(klass, "ctnr")
                         or hasattr(klass, "ctnr_set"))):
                results = klass.filter_by_ctnr(ctnr, objects=None)

                if issubclass(klass, BasePTR) and objtype == "range":
                    results = [p for p in results.all() if p.range == obj]
                else:
                    try:
                        kwargs = {objtype: obj}
                    except FieldError:
                        continue
                    results = results.filter(**kwargs)

                if results:
                    raise ValidationError(
                        "Cannot remove {0} because some {1} depends on"
                        " this {0} and container.".format(objtype,
                                                          klass.pretty_type))


def domains_changed(sender, **kwargs):
    action = kwargs['action']
    if action == "pre_remove":
        ctnr = kwargs['instance']
        domains = Domain.objects.filter(pk__in=kwargs['pk_set'])
        objects_removed(ctnr, domains, objtype="domain")


def ranges_changed(sender, **kwargs):
    action = kwargs['action']
    if action == "pre_remove":
        ctnr = kwargs['instance']
        ranges = Range.objects.filter(pk__in=kwargs['pk_set'])
        objects_removed(ctnr, ranges, objtype="range")


def workgroups_changed(sender, **kwargs):
    action = kwargs['action']
    if action == "pre_remove":
        ctnr = kwargs['instance']
        workgroups = Workgroup.objects.filter(pk__in=kwargs['pk_set'])
        objects_removed(ctnr, workgroups, objtype="workgroup")


m2m_changed.connect(domains_changed, sender=Ctnr.domains.through)
m2m_changed.connect(ranges_changed, sender=Ctnr.ranges.through)
m2m_changed.connect(workgroups_changed, sender=Ctnr.workgroups.through)
