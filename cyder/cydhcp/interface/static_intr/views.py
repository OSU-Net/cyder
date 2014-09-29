from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect

from cyder.base.views import cy_detail
from cyder.cydhcp.interface.static_intr.models import (StaticInterface,
                                                       StaticInterfaceAV)


def static_intr_detail(request, pk):
    static_interface = get_object_or_404(StaticInterface, pk=pk)

    return cy_detail(request, StaticInterface,
                     'static_intr/static_intr_detail.html', {
                     'Attributes': 'staticinterfaceav_set',
                     }, pk=pk, obj=static_interface)


def detail_static_interface(reqeust, intr_pk):
    intr = get_object_or_404(StaticInterface, pk=intr_pk)
    system = intr.system
    return redirect(system)


def delete_attr(request, attr_pk):
    """
    A view destined to be called by ajax to remove an attr.
    """
    #system = get_object_or_404(System, pk=system_pk)
    #intr = get_object_or_404(StaticInterface, pk=intr_pk)
    attr = get_object_or_404(StaticInterfaceAV, pk=attr_pk)
    attr.delete()
    return HttpResponse("Attribute Removed.")
