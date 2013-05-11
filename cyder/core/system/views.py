from django.shortcuts import get_object_or_404, render


from cyder.base.utils import tablefy
from cyder.core.system.models import System
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.interface.static_intr.models import StaticInterface


def system_detail(request, pk):
    system = get_object_or_404(System, pk=pk)
    attrs = system.systemkeyvalue_set.all()
    dynamic = DynamicInterface.objects.filter(system=system)
    static = StaticInterface.objects.filter(system=system)
    static_intr = []
    dynamic_intr = []
    for intr in static:
        static_intr.append((tablefy((intr,)),
                            tablefy(intr.staticintrkeyvalue_set.all())))
    for intr in dynamic:
        dynamic_intr.append((tablefy((intr,)),
                             tablefy(intr.dynamicintrkeyvalue_set.all())))
    return render(request, 'system/system_detail.html', {
      'system': system,
      'system_table': tablefy([system]),
      'attrs_table': tablefy(attrs),
      'static_intr_tables': static_intr,
      'dynamic_intr_tables': dynamic_intr,
      'obj_type': 'system',
      'obj': system,
    })
