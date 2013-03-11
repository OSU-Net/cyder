from cyder.base.utils import tablefy
from cyder.base.views import (cy_view, cy_delete, get_update_form, search_obj,
                              table_update)
from cyder.core.system.forms import SystemForm
from cyder.core.system.models import System
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.interface.static_intr.models import StaticInterface

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
