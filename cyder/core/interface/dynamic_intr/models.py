from django.db import models

from cyder.core.ctnr.models import Ctnr
from cyder.core.interface.models import BaseInterface
from cyder.mozdns.mozdhcp.range.models import Range


class DynamicInterface(BaseInterface):
    Ctnr = models.ForeignKey(Ctnr, null=False)
    range = models.ForeignKey(Range, null=False)

    class Meta:
        db_table = 'dynamic_interface'
