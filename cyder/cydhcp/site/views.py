from django.shortcuts import get_object_or_404

from cyder.base.views import cy_detail
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.site.models import Site


def site_detail(request, pk):
    obj = get_object_or_404(Site, pk=pk)
    networks = Network.objects.filter(site=obj)

    return cy_detail(request, Site, 'site/site_detail.html', {
        'Networks': networks,
        'Attributes': 'siteav_set',
        'Children Sites': 'site_set',
        'Vlanless Networks': networks.filter(vlan__isnull=True)
    }, obj=obj)
