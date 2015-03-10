from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect

from cyder.base.views import cy_detail
from cyder.cydhcp.interface.static_intr.models import StaticInterface


def static_intr_detail(request, pk):
    static_interface = get_object_or_404(StaticInterface, pk=pk)

    return cy_detail(request, StaticInterface,
                     'cydhcp/cydhcp_detail.html', {},
                     pk=pk, obj=static_interface)


def detail_static_interface(reqeust, intr_pk):
    intr = get_object_or_404(StaticInterface, pk=intr_pk)
    system = intr.system
    return redirect(system)
