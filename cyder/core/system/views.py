from cyder.base.views import (cy_view, cy_delete, get_update_form, search_obj,
                              table_update)
from cyder.core.system.forms import SystemForm
from cyder.core.system.models import System
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface

from django.shortcuts import get_object_or_404, render


def get_klasses(itdoesntmatterwhatyoupass):
    return (System, SystemForm, None)


def system_view(request, pk=None):
    return cy_view(request, get_klasses, 'system/system_view.html', pk,
                   'system')


def system_get_update_form(request):
    return get_update_form(request, get_klasses)


def system_search_obj(request):
    return search_obj(request, get_klasses)


def system_delete(request, pk):
    return cy_delete(request, pk, get_klasses)


def system_table_update(request, pk, record_type=None):
    return table_update(request, pk, get_klasses, record_type)


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
