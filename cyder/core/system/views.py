from cyder.core.views import CoreListView
from cyder.core.system.forms import SystemForm
from cyder.core.system.models import System
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface

from django.shortcuts import get_object_or_404, render


class SystemView(object):
    model = System
    form_class = SystemForm


class SystemListView(SystemView, CoreListView):
    """"""


def system_detail(request, system_pk):
    system = get_object_or_404(System, pk=system_pk)
    attrs = system.systemkeyvalue.all()
    dynamic = DynamicInterface.objects.filter(system=system)
    static = StaticInterface.objects.filter(system=system)
    return render(request, "site/site_details.html",
                  {
                      "system": system,
                      "attrs": attrs,
                      "dynamic_intrs": dynamic,
                      "static_intrs": static,
                  })
