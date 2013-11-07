from cyder.cydhcp.site.models import Site
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.vrf.models import Vrf
from cyder.api.v1.tests.base import APITests, APIEAVTestMixin


class NetworkBase(APITests, APIEAVTestMixin):
    model = Network

    def setUp(self):
        self.site = Site.objects.get_or_create(name='site')[0]
        self.vlan = Vlan.objects.get_or_create(name='vlan', number=420)[0]
        self.vrf = Vrf.objects.get_or_create(name='vrf')[0]
        super(NetworkBase, self).setUp()

    def create_data(self):
        return {
            'vlan': self.vlan,
            'site': self.site,
            'vrf': self.vrf,
        }


class NetworkV4API_Test(NetworkBase):
    __test__ = True

    def create_data(self):
        data = super(NetworkV4API_Test, self).create_data()
        data.update({
            'ip_type': '4',
            'network_str': '10.1.0.0/25',
        })
        return self.model.objects.get_or_create(**data)[0]


class NetworkV6API_Test(NetworkBase):
    __test__ = True

    def create_data(self):
        data = super(NetworkV6API_Test, self).create_data()
        data.update({
            'ip_type': '6',
            'network_str': '2001:0db8::/32',
        })
        return self.model.objects.get_or_create(**data)[0]
