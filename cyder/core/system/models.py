from django.db import models

from cyder.base.mixins import ObjectUrlMixin
from cyder.base.models import BaseModel
from cyder.cydhcp.keyvalue.models import KeyValue


class System(BaseModel, ObjectUrlMixin):
    name = models.CharField(max_length=255, unique=False)
    department = models.CharField(max_length=255, unique=False, blank=True)
    location = models.CharField(max_length=255, unique=False, blank=True)

    search_fields = ('name', 'department', 'location')
    display_fields = ('name', 'pk')

    def __str__(self):
        return "{0} : {1}".format(*(str(getattr(self, f))
                                    for f in self.display_fields))

    class Meta:
        db_table = 'system'

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
