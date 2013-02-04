from cyder.core.views import CoreListView
from cyder.core.system.forms import SystemForm
from cyder.core.system.models import System, SystemKeyValue

from django.shortcuts import get_object_or_404, render, redirect

class SystemView(object):
    model = System
    form_class = SystemForm


class SystemListView(SystemView, CoreListView):
    """"""


def system_detail(request, system_pk):
    system = get_object_or_404(System, pk=sytstem_pk)
    attrs = system.systemkeyvalue.all()

