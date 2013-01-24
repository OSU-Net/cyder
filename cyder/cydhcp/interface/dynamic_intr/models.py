from django.db import models

from cyder.cydhcp.range.models import Range
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydhcp.workgroup.models import Workgroup
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydns.domain.models import Domain
from cyder.base.mixins import ObjectUrlMixin


class DynamicInterface(models.Model, ObjectUrlMixin):
    ctnr = models.ForeignKey(Ctnr, null=False)
    range = models.ForeignKey(Range, null=False)
    workgroup = models.ForeignKey(Workgroup, null=True)
    mac = models.CharField(max_length=19,
                help_text="Mac address in format XX:XX:XX:XX:XX:XX")
    system = models.ForeignKey(System, null=True, blank=True,
                help_text="System to associate the interface with")
    vrf = models.ForeignKey(Vrf, null=True)
    domain = models.ForeignKey(Domain, null=True)

    class Meta:
        db_table = 'dynamic_interface'
