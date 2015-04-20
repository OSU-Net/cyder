from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from cyder.base.views import cy_render
from cyder.cydhcp.network.models import Network


def build_network(request, network_pk):
    network = get_object_or_404(Network, pk=network_pk)
    if request.GET.get('raw', False):
        DEBUG_BUILD_STRING = network.build_subnet(raw=True)
        return HttpResponse(DEBUG_BUILD_STRING)
    else:
        DEBUG_BUILD_STRING = network.build_subnet(raw=False)
        return cy_render(
            'build/sample_build.html',
            {'data': DEBUG_BUILD_STRING, 'network': network})
