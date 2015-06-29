from django.shortcuts import get_object_or_404

from cyder.base.views import cy_detail
from cyder.cydhcp.supernet.models import Supernet


def supernet_detail(request, pk):
    supernet = get_object_or_404(Supernet, pk=pk)
    networks = supernet.networks

    return cy_detail(request, Supernet, 'supernet/supernet_detail.html', {
        'Child Networks': networks,
    }, obj=supernet)
