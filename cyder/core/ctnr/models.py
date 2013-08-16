from django.contrib.auth.models import User
from django.db import models

from cyder.base.constants import LEVELS
from cyder.base.mixins import ObjectUrlMixin
from cyder.base.helpers import get_display
from cyder.cydns.domain.models import Domain
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.workgroup.models import Workgroup
from cyder.core.validation import validate_ctnr_name


class Ctnr(models.Model, ObjectUrlMixin):
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
        db_table = 'ctnr'

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Ctnr, self).save(*args, **kwargs)

    def __str__(self):
        return get_display(self)

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        return Ctnr.objects.filter(pk=ctnr.pk)

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

    def build_legacy_class(self):
        from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
        build_str = ""
        for range_ in self.ranges.all():
            build_str += ("class \"{0}:{1}:{2}\" {{"
                          "\n\tmatch hardware;\n}}\n".format(
                              self.name, range_.start_str, range_.end_str))
            for client in DynamicInterface.objects.filter(range=range_,
                                                          ctnr=self,
                                                          dhcp_enabled=True):
                if client.mac:
                    build_str += client.build_subclass(self.name)
        return build_str


class CtnrUser(models.Model, ObjectUrlMixin):
    user = models.ForeignKey(User)
    ctnr = models.ForeignKey(Ctnr)
    level = models.IntegerField()

    class Meta:
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
