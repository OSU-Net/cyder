from django.shortcuts import get_object_or_404, redirect

from cyder.cydhcp.views import CydhcpCreateView
from cyder.cydhcp.vrf.forms import VrfForm
from cyder.cydhcp.vrf.models import Vrf
from cyder.base.utils import tablefy

class VrfView(object):
    model = Vrf
    queryset = Vrf.objects.all()
    form_class = VrfForm


class VrfCreateView(VrfView, CydhcpCreateView):
    """"""


def vrf_detail(request, vrf_pk):
    vrf = get_object_or_404(Vrf, pk=vrf_pk)
    attrs = VrfKeyValue.objects.filter(vrf=vrf)
    return render(request, 'vrf/vrf_detail.html',
        {
            'vrf': tablefy([vrf], views=True),
            'attrs': tablefy([attrs], views=True),
        }
    )
