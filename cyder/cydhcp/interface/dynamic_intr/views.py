from django.shortcuts import get_object_or_404

from cyder.base.views import cy_detail
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface


def dynamic_intr_detail(request, pk):
    dynamic_interface = get_object_or_404(DynamicInterface, pk=pk)

    return cy_detail(request, DynamicInterface,
                     'cydhcp/cydhcp_detail.html', {}, pk=pk,
                     obj=dynamic_interface)
