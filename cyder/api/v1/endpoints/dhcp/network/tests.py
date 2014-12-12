from cyder.cydhcp.site.models import Site
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.vrf.models import Vrf
from cyder.api.v1.tests.base import APITests, APIEAVTestMixin


class NetworkV4API_Test(APITests, APIEAVTestMixin):
    __test__ = True
    model = Network

    def create_data(self):
        site = Site.objects.create(name='site')
        vlan = Vlan.objects.create(name='vlan', number=420)
        vrf = Vrf.objects.create(name='vrf')

        return Network.objects.create(
            vlan=vlan, site=site, vrf=vrf, ip_type='4',
            network_str='10.1.0.0/25')


class NetworkV6API_Test(APITests, APIEAVTestMixin):
    __test__ = True
    model = Network

    def create_data(self):
        site = Site.objects.create(name='site')
        vlan = Vlan.objects.create(name='vlan', number=420)
        vrf = Vrf.objects.create(name='vrf')

        return Network.objects.create(
            vlan=vlan, site=site, vrf=vrf, ip_type='6',
            network_str='2001:0db8::/32')
