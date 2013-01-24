from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models, IntegrityError
from django.db.models.query import QuerySet
from django.db.models.signals import post_save
from cyder.base.mixins import ObjectUrlMixin
from cyder.base.models import BaseModel
import ipaddr


class System(BaseModel, ObjectUrlMixin):
    YES_NO_CHOICES = (
        (0, 'No'),
        (1, 'Yes'),
    )
    hostname = models.CharField(max_length=255, unique=False)
    department = models.CharField(max_length=255, unique=False)
    location = models.CharField(max_length=255, unique=False)

    class Meta:
        db_table = 'system'
        unique_together = ('hostname', 'location', 'department')

    def details(self):
        data = super(System, self).details()
        data['data'] = [
            ('Name', 'name', self.name),
        ]
        return data
