from django.shortcuts import get_object_or_404, render

from cyder.base.views import cy_detail
from cyder.cydhcp.vlan.models import Vlan


def vlan_detail(request, pk):
    vlan = get_object_or_404(Vlan, pk=pk)

    return cy_detail(request, Vlan, 'vlan/vlan_detail.html', {
        'Networks': 'network_set',
        'Attributes': 'vlanav_set',
    }, pk=pk, obj=vlan)
