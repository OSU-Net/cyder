from django.db import models

from cyder.base.mixins import ObjectUrlMixin
from cyder.base.models import BaseModel
from cyder.cydhcp.keyvalue.models import KeyValue


class System(BaseModel, ObjectUrlMixin):
    hostname = models.CharField(max_length=255, unique=False)
    department = models.CharField(max_length=255, unique=False)
    location = models.CharField(max_length=255, unique=False,
                                blank=True, null=True)

    search_fields = ('hostname',)

    def __str__(self):
        return self.hostname

    class Meta:
        db_table = 'system'
        unique_together = ('hostname', 'location', 'department')

    def details(self):
        data = super(System, self).details()
        data['data'] = [
            ('Host Name', 'hostname', self),
            ('Department', 'department', self.department),
            ('Location', 'location', self.location),
        ]
        return data


class SystemKeyValue(KeyValue):

    system = models.ForeignKey(System, null=False)

    class Meta:
        db_table = 'system_key_value'
        unique_together = ('key', 'value', 'system')
