from django.shortcuts import get_object_or_404

from cyder.base.views import cy_detail
from cyder.cydhcp.vrf.models import Vrf


def vrf_detail(request, pk):
    vrf = get_object_or_404(Vrf, pk=pk)
    return cy_detail(request, Vrf, 'cydhcp/cydhcp_detail.html', {
        'Dynamic Hosts': 'dynamicinterface_set',
        'Static Hosts': 'staticinterface_set',
        'Attributes': 'vrfkeyvalue_set',
    }, pk=pk)
