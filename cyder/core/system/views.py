from cyder.base.utils import tablefy
from cyder.core.system.models import System
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.interface.static_intr.models import StaticInterface

from django.shortcuts import get_object_or_404, render


def system_detail(request, pk):
    system = get_object_or_404(System, pk=pk)
    attrs = system.systemkeyvalue_set.all()

    static = StaticInterface.objects.filter(system=system)
    dynamic = DynamicInterface.objects.filter(system=system)

    return render(request, 'system/system_detail.html', {
      'system': system,
      'system_table': tablefy([system]),
      'attrs_table': tablefy(attrs),
      'static_intrs_table': tablefy(static),
      'dynamic_intrs_table': tablefy(dynamic),
    })
