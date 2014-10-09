from django.test import TestCase
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.site.models import Site


class VlanTests(TestCase):

    def do_basic_add_network(self, network, prefixlen, ip_type, name=None,
                             vlan=None, site=None):
        n = Network(network_str=network + "/" + prefixlen, ip_type=ip_type,
                    site=site, vlan=vlan)
        n.save()
        return n

    def do_basic_add_site(self, name, parent=None):
        s = Site(name=name, parent=parent)
        s.save()
        return s

    def do_basic_add_vlan(self, name, number):
        vlan = Vlan(name=name, number=number)
        vlan.save()
        return vlan
