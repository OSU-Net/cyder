from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from cyder.base.constants import LEVELS
from cyder.base.mixins import ObjectUrlMixin
from cyder.base.models import BaseModel
from cyder.base.helpers import get_display
from cyder.cydns.domain.models import Domain
from cyder.cydhcp.constants import DYNAMIC
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.workgroup.models import Workgroup
from cyder.core.validation import validate_ctnr_name


class Ctnr(BaseModel, ObjectUrlMixin):
    pretty_type = 'container'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True,
                            validators=[validate_ctnr_name])
    users = models.ManyToManyField(User, null=False, related_name='users',
                                   through='CtnrUser', blank=True)
    domains = models.ManyToManyField(Domain, null=False, blank=True)
    ranges = models.ManyToManyField(Range, null=False, blank=True)
    workgroups = models.ManyToManyField(Workgroup, null=False, blank=True)
    description = models.CharField(max_length=200, blank=True)
    email_contact = models.CharField(max_length=75, blank=True)

    display_fields = ('name',)
    search_fields = ('name', 'description')

    class Meta:
        app_label = 'cyder'
        db_table = 'ctnr'

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Ctnr, self).save(*args, **kwargs)

    def __str__(self):
        return get_display(self)

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

    def build_legacy_classes(self):
        build_str = ""
        for range_ in self.ranges.filter(Q(range_type=DYNAMIC,
                                           dhcp_enabled=True) |
                                         Q(start_str='10.255.255.255')):
            clients = (range_.dynamicinterface_set.filter(ctnr=self,
                                                          dhcp_enabled=True)
                                                  .exclude(mac=''))

            classname = '{0}:{1}:{2}'.format(
                self.name, range_.start_str, range_.end_str)

            build_str += ('class "{0}" {{\n'
                          '\tmatch hardware;\n'
                          '}}\n'
                          .format(classname))

            for client in clients:
                build_str += client.build_subclass(classname)
        return build_str


class CtnrUser(BaseModel, ObjectUrlMixin):
    user = models.ForeignKey(User)
    ctnr = models.ForeignKey(Ctnr)
    level = models.IntegerField()

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
