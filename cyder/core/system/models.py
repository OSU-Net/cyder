from django.db import models

from cyder.base.models import BaseModel
from cyder.base.mixins import ObjectUrlMixin


class System(BaseModel, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = u'system'

    def details(self):
        data = super(System, self).details()
        data['data'] = [
            ('Name', 'name', self.name),
        ]
        return data
