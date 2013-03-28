from django.shortcuts import get_object_or_404,  render

from cyder.base.utils import tablefy, make_paginator
from cyder.cydhcp.vrf.models import Vrf


def vrf_detail(request, vrf_pk):
    vrf = get_object_or_404(Vrf, pk=vrf_pk)
    attrs = vrf.vrfkeyvalue_set.all()
    static_hosts_paginator = make_paginator(
        request, vrf.staticinterface_set.all(), record_type='static')
    dynamic_hosts_paginator = make_paginator(
        request, vrf.dynamicinterface_set.all(), record_type='dynamic')
    return render(request, 'vrf/vrf_detail.html', {
        'object': vrf,
        'obj_type': 'vrf',
        'vrf_table': tablefy([vrf]),
        'dynamic_hosts_page_obj': dynamic_hosts_paginator,
        'dynamic_hosts_table': tablefy(dynamic_hosts_paginator),
        'static_hosts_page_obj': static_hosts_paginator,
        'static_hosts_table': tablefy(static_hosts_paginator),
        'attrs_table': tablefy(attrs),
    })
