from cyder.api.v1.endpoints.dhcp.tests import DHCPAPITests
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.vrf.models import Vrf


class RangeBase(DHCPAPITests):
    model = Range

    def __init__(self, *args, **kwargs):
        super(RangeBase, self).__init__(*args, **kwargs)
        self.site = Site.objects.get_or_create(name='site')[0]
        self.vlan = Vlan.objects.get_or_create(name='vlan', number=420)[0]
        self.vrf = Vrf.objects.get_or_create(name='vrf')[0]

        self.network_data = {
            'vlan': self.vlan,
            'site': self.site,
            'vrf': self.vrf,
        }


class RangeV4API_Test(RangeBase):
    def create_data(self):
        self.network_data.update({
            'ip_type': '4',
            'network_str': '10.1.0.0/8',
        })
        self.network = Network.objects.get_or_create(**self.network_data)[0]

        data = {
            'network': self.network,
            'ip_type': '4',
            'start_str': '10.1.0.0',
            'end_str': '10.1.0.255',
        }

        return self.model.objects.get_or_create(**data)[0]


class RangeV6API_Test(RangeBase):
    def create_data(self):
        self.network_data.update({
            'ip_type': '6',
            'network_str': 'ffff:ffff:ffff:fc00:0000:0000:0000:0000/12',
        })
        self.network = Network.objects.get_or_create(**self.network_data)[0]

        data = {
            'network': self.network,
            'ip_type': '6',
            'start_str': 'ffff:ffff:ffff:fc00:0000:0000:0000:0000',
            'end_str': 'ffff:ffff:ffff:fc00:0000:0000:0000:0fff',
        }

        return self.model.objects.get_or_create(**data)[0]
