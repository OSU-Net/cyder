from django.test import TestCase

from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.network.models import Network
from cyder.core.system.models import System
from cyder.core.ctnr.models import Ctnr
from cyder.cydns.domain.models import Domain
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.view.models import View

from cyder.cydns.ip.utils import ip_to_domain_name


class DeleteStaticInterTests(TestCase):
    def create_domain(self, name, ip_type=None, delegated=False):
        if ip_type is None:
            ip_type = '4'
        if name in ('arpa', 'in-addr.arpa', 'ip6.arpa'):
            pass
        else:
            name = ip_to_domain_name(name, ip_type=ip_type)
        d = Domain(name=name, delegated=delegated)
        d.clean()
        self.assertTrue(d.is_reverse)
        return d

    def setUp(self):
        self.ctnr = Ctnr(name='abloobloobloo')
        self.ctnr.save()
        self.arpa = self.create_domain(name='arpa')
        self.arpa.save()
        self.i_arpa = self.create_domain(name='in-addr.arpa')
        self.i_arpa.save()

        self.c = Domain(name="ccc")
        self.c.save()
        self.f_c = Domain(name="foo.ccc")
        self.f_c.save()
        self.r1 = self.create_domain(name="10")
        self.r1.save()
        self.n = System()
        self.n.clean()
        self.n.save()
        View.objects.get_or_create(name="private")

        self.net = Network(network_str='10.0.0.0/29')
        self.net.update_network()
        self.net.save()
        self.sr = Range(network=self.net, range_type=STATIC,
                        start_str='10.0.0.1', end_str='10.0.0.3')
        self.sr.save()

    def do_add(self, mac, label, domain, ip_str, system, ip_type='4'):
        r = StaticInterface(mac=mac, label=label, domain=domain, ip_str=ip_str,
                            ip_type=ip_type, system=system, ctnr=self.ctnr)
        r.clean()
        r.save()
        return r

    def do_delete(self, r):
        ip_str = r.ip_str
        fqdn = r.fqdn
        r.delete()
        self.assertFalse(
            AddressRecord.objects.filter(ip_str=ip_str, fqdn=fqdn))

    def test1_delete_basic(self):
        # Does deleting a system delete it's interfaces?
        mac = "112233445566"
        label = "foo"
        domain = self.f_c
        ip_str = "10.0.0.2"
        system = System(name='test1_delete_basic')
        system.save()
        kwargs = {'mac': mac, 'label': label, 'domain': domain, 'ip_str':
                ip_str, 'system': system}
        self.do_add(**kwargs)
        self.assertTrue(StaticInterface.objects.filter(**kwargs))
        system.delete()
        self.assertFalse(StaticInterface.objects.filter(**kwargs))
