from django.shortcuts import get_object_or_404, render

from cyder.cydhcp.vlan.models import Vlan


def vlan_detail(request, vlan_pk):
    vlan = get_object_or_404(Vlan, pk=vlan_pk)
    attrs = vlan.vlankeyvalue_set.all()
    return render(request, "vlan/vlan_detail.html", {
        "vlan": vlan,
        "attrs": attrs
    })
