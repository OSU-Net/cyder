from django.shortcuts import get_object_or_404,  render

from cyder.cydhcp.vrf.models import Vrf


def vrf_detail(request, vrf_pk):
    vrf = get_object_or_404(Vrf, pk=vrf_pk)
    attrs = vrf.vrfkeyvalue_set.all()
    return render(request, 'vrf/vrf_detail.html',
        {
            'vrf': vrf,
            'attrs': attrs,
        }
    )
