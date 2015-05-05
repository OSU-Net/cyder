from cyder.api.v1.tests.base import APITests
from cyder.core.system.models import System
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.soa.models import SOA
from cyder.cydns.tests.utils import create_zone
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.network.models import Network
from cyder.cydns.domain.models import Domain


class StaticInterfaceV4API_Test(APITests):
    __test__ = True
    model = StaticInterface

    def create_data(self):
        Domain.objects.create(name='arpa')
        system = System.objects.create(name="TestSystem", ctnr=self.ctnr)

        Domain.objects.create(name='in-addr.arpa')
        create_zone('11.in-addr.arpa')
        net = Network.objects.create(
            network_str='11.12.14.0/8', ip_type='4')
        r = Range.objects.create(
            network=net, range_type='st', ip_type='4',
            start_str='11.12.14.253', end_str='11.12.14.254')
        self.ctnr.ranges.add(r)

        return StaticInterface.objects.create(
            description='Test Static Interface', ttl=420,
            mac='11:22:33:44:55:00', system=system, label='stat',
            domain=self.domain, dhcp_enabled=False, dns_enabled=True,
            ip_str='11.12.14.253', ip_type='4')


class StaticInterfaceV6API_Test(APITests):
    __test__ = True
    model = StaticInterface

    def create_data(self):
        Domain.objects.create(name='arpa')
        system = System.objects.create(name="TestSystem", ctnr=self.ctnr)

        Domain.objects.create(name='ip6.arpa')
        create_zone('2.ip6.arpa')
        net = Network.objects.create(network_str='2001::/16', ip_type='6')
        r = Range.objects.create(
            network=net, range_type='st', ip_type='6', start_str='2001::1',
            end_str='2001:ffff:ffff:ffff:ffff:ffff:ffff:fffe')
        self.ctnr.ranges.add(r)

        return StaticInterface.objects.create(
            description='Test Static Interface', ttl=420,
            mac='11:22:33:44:55:00', system=system, label='stat',
            domain=self.domain, dhcp_enabled=False, dns_enabled=True,
            ip_str='2001:0db8:85a3:0000:0000:8a2e:0370:7344', ip_type='6')
