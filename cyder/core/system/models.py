from django.db import models

from cyder.base.mixins import ObjectUrlMixin
from cyder.base.models import BaseModel
from cyder.cydhcp.keyvalue.models import KeyValue


class System(BaseModel, ObjectUrlMixin):
    name = models.CharField(max_length=255, unique=False)
    department = models.CharField(max_length=255, unique=False)
    location = models.CharField(max_length=255, unique=False,
                                blank=True, null=True)

    search_fields = ('name', 'department', 'location')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'system'
        unique_together = ('name', 'location', 'department')

    def details(self):
        """For tables."""
        data = super(System, self).details()
        data['data'] = [
            ('Name', 'name', self),
            ('Department', 'department', self.department),
            ('Location', 'location', self.location),
        ]
        return data

    def eg_metadata(self):
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'name', 'datatype': 'string', 'editable': True},
            {'name': 'department', 'datatype': 'string', 'editable': True},
            {'name': 'location', 'datatype': 'string', 'editable': True},
        ]}


class SystemKeyValue(KeyValue):

    system = models.ForeignKey(System, null=False)

    class Meta:
        db_table = 'system_key_value'
        unique_together = ('key', 'value', 'system')
