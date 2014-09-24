from django.test import TestCase
from cyder.cydns.ip.utils import ip_to_domain_name
from cyder.cydns.domain.models import Domain
from cyder.cydns.view.models import View
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.ptr.models import PTR


class BaseStaticTests(TestCase):
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
        d.save()
        self.ctnr.domains.add(d)
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
        self.ctnr.domains.add(self.c)
        self.ctnr.domains.add(self.f_c)
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
        self.ctnr.ranges.add(self.sr)

    def do_add_intr(self, mac, label, domain, ip_str, ip_type='4',
                    system=None):
        if system is None:
            system = self.n
        r = StaticInterface(mac=mac, label=label, domain=domain, ip_str=ip_str,
                            ip_type=ip_type, system=system, ctnr=self.ctnr,
                            range=self.sr)
        r.clean()
        r.save()
        r.details()
        r.get_update_url()
        r.get_delete_url()
        r.get_detail_url()
        repr(r)
        return r

    def do_add_a(self, label, domain, ip_str, ip_type='4'):
        a = AddressRecord(label=label, domain=domain, ip_str=ip_str,
                          ip_type=ip_type, ctnr=self.ctnr)
        a.clean()
        a.save()
        return a

    def do_delete(self, r):
        ip_str = r.ip_str
        fqdn = r.fqdn
        r.delete()
        self.assertFalse(
            AddressRecord.objects.filter(ip_str=ip_str, fqdn=fqdn))

    def do_add_ptr(self, label, domain, ip_str, ip_type='4'):
        ptr = PTR(fqdn=label + '.' + domain.name, ip_str=ip_str,
                  ip_type=ip_type, ctnr=self.ctnr)
        ptr.clean()
        ptr.save()
        return ptr
