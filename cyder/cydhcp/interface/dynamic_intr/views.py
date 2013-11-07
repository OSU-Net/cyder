from django.shortcuts import get_object_or_404

from cyder.base.views import cy_detail
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.interface.dynamic_intr.forms import DynamicInterfaceForm
from cyder.cydhcp.views import (CydhcpDeleteView, CydhcpUpdateView,
                                CydhcpCreateView, CydhcpListView,
                                CydhcpDetailView)


def dynamic_intr_detail(request, pk):
    dynamic_interface = get_object_or_404(DynamicInterface, pk=pk)

    return cy_detail(request, DynamicInterface,
                     'dynamic_intr/dynamic_intr_detail.html', {
                     'Attributes': 'dynamicinterfaceav_set',
                     }, pk=pk, obj=dynamic_interface)


class DynamicView(object):
    model = DynamicInterface
    form_class = DynamicInterfaceForm
    queryset = DynamicInterface.objects.all()


class DynamicInterfaceDetailView(DynamicView, CydhcpDetailView):
    """"""


class DynamicInterfaceDeleteView(DynamicView, CydhcpDeleteView):
    """"""


class DynamicInterfaceUpdateView(DynamicView, CydhcpUpdateView):
    """"""


class DynamicInterfaceListView(DynamicView, CydhcpListView):
    """"""


class DynamicInterfaceCreateView(DynamicView, CydhcpCreateView):
    """"""
