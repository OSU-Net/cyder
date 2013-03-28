from django.shortcuts import get_object_or_404, render

from cyder.base.utils import make_paginator, tablefy
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.site.models import Site


def site_detail(request, site_pk):
    site = get_object_or_404(Site, pk=site_pk)
    networks = Network.objects.filter(site=site)

    return render(request, 'site/site_detail.html', {
        'object': site,
        'obj_type': 'site',
        'site_table': tablefy((site,)),
        'networks_table': tablefy(networks),
        'attrs_table': tablefy(site.sitekeyvalue_set.all()),
        'child_sites_table': tablefy(site.site_set.all()),
        'vlanless_networks_page_obj': make_paginator(
            request, networks.filter(vlan__isnull=True)),
    })
