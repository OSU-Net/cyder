from django.test import TestCase
from django.core.exceptions import ValidationError

from cyder.cydns.ptr.models import PTR
from cyder.cydns.tests.test_views import random_label
from cyder.cydns.tests.utils import create_fake_zone, create_zone, make_root

from cyder.cydns.ip.models import ipv6_to_longs
from cyder.cydns.ip.utils import ip_to_domain_name, nibbilize

from cyder.cydns.domain.models import Domain, boot_strap_ipv6_reverse_domain
from cyder.cydns.soa.models import SOA

from cyder.cydns.tests.utils import make_root

from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.network.models import Network

from cyder.core.system.models import System
from cyder.core.ctnr.models import Ctnr

import ipaddr


class ReverseDomainTests(TestCase):
    def setUp(self):
        self.ctnr = Ctnr.objects.create(name='abloobloobloo')

        self.arpa = self.create_reverse_domain(name='arpa')
        self.i_arpa = self.create_reverse_domain(name='in-addr.arpa')
        self.i6_arpa = self.create_reverse_domain(name='ip6.arpa')

        Domain.objects.create(name='com')
        Domain.objects.create(name='mozilla.com')
        self.domain = create_zone('foo.mozilla.com')
        self.ctnr.domains.add(self.domain)
        self.s = System.objects.create(name='mozilla.com')

        self.create_network_range(
            network_str="127.193.8.0/29", start_str="127.193.8.1",
            end_str="127.193.8.4", ip_type='4')
        self.create_network_range(
            network_str="2620:105::/32", start_str="2620:105:f000:8000::1",
            end_str="2620:105:f000:8000::1000", ip_type='6')
        self.create_network_range(
            network_str="2001:db8::/32", start_str="2001:db8:85a3::8000:0:0",
            end_str="2001:db8:85a3::9000:0:0", ip_type='6')

    def create_network_range(self, network_str, start_str, end_str,
                             range_type="st", ip_type='4', domain=None):
        if domain is None:
            domain = self.domain

        n = Network.objects.create(ip_type=ip_type, network_str=network_str)

        r = Range.objects.create(
            network=n, range_type=range_type, start_str=start_str,
            end_str=end_str, domain=domain, ip_type=ip_type)
        self.ctnr.ranges.add(r)

    def add_intr_ipv4(self, ip):
        return StaticInterface.objects.create(
            label=random_label(), domain=self.domain, ip_str=ip, ip_type='4',
            system=self.s, mac='11:22:33:44:55:66', ctnr=self.ctnr,
        )

    def add_ptr_ipv4(self, ip):
        return PTR.objects.create(
            fqdn=("bluh." + self.domain.name), ip_str=ip, ip_type='4',
            ctnr=self.ctnr)

    def add_ptr_ipv6(self, ip):
        return PTR.objects.create(
            fqdn=("bluh." + self.domain.name), ip_str=ip, ip_type='6',
            ctnr=self.ctnr)

    def create_reverse_domain(self, name, ip_type='4', delegated=False):
        if name not in ('arpa', 'in-addr.arpa', 'ip6.arpa'):
            name = ip_to_domain_name(name, ip_type=ip_type)
        d = Domain.objects.create(name=name, delegated=delegated)
        self.assertTrue(d.is_reverse)
        self.ctnr.domains.add(d)
        return d

    def test_soa_validators(self):
        m = self.create_reverse_domain(name='8')
        f_m = self.create_reverse_domain(name='8.2')
        n_f_m = self.create_reverse_domain(name='8.2.3')
        b_m = self.create_reverse_domain(name='8.3')

        s = SOA.objects.create(
            primary="ns1.foo.com", contact="asdf", description="test",
            root_domain=f_m)

        n_f_m = n_f_m.reload()
        self.assertEqual(n_f_m.soa, s)

        s.root_domain = m
        s.save()

        b_m = b_m.reload()
        self.assertEqual(b_m.soa, s)

        self.assertRaises(ValidationError, SOA.objects.create,
            primary="ns2.foo.com", contact="asdf", description="test2",
            root_domain=m)

    def test_remove_reverse_domain(self):
        create_zone('127.in-addr.arpa')
        rd1 = create_zone('193.127.in-addr.arpa')
        rd2 = create_zone('8.193.127.in-addr.arpa')
        ip1 = self.add_ptr_ipv4('127.193.8.1')
        self.assertEqual(ip1.reverse_domain, rd2)
        ip2 = self.add_ptr_ipv4('127.193.8.2')
        self.assertEqual(ip2.reverse_domain, rd2)
        ip3 = self.add_ptr_ipv4('127.193.8.3')
        self.assertEqual(ip3.reverse_domain, rd2)
        ip4 = self.add_ptr_ipv4('127.193.8.4')
        self.assertEqual(ip4.reverse_domain, rd2)
        rd2.soa.delete()
        rd2.nameserver_set.get().delete()
        rd2.delete()
        ptr1 = PTR.objects.filter(
            ip_str='127.193.8.1', ip_type='4')[0]
        self.assertEqual(ptr1.reverse_domain, rd1)
        ptr2 = PTR.objects.filter(
            ip_str='127.193.8.2', ip_type='4')[0]
        self.assertEqual(ptr2.reverse_domain, rd1)
        ptr3 = PTR.objects.filter(
            ip_str='127.193.8.2', ip_type='4')[0]
        self.assertEqual(ptr3.reverse_domain, rd1)
        ptr4 = PTR.objects.filter(
            ip_str='127.193.8.3', ip_type='4')[0]
        self.assertEqual(ptr4.reverse_domain, rd1)

    def test_remove_reverse_domain_intr(self):
        create_zone('127.in-addr.arpa')
        rd1 = create_zone('193.127.in-addr.arpa')
        rd2 = create_zone('8.193.127.in-addr.arpa')
        ip1 = self.add_intr_ipv4('127.193.8.1')
        self.assertEqual(ip1.reverse_domain, rd2)
        ip2 = self.add_intr_ipv4('127.193.8.2')
        self.assertEqual(ip2.reverse_domain, rd2)
        ip3 = self.add_intr_ipv4('127.193.8.3')
        self.assertEqual(ip3.reverse_domain, rd2)
        ip4 = self.add_intr_ipv4('127.193.8.4')
        self.assertEqual(ip4.reverse_domain, rd2)
        rd2.soa.delete()
        rd2.nameserver_set.get().delete()
        rd2.delete()
        ptr1 = StaticInterface.objects.filter(
            ip_lower=int(ipaddr.IPv4Address('127.193.8.1')),
            ip_type='4'
        )[0]
        self.assertEqual(ptr1.reverse_domain, rd1)
        ptr2 = StaticInterface.objects.filter(
            ip_lower=int(ipaddr.IPv4Address('127.193.8.2')),
            ip_type='4'
        )[0]
        self.assertEqual(ptr2.reverse_domain, rd1)
        ptr3 = StaticInterface.objects.filter(
            ip_lower=int(ipaddr.IPv4Address('127.193.8.3')),
            ip_type='4'
        )[0]
        self.assertEqual(ptr3.reverse_domain, rd1)
        ptr4 = StaticInterface.objects.filter(
            ip_lower=int(ipaddr.IPv4Address('127.193.8.4')),
            ip_type='4'
        )[0]
        self.assertEqual(ptr4.reverse_domain, rd1)

    def test_bad_nibble(self):
        for bad in ('asdfas', 12341245, '123.123.123.123', True, False):
            self.assertRaises(ValidationError, nibbilize, bad)

    def test_remove_invalid_reverse_domain(self):
        rd1 = self.create_reverse_domain(name='130', ip_type='4')
        rd2 = self.create_reverse_domain(name='130.193', ip_type='4')
        rd3 = self.create_reverse_domain(name='130.193.8', ip_type='4')
        self.assertRaises(ValidationError, rd1.delete)

    def test_master_domain(self):
        rd1 = self.create_reverse_domain(name='128', ip_type='4')
        rd2 = self.create_reverse_domain(name='128.193', ip_type='4')
        rd3 = self.create_reverse_domain(name='128.193.8', ip_type='4')
        self.assertEqual(rd3.master_domain, rd2)
        self.assertEqual(rd2.master_domain, rd1)
        self.assertEqual(rd1.master_domain, self.i_arpa)

    def test_add_reverse_domains(self):
        self.assertRaises(ValidationError, self.create_reverse_domain,
            name='192.168', ip_type='4')
        rdx = self.create_reverse_domain(name='192', ip_type='4')
        rdy = self.create_reverse_domain(name='192.168', ip_type='4')
        self.assertRaises(ValidationError, self.create_reverse_domain,
                          name='192.168', ip_type='4')

        create_zone('127.in-addr.arpa')
        rd0 = create_zone('193.127.in-addr.arpa')

        ip1 = self.add_ptr_ipv4('127.193.8.1')
        self.assertEqual(ip1.reverse_domain, rd0)
        ip2 = self.add_ptr_ipv4('127.193.8.2')
        self.assertEqual(ip2.reverse_domain, rd0)
        ip3 = self.add_ptr_ipv4('127.193.8.3')
        self.assertEqual(ip3.reverse_domain, rd0)
        ip4 = self.add_ptr_ipv4('127.193.8.4')
        self.assertEqual(ip4.reverse_domain, rd0)

        rd1 = create_zone('8.193.127.in-addr.arpa')

        ptr1 = PTR.objects.filter(ip_lower=ipaddr.IPv4Address(
            '127.193.8.1').__int__(), ip_type='4')[0]
        self.assertEqual(ptr1.reverse_domain, rd1)
        ptr2 = PTR.objects.filter(ip_lower=ipaddr.IPv4Address(
            '127.193.8.2').__int__(), ip_type='4')[0]
        self.assertEqual(ptr2.reverse_domain, rd1)
        ptr3 = PTR.objects.filter(ip_lower=ipaddr.IPv4Address(
            '127.193.8.3').__int__(), ip_type='4')[0]
        self.assertEqual(ptr3.reverse_domain, rd1)
        ptr4 = PTR.objects.filter(ip_lower=ipaddr.IPv4Address(
            '127.193.8.4').__int__(), ip_type='4')[0]
        self.assertEqual(ptr4.reverse_domain, rd1)

        rd1.soa.delete()
        rd1.nameserver_set.get().delete()
        rd1.delete()

        ptr1 = PTR.objects.filter(ip_lower=ipaddr.IPv4Address(
            '127.193.8.1').__int__(), ip_type='4')[0]
        self.assertEqual(ptr1.reverse_domain, rd0)
        ptr2 = PTR.objects.filter(ip_lower=ipaddr.IPv4Address(
            '127.193.8.2').__int__(), ip_type='4')[0]
        self.assertEqual(ptr2.reverse_domain, rd0)
        ptr3 = PTR.objects.filter(ip_lower=ipaddr.IPv4Address(
            '127.193.8.2').__int__(), ip_type='4')[0]
        self.assertEqual(ptr3.reverse_domain, rd0)
        ptr4 = PTR.objects.filter(ip_lower=ipaddr.IPv4Address(
            '127.193.8.3').__int__(), ip_type='4')[0]
        self.assertEqual(ptr4.reverse_domain, rd0)

    def test_boot_strap_add_ipv6_domain(self):
        osu_block = "2.6.2.1.1.0.5.F.0.0.0"
        test_dname = osu_block + ".d.e.a.d.b.e.e.f"
        boot_strap_ipv6_reverse_domain(test_dname)

        self.assertRaises(ValidationError, self.create_reverse_domain,
                          name='2.6.2.1.1.0.5.f.0.0.0', ip_type='6')
        self.assertRaises(ValidationError, self.create_reverse_domain,
                          name='2.6.2.1', ip_type='6')
        self.assertRaises(ValidationError, self.create_reverse_domain,
                          name='2.6.2.1.1.0.5.F.0.0.0.d.e.a.d', ip_type='6')
        self.assertRaises(ValidationError, self.create_reverse_domain,
                          name='2.6.2.1.1.0.5.F.0.0.0.d.e.a.d.b.e.e.f',
                          ip_type='6')
        self.assertRaises(ValidationError, self.create_reverse_domain,
                          name=test_dname, ip_type='6')

        # These should pass.
        boot_strap_ipv6_reverse_domain('7.6.2.4')
        boot_strap_ipv6_reverse_domain('6.6.2.5.1')
        # These are pretty unrealistic since they protrude into the host part
        # of the address.
        boot_strap_ipv6_reverse_domain(
            '4.6.2.2.1.0.5.3.f.0.0.0.1.2.3.4.1.2.3.4.1.2.3.4.1.2.3.4.1.2.3.4')
        boot_strap_ipv6_reverse_domain(
            '5.6.2.3.1.0.5.3.f.0.0.0.1.2.3.4.1.2.3.4.1.2.3.4')

    def test_add_reverse_domainless_ips(self):
        self.assertRaises(ValidationError, self.add_ptr_ipv4, ip='8.8.8.8')
        self.assertRaises(ValidationError, self.add_ptr_ipv6,
                          ip='2001:0db8:85a3:0000:0000:8a2e:0370:733')

        create_zone('2.ip6.arpa')
        boot_strap_ipv6_reverse_domain("2.0.0.1")
        self.assertRaises(ValidationError, self.create_reverse_domain,
                          name='2.0.0.1', ip_type='6')
        self.add_ptr_ipv6('2001:0db8:85a3:0000:0000:8a2e:0370:733')

    def test_ipv6_to_longs(self):
        ip = ipaddr.IPv6Address('2001:0db8:85a3:0000:0000:8a2e:0370:733')
        ret = ipv6_to_longs(ip.__str__())
        self.assertEqual(ret, (2306139570357600256, 151930230802227))

    def test_bad_names(self):
        self.assertRaises(ValidationError, self.create_reverse_domain,
                          name=None, ip_type='6')
        self.assertRaises(ValidationError, self.create_reverse_domain,
                          name=124, ip_type='6')
        self.assertRaises(ValidationError, self.create_reverse_domain,
                          name='0.9.0', ip_type='asdf')
        self.assertRaises(ValidationError, self.create_reverse_domain,
                          name='0.9.0', ip_type=None)
        self.assertRaises(ValidationError, self.create_reverse_domain,
                          name='0.9.0', ip_type=1234)

    def test_add_remove_reverse_ipv6_zones(self):
        osu_block = "2620:105:F000"
        boot_strap_ipv6_reverse_domain('2.6.2.0.0.1.0.5.f.0.0')
        rd0 = create_zone(
            ip_to_domain_name('2.6.2.0.0.1.0.5.f.0.0.0', ip_type='6'))

        ip1 = self.add_ptr_ipv6(osu_block + ":8000::1")
        self.assertEqual(ip1.reverse_domain, rd0)
        ip2 = self.add_ptr_ipv6(osu_block + ":8000::2")
        self.assertEqual(ip2.reverse_domain, rd0)
        ip3 = self.add_ptr_ipv6(osu_block + ":8000::3")
        self.assertEqual(ip3.reverse_domain, rd0)
        self.add_ptr_ipv6(osu_block + ":8000::4")

        rd1 = create_zone(ip_to_domain_name('2.6.2.0.0.1.0.5.f.0.0.0.8',
                                            ip_type='6'))

        for suffix in (':8000::1', ':8000::2', ':8000::3', ':8000::4'):
            ip_upper, ip_lower = ipv6_to_longs(osu_block + suffix)
            ptr = PTR.objects.filter(
                ip_upper=ip_upper, ip_lower=ip_lower, ip_type='6')[0]
            self.assertEqual(ptr.reverse_domain, rd1)

        rd1.soa.delete()
        rd1.nameserver_set.get().delete()
        rd1.delete()

        for suffix in (':8000::1', ':8000::2', ':8000::3', ':8000::4'):
            ip_upper, ip_lower = ipv6_to_longs(osu_block + suffix)
            ptr = PTR.objects.filter(
                ip_upper=ip_upper, ip_lower=ip_lower, ip_type='6')[0]
            self.assertEqual(ptr.reverse_domain, rd0)

    def test_master_reverse_ipv6_domains(self):
        ip = '1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0.0.0.0.0.0.0.0.0.0.0.0.3.2.1'
        nibbles = ip.split('.')
        domains = []
        name = 'ip6.arpa'
        for nibble in nibbles:
            name = nibble + '.' + name
            domains.append(Domain.objects.create(name=name))

        self.assertEqual(domains[0].master_domain, self.i6_arpa)
        for i in xrange(1, len(domains)):
            self.assertEqual(domains[i].master_domain, domains[i - 1])

        d = Domain.objects.get(
            name=ip_to_domain_name(
                '1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0.0', ip_type='6'))
        self.assertRaises(ValidationError, d.delete)

    def test_delegation_add_domain(self):
        three = self.create_reverse_domain(name='3')
        three = make_root(three)
        four = self.create_reverse_domain(name='3.4', delegated=True)

        self.assertRaises(ValidationError, self.create_reverse_domain,
                          name='3.4.5', delegated=False)
