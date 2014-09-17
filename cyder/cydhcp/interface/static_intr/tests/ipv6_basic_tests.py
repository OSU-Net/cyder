from django.core.exceptions import ValidationError
from functools import partial

from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.core.system.models import System
from cyder.core.ctnr.models import Ctnr
from cyder.cydns.domain.models import Domain
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.ptr.models import PTR
from cyder.cydns.tests.utils import create_zone

from .basestatic import BaseStaticTests


class V6StaticInterTests(BaseStaticTests):
    def setUp(self):
        self.ctnr = Ctnr(name='abloobloobloo')
        self.ctnr.save()
        self.arpa = self.create_domain(name='arpa')
        self.arpa.save()
        self.i_arpa = self.create_domain(name='ip6.arpa', ip_type='6')
        self.i_arpa.save()

        self.c = Domain(name="ccc")
        self.c.save()
        self.f_c = Domain(name="foo.ccc")
        self.f_c.save()
        self.ctnr.domains.add(self.c)
        self.ctnr.domains.add(self.f_c)
        self.r1 = self.create_domain(name="0", ip_type='6')
        self.r1.save()
        self.r2 = create_zone('1.ip6.arpa')
        self.s = System(name='foobar')
        self.s.save()

        self.net = Network(network_str='1000::/16', ip_type='6')
        self.net.update_network()
        self.net.save()
        self.range = Range(network=self.net, range_type=STATIC,
                           ip_type='6', start_str='1000::1',
                           end_str='1000:ffff:ffff:ffff:ffff:ffff:ffff:fffe')
        self.range.save()
        self.ctnr.ranges.add(self.range)

    def do_add(self, mac, label, domain, ip_str, ip_type='6'):
        r = StaticInterface(mac=mac, label=label, domain=domain, ip_str=ip_str,
                            ip_type=ip_type, system=self.s, ctnr=self.ctnr,
                            range=self.range)
        r.save()
        repr(r)
        return r

    def do_delete(self, r):
        ip_str = r.ip_str
        fqdn = r.fqdn
        r.delete()
        self.assertFalse(
            AddressRecord.objects.filter(ip_str=ip_str, fqdn=fqdn))

    def test1_create_basic(self):
        mac = "11:22:33:44:55:66"

        self.do_add(
            mac=mac,
            label="foo",
            domain=self.f_c,
            ip_str=("1000:12:" + mac),
        )

    def test2_create_basic(self):
        mac = "11:22:33:44:55:66"

        self.do_add(
            mac=mac,
            label="foo1",
            domain=self.f_c,
            ip_str=("1000:123:" + mac),
        )

    def test3_create_basic(self):
        mac = "11:22:33:44:55:66"

        self.do_add(
            mac=mac,
            label="foo1",
            domain=self.f_c,
            ip_str=("1000:1234:" + mac),
        )

    def test4_create_basic(self):
        mac = "11:22:33:44:55:66"

        self.do_add(
            mac=mac,
            label="foo1",
            domain=self.f_c,
            ip_str=("1000:11:" + mac),
        )

    def test1_delete(self):
        mac = "11:22:33:44:55:66"

        r = self.do_add(
            mac=mac,
            label="foo1",
            domain=self.f_c,
            ip_str=("1000:112:" + mac),
        )
        self.do_delete(r)

    def test1_dup_create_basic(self):
        mac = "11:22:33:44:55:66"
        def x():
            self.do_add(
                mac=mac,
                label="foo3",
                domain=self.f_c,
                ip_str=("1000:1123:" + mac),
            )

        x()

        self.assertRaises(ValidationError, x)

    def test1_bad_add_for_a_ptr(self):
        # Intr exists, then try ptr and A
        mac = "11:22:33:44:55:6e"
        label = "9988fooddfdf"
        domain = self.c
        ip_str = "1000:111:" + mac

        self.do_add(mac=mac, label=label, domain=domain, ip_str=ip_str)

        self.assertRaises(ValidationError, AddressRecord.objects.create,
            label=label, domain=domain, ip_str=ip_str, ip_type='6',
            ctnr=self.ctnr)

        self.assertRaises(ValidationError, PTR.objects.create,
                ip_str=ip_str, ip_type='6',
                fqdn=(label + '.' + domain.name), ctnr=self.ctnr)

    def test2_bad_add_for_a_ptr(self):
        # PTR and A exist, then try add intr
        mac = "11:22:33:44:55:6e"
        label = "9988fooddfdf"
        domain = self.c
        ip_str = "1000:111:" + mac

        AddressRecord.objects.create(
            label=label, domain=domain, ip_str=ip_str, ip_type='6',
            ctnr=self.ctnr)

        PTR.objects.create(
                ip_str=ip_str, ip_type='6',
                fqdn=(label + '.' + domain.name), ctnr=self.ctnr)

        self.assertRaises(ValidationError, self.do_add,
            mac=mac, label=label, domain=domain, ip_str=ip_str)

    def test1_bad_reverse_domain(self):
        mac = "11:22:33:44:55:66"

        i = self.do_add(
            mac=mac,
            label="8888foo",
            domain=self.f_c,
            ip_str=("1000:115:" + mac),
        )

        i.ip_str = "9111::"
        self.assertRaises(ValidationError, i.save)

    def test1_no_system(self):
        mac = "15:22:33:44:55:66"

        self.assertRaises(ValueError, StaticInterface.objects.create,
            mac=mac,
            label="8888foo",
            domain=self.f_c,
            ip_str=("1000:188:" + mac),
            ip_type='6',
            system=None,
            ctnr=self.ctnr,
        )
