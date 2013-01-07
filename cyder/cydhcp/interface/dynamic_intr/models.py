from django.db import models

from cyder.cydhcp.range.models import Range
from cyder.cydhcp.workgroup.models import Workgroup
from cyder.core.ctnr.models import Ctnr
from cyder.base.mixins import ObjectUrlMixin

class DynamicInterface(models.Model, ObjectUrlMixin):
    Ctnr = models.ForeignKey(Ctnr, null=False)
    range = models.ForeignKey(Range, null=False)
    workgroup = models.ForeignKey(Workgroup, null=True)
    vrf = models.ForeignKey(Vrf, null=True)
    class Meta:
        db_table = 'dynamic_interface'
