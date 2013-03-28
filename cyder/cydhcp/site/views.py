from django.shortcuts import get_object_or_404, render

from cyder.base.utils import make_paginator, tablefy
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.site.models import Site


def site_detail(request, site_pk):
    site = get_object_or_404(Site, pk=site_pk)
    networks = Network.objects.filter(site=site)
    network_paginator = make_paginator(
        request, networks, record_type='network')
    vlanless_networks_paginator = make_paginator(
        request, networks.filter(vlan__isnull=True), record_type='novlan')
    return render(request, 'site/site_detail.html', {
        'object': site,
        'obj_type': 'site',
        'site_table': tablefy((site,)),
        'networks_table_page_obj': network_paginator,
        'networks_table': tablefy(network_paginator),
        'attrs_table': tablefy(site.sitekeyvalue_set.all()),
        'child_sites_table': tablefy(site.site_set.all()),
        'vlanless_networks_page_obj': vlanless_networks_paginator,
        'vlanless_networks_table': tablefy(vlanless_networks_paginator),
    })
