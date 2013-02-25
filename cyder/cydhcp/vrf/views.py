from cyder.cydhcp.views import CydhcpCreateView
from cyder.cydhcp.vrf.forms import VrfForm
from cyder.cydhcp.vrf.models import Vrf


class VrfView(object):
    model = Vrf
    queryset = Vrf.objects.all()
    form_class = VrfForm


class VrfCreateView(VrfView, CydhcpCreateView):
    """"""
