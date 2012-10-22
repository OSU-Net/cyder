from django.db import models

from cyder.cydhcp.range.models import Range


class BaseRegistration(models.Model):
    id = models.AutoField(primary_key=True)
    range = models.ForeignKey(Range, null=False)
    mac = models.CharField(max_length=12) # TODO make a mac table?

    class Meta:
        abstract = True
