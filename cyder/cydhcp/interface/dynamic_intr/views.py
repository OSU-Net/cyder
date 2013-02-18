from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.interface.dynamic_intr.forms import DynamicInterfaceForm
from cyder.cydhcp.views import (CydhcpDeleteView, CydhcpUpdateView,
                                CydhcpCreateView, CydhcpListView,
                                CydhcpDetailView)


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
