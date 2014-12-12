from cyder.cydns.tests.utils import DNSTest
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.utils import ip_to_reverse_name
from cyder.cydns.tests.utils import create_zone
from cyder.cydns.view.models import View
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydns.address_record.models import AddressRecord


class BaseStaticTests(DNSTest):
    def setUp(self, ip_type='4'):
        super(BaseStaticTests, self).setUp()

        self.c = Domain.objects.create(name="ccc")
        self.f_c = Domain.objects.create(name="foo.ccc")
        self.ctnr.domains.add(self.c)
        self.ctnr.domains.add(self.f_c)
        self.n = System.objects.create(name='test_system')
        View.objects.get_or_create(name="private")

        if ip_type == '4':
            create_zone('10.in-addr.arpa')
            self.net = Network.objects.create(network_str='10.0.0.0/27')
            self.sr = Range.objects.create(
                network=self.net, range_type=STATIC, start_str='10.0.0.1',
                end_str='10.0.0.10')
            self.ctnr.ranges.add(self.sr)
        else:
            self.net = Network.objects.create(
                network_str='1000::/16', ip_type='6')
            self.sr = Range.objects.create(
                network=self.net, range_type=STATIC, ip_type='6',
                start_str='1000::1',
                end_str='1000:ffff:ffff:ffff:ffff:ffff:ffff:fffe')
            self.ctnr.ranges.add(self.sr)

    def create_si(self, **kwargs):
        kwargs.setdefault('ctnr', self.ctnr)
        kwargs.setdefault('range', self.sr)
        kwargs.setdefault('system', self.n)
        return StaticInterface.objects.create(**kwargs)
