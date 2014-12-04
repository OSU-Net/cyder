from cyder.cydhcp.range.models import Range
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.vrf.models import Vrf
from cyder.api.v1.tests.base import APITests, APIEAVTestMixin


class RangeV4API_Test(APITests, APIEAVTestMixin):
    __test__ = True
    model = Range

    def create_data(self):
        self.site = Site.objects.create(name='site')
        self.vlan = Vlan.objects.create(name='vlan', number=420)
        self.vrf = Vrf.objects.create(name='vrf')

        network = Network.objects.create(
            vlan=self.vlan, site=self.site, vrf=self.vrf, ip_type='4',
            network_str='10.1.0.0/8')

        return Range.objects.create(
            network=network, ip_type='4', start_str='10.1.0.0',
            end_str='10.1.0.255')


class RangeV6API_Test(APITests, APIEAVTestMixin):
    __test__ = True
    model = Range

    def create_data(self):
        self.site = Site.objects.create(name='site')
        self.vlan = Vlan.objects.create(name='vlan', number=420)
        self.vrf = Vrf.objects.create(name='vrf')

        network = Network.objects.create(
            vlan=self.vlan, site=self.site, vrf=self.vrf, ip_type='6',
            network_str='ffff:ffff:ffff:fc00:0000:0000:0000:0000/12')

        return Range.objects.create(
            network=network, ip_type='6',
            start_str='ffff:ffff:ffff:fc00:0000:0000:0000:0000',
            end_str='ffff:ffff:ffff:fc00:0000:0000:0000:0fff')
