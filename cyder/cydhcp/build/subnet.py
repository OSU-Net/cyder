import os
import chili_manage

from cyder.core.ctnr.models import Ctnr
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.network.utils import calc_networks
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydhcp.workgroup.models import Workgroup


def main():
    build_str = "# DHCP Generated from cyder."
    networks = Network.objects.all()
    children = []
    for network in networks:
        _, sub = calc_networks(network)
        if not sub:
            children.append(network)
    for network in children:
        #build_str += build_subnet(network)
        build_str += network.build_subnet()
    for workgroup in Workgroup.objects.all():
        build_str += workgroup.build_workgroup()
    for vrf in Vrf.objects.all():
        build_str += vrf.build_vrf()
    for ctnr in Ctnr.objects.all():
        build_str += ctnr.build_legacy_class()

    f = open(os.path.join(os.path.dirname(__file__), 'test.conf'), 'w')
    f.write(build_str)
    f.close()
main()
