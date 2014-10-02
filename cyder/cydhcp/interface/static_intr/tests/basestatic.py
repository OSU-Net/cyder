from cyder.base.tests import TestCase
from cyder.cydns.ip.utils import ip_to_domain_name
from cyder.cydns.domain.models import Domain
from cyder.cydns.tests.utils import create_zone
from cyder.cydns.view.models import View
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydns.address_record.models import AddressRecord


class BaseStaticTests(TestCase):
    def create_domain(self, name, ip_type=None, delegated=False):
        if ip_type is None:
            ip_type = '4'
        if name in ('arpa', 'in-addr.arpa', 'ip6.arpa'):
            pass
        else:
            name = ip_to_domain_name(name, ip_type=ip_type)
        d = Domain.objects.create(name=name, delegated=delegated)
        self.assertTrue(d.is_reverse)
        self.ctnr.domains.add(d)
        return d

    def setUp(self):
        self.ctnr = Ctnr.objects.create(name='abloobloobloo')
        self.arpa = self.create_domain(name='arpa')
        self.i_arpa = self.create_domain(name='in-addr.arpa')
        self.r1 = create_zone('10.in-addr.arpa')

        self.c = Domain.objects.create(name="ccc")
        self.f_c = Domain.objects.create(name="foo.ccc")
        self.ctnr.domains.add(self.c)
        self.ctnr.domains.add(self.f_c)
        self.n = System.objects.create(name='test_system')
        View.objects.get_or_create(name="private")

        self.net = Network.objects.create(network_str='10.0.0.0/29')
        self.sr = Range.objects.create(
            network=self.net, range_type=STATIC, start_str='10.0.0.1',
            end_str='10.0.0.3')
        self.ctnr.ranges.add(self.sr)

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
