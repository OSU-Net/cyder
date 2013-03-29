from cyder.base.views import cy_detail
from cyder.cydhcp.vlan.models import Vlan


def vlan_detail(request, pk):
    return cy_detail(request, pk, Vlan, 'cydhcp/cydhcp_detail.html', {
        'Networks': 'network_set',
        'Attributes': 'vlankeyvalue_set',
    })
