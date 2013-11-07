from django.shortcuts import get_object_or_404

from cyder.base.views import cy_detail
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.network.utils import calc_networks


def network_detail(request, pk):
    network = get_object_or_404(Network, pk=pk)
    parent_networks, child_networks = calc_networks(network)
    return cy_detail(request, Network, 'network/network_detail.html', {
        'Ranges': 'range_set',
        'Parent Networks': parent_networks,
        'Child Networks': child_networks,
        'Attributes': 'networkav_set',
    }, obj=network)
