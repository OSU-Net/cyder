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
            self.net = Network.objects.create(network_str='10.0.0.0/29')
            self.sr = Range.objects.create(
                network=self.net, range_type=STATIC, start_str='10.0.0.1',
                end_str='10.0.0.3')
            self.ctnr.ranges.add(self.sr)
        else:
            self.net = Network.objects.create(
                network_str='1000::/16', ip_type='6')
            self.range = Range.objects.create(
                network=self.net, range_type=STATIC, ip_type='6',
                start_str='1000::1',
                end_str='1000:ffff:ffff:ffff:ffff:ffff:ffff:fffe')
            self.range.save()
            self.ctnr.ranges.add(self.range)

    def do_add_intr(self, mac, label, domain, ip_str, ip_type='4',
                    system=None):
        system = system or self.n
        r = StaticInterface.objects.create(
            mac=mac, label=label, domain=domain, ip_str=ip_str,
            ip_type=ip_type, system=system, ctnr=self.ctnr, range=self.sr)
        r.details()
        r.get_update_url()
        r.get_delete_url()
        r.get_detail_url()
        repr(r)
        return r

    def do_delete(self, r):
        ip_str = r.ip_str
        fqdn = r.fqdn
        r.delete()
        self.assertFalse(
            AddressRecord.objects.filter(ip_str=ip_str, fqdn=fqdn))
