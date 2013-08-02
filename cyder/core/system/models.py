from django.db import models

from cyder.base.mixins import ObjectUrlMixin
from cyder.base.models import BaseModel
from cyder.base.helpers import get_display
from cyder.cydhcp.keyvalue.models import KeyValue


class System(BaseModel, ObjectUrlMixin):
    name = models.CharField(max_length=255, unique=False)

    search_fields = ('name',)
    display_fields = ('name',)

    def __str__(self):
        return get_display(self)

    class Meta:
        db_table = 'system'

    def details(self):
        """For tables."""
        data = super(System, self).details()
        data['data'] = [
            ('Name', 'name', self),
        ]
        return data

    @staticmethod
    def eg_metadata():
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'name', 'datatype': 'string', 'editable': True},
        ]}


class SystemKeyValue(KeyValue):

    system = models.ForeignKey(System, null=False)

    class Meta:
        db_table = 'system_key_value'
        unique_together = ('key', 'value', 'system')
