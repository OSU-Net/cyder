from django.contrib.auth.models import User
from django.db import models

from cyder.base.mixins import ObjectUrlMixin
from cyder.cydns.domain.models import Domain
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.workgroup.models import Workgroup


class Ctnr(models.Model, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    users = models.ManyToManyField(User, null=False, related_name='users',
                                   through='CtnrUser', blank=True)
    domains = models.ManyToManyField(Domain, null=False, blank=True)
    ranges = models.ManyToManyField(Range, null=False, blank=True)
    workgroups = models.ManyToManyField(Workgroup, null=False, blank=True)
    description = models.CharField(max_length=200, blank=True)
    email_contact = models.EmailField(blank=True, null=True)

    class Meta:
        db_table = 'ctnr'

    def __str__(self):
        return self.name

    def details(self):
        data = super(Ctnr, self).details()
        data['data'] = (
            ('Name', 'name', self.name),
            ('Description', 'description', self.description),
        )
        return data


class CtnrUser(models.Model):
    user = models.ForeignKey(User)
    ctnr = models.ForeignKey(Ctnr)
    level = models.IntegerField()

    class Meta:
        db_table = 'ctnr_users'
        unique_together = ('ctnr', 'user')

    def get_detail_url(self):
        return '/ctnr/%s/' % (self.ctnr.id)
