from django.db import models
# Create your models here.

from cyder.base.mixins import ObjectUrlMixin
from cyder.cydhcp.keyvalue.base_option import CommonOption


class Workgroup(models.Model, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    search_fields = ('name',)

    class Meta:
        db_table = 'workgroup'

    def __str__(self):
        return self.name

    def details(self):
        data = super(Workgroup, self).details()
        data['data'] = [
            ('Name', 'name', self),
        ]
        return data


class WorkgroupKeyValue(CommonOption):
    workgroup = models.ForeignKey(Workgroup, null=False)
    aux_attrs = (('description', 'A description of the workgroup'))

    class Meta:
        db_table = 'workgroup_key_value'
        unique_together = ('key', 'value', 'workgroup')

    def save(self, *args, **kwargs):
        self.clean()
        super(WorkgroupKeyValue, self).save(*args, **kwargs)
