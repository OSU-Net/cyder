from django.shortcuts import get_object_or_404, render

from cyder.base.utils import make_paginator, tablefy
from cyder.cydhcp.vlan.models import Vlan


def vlan_detail(request, vlan_pk):
    vlan = get_object_or_404(Vlan, pk=vlan_pk)
    network_paginator = make_paginator(request, vlan.network_set.all())
    return render(request, "vlan/vlan_detail.html", {
        "object": vlan,
        "vlan_table": tablefy((vlan,)),
        "attrs_table": tablefy(vlan.vlankeyvalue_set.all()),
        "network_page_obj": network_paginator,
        "network_table": tablefy(network_paginator),
    })
