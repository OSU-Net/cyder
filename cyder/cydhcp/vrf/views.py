from django.db.models import Q
from django.shortcuts import get_object_or_404

from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.site.models import Site
from cyder.base.views import cy_detail
from cyder.cydhcp.vrf.models import Vrf


def get_static_intr_q(vrf):
    from cyder.cydhcp.utils import start_end_filter, four_to_two
    from cyder.cydhcp.constants import STATIC

    q_list = list()
    for network_ in vrf.network_set.all():
        for range_ in network_.range_set.filter(range_type=STATIC):
            two = four_to_two(range_.start_upper, range_.start_lower,
                              range_.end_upper, range_.end_lower)
            q_list += [start_end_filter(two[0], two[1], range_.ip_type)[2]]

    q = reduce(lambda x, y: x | y, q_list, Q())
    return q or None

def vrf_detail(request, pk):
    from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface

    vrf = get_object_or_404(Vrf, pk=pk)

    static_intr_q = get_static_intr_q(vrf)
    static_intrs = (
        StaticInterface.objects.filter(static_intr_q) if static_intr_q else ())
    networks = Network.objects.filter(vrf=vrf)
    sites = Site.objects.filter(network__in=networks).distinct()

    return cy_detail(request, Vrf, 'vrf/vrf_detail.html', {
        'Dynamic Interfaces': DynamicInterface.objects.filter(
            range__network__vrf=vrf),
        'Static Interfaces': static_intrs,
        'Sites': sites,
        'Networks': networks,
        'Attributes': 'vrfav_set',
    }, pk=pk, obj=vrf)
