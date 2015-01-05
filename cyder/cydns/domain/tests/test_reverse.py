import ipaddr
from django.test import TestCase
from django.core.exceptions import ValidationError

from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.models import ipv6_to_longs
from cyder.cydns.ip.utils import (
    ip_prefix_to_reverse_name, ip_to_reverse_name, nibbilize)
from cyder.cydns.ptr.models import PTR
from cyder.cydns.soa.models import SOA
from cyder.cydns.tests.utils import (
    create_reverse_domain, create_zone, DNSTest, make_root)


class ReverseDomainTests(DNSTest):
    def setUp(self):
        super(ReverseDomainTests, self).setUp()

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

    def add_intr_ipv4(self, ip, label):
        return StaticInterface.objects.create(
            label=label, domain=self.domain, ip_str=ip, ip_type='4',
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

    def test_soa_validators(self):
        m = create_reverse_domain('8', ip_type='4')
        f_m = create_reverse_domain('8.2', ip_type='4')
        n_f_m = create_reverse_domain('8.2.3', ip_type='4')
        b_m = create_reverse_domain('8.3', ip_type='4')

        s = SOA.objects.create(
            primary="ns1.foo.com", contact="asdf", description="test",
            root_domain=f_m)

        n_f_m = n_f_m.reload()
        self.assertEqual(n_f_m.soa, s)

        s.root_domain = m
        s.save()

        b_m = b_m.reload()
        self.assertEqual(b_m.soa, s)

        self.assertRaises(
            ValidationError, SOA.objects.create,
            primary="ns2.foo.com", contact="asdf", description="test2",
            root_domain=m)

    def test_remove_reverse_domain(self):
        create_zone('127.in-addr.arpa')
        rd1 = create_zone('193.127.in-addr.arpa')
        rd2 = create_zone('8.193.127.in-addr.arpa')

        p1 = self.add_ptr_ipv4('127.193.8.1')
        self.assertEqual(p1.reverse_domain, rd2)
        p2 = self.add_ptr_ipv4('127.193.8.2')
        self.assertEqual(p2.reverse_domain, rd2)
        p3 = self.add_ptr_ipv4('127.193.8.3')
        self.assertEqual(p3.reverse_domain, rd2)
        p4 = self.add_ptr_ipv4('127.193.8.4')
        self.assertEqual(p4.reverse_domain, rd2)

        rd2.soa.delete()
        rd2.nameserver_set.get().delete()
        rd2.delete()

        p1 = p1.reload()
        self.assertEqual(p1.reverse_domain, rd1)
        p2 = p2.reload()
        self.assertEqual(p2.reverse_domain, rd1)
        p3 = p3.reload()
        self.assertEqual(p3.reverse_domain, rd1)
        p4 = p4.reload()
        self.assertEqual(p4.reverse_domain, rd1)

    def test_remove_reverse_domain_intr(self):
        create_zone('127.in-addr.arpa')
        rd1 = create_zone('193.127.in-addr.arpa')
        rd2 = create_zone('8.193.127.in-addr.arpa')

        p1 = self.add_intr_ipv4('127.193.8.1', 'foo')
        self.assertEqual(p1.reverse_domain, rd2)
        p2 = self.add_intr_ipv4('127.193.8.2', 'bar')
        self.assertEqual(p2.reverse_domain, rd2)
        p3 = self.add_intr_ipv4('127.193.8.3', 'qux')
        self.assertEqual(p3.reverse_domain, rd2)
        p4 = self.add_intr_ipv4('127.193.8.4', 'zih')
        self.assertEqual(p4.reverse_domain, rd2)

        rd2.soa.delete()
        rd2.nameserver_set.get().delete()
        rd2.delete()

        p1 = p1.reload()
        self.assertEqual(p1.reverse_domain, rd1)
        p2 = p2.reload()
        self.assertEqual(p2.reverse_domain, rd1)
        p3 = p3.reload()
        self.assertEqual(p3.reverse_domain, rd1)
        p4 = p4.reload()
        self.assertEqual(p4.reverse_domain, rd1)

    def test_nibbilize_bad_ip(self):
        for ip in ('asdfas', 12341245, '123.123.123.123', True, False):
            self.assertRaises(ValidationError, nibbilize, ip)

    def test_remove_invalid_reverse_domain(self):
        rd1 = create_reverse_domain('130', ip_type='4')
        rd2 = create_reverse_domain('130.193', ip_type='4')
        rd3 = create_reverse_domain('130.193.8', ip_type='4')
        self.assertRaises(ValidationError, rd1.delete)

    def test_master_domain(self):
        rd1 = create_reverse_domain('128', ip_type='4')
        rd2 = create_reverse_domain('128.193', ip_type='4')
        rd3 = create_reverse_domain('128.193.8', ip_type='4')
        self.assertEqual(rd3.master_domain, rd2)
        self.assertEqual(rd2.master_domain, rd1)
        self.assertEqual(rd1.master_domain.name, 'in-addr.arpa')

    def test_add_reverse_domains(self):
        create_reverse_domain('192.168', ip_type='4')

        create_zone('127.in-addr.arpa')
        rd0 = create_zone('193.127.in-addr.arpa')

        p1 = self.add_ptr_ipv4('127.193.8.1')
        self.assertEqual(p1.reverse_domain, rd0)
        p2 = self.add_ptr_ipv4('127.193.8.2')
        self.assertEqual(p2.reverse_domain, rd0)
        p3 = self.add_ptr_ipv4('127.193.8.3')
        self.assertEqual(p3.reverse_domain, rd0)
        p4 = self.add_ptr_ipv4('127.193.8.4')
        self.assertEqual(p4.reverse_domain, rd0)

        rd1 = create_zone('8.193.127.in-addr.arpa')

        p1 = p1.reload()
        self.assertEqual(p1.reverse_domain, rd1)
        p2 = p2.reload()
        self.assertEqual(p2.reverse_domain, rd1)
        p3 = p3.reload()
        self.assertEqual(p3.reverse_domain, rd1)
        p4 = p4.reload()
        self.assertEqual(p4.reverse_domain, rd1)

        rd1.soa.delete()
        rd1.nameserver_set.get().delete()
        rd1.delete()

        p1 = p1.reload()
        self.assertEqual(p1.reverse_domain, rd0)
        p2 = p2.reload()
        self.assertEqual(p2.reverse_domain, rd0)
        p3 = p3.reload()
        self.assertEqual(p3.reverse_domain, rd0)
        p4 = p4.reload()
        self.assertEqual(p4.reverse_domain, rd0)

    def test_add_reverse_domainless_ips(self):
        self.assertRaises(ValidationError, self.add_ptr_ipv4, ip='8.8.8.8')
        self.assertRaises(ValidationError, self.add_ptr_ipv6,
                          ip='2001:0db8:85a3:0000:0000:8a2e:0370:733')

        create_zone('2.ip6.arpa')
        create_reverse_domain('2.0.0.1', ip_type='6')
        self.add_ptr_ipv6('2001:0db8:85a3:0000:0000:8a2e:0370:733')

    def test_ipv6_to_longs(self):
        ip = ipaddr.IPv6Address('2001:0db8:85a3:0000:0000:8a2e:0370:733')
        ret = ipv6_to_longs(str(ip))
        self.assertEqual(ret, (2306139570357600256, 151930230802227))

    def test_add_remove_reverse_ipv6_zones(self):
        osu_block = "2620:105:F000"
        rd0 = create_reverse_domain('2.6.2.0.0.1.0.5.f.0.0.0', ip_type='6')
        rd0 = make_root(rd0)

        p1 = self.add_ptr_ipv6(osu_block + ":8000::1")
        self.assertEqual(p1.reverse_domain, rd0)
        p2 = self.add_ptr_ipv6(osu_block + ":8000::2")
        self.assertEqual(p2.reverse_domain, rd0)
        p3 = self.add_ptr_ipv6(osu_block + ":8000::3")
        self.assertEqual(p3.reverse_domain, rd0)
        p4 = self.add_ptr_ipv6(osu_block + ":8000::4")
        self.assertEqual(p4.reverse_domain, rd0)

        rd1 = create_reverse_domain('2.6.2.0.0.1.0.5.f.0.0.0.8', ip_type='6')
        rd1 = make_root(rd1)

        for ptr in (p1, p2, p3, p4):
            self.assertEqual(ptr.reload().reverse_domain, rd1)

        rd1.soa.delete()
        rd1.nameserver_set.get().delete()
        rd1.delete()

        for ptr in (p1, p2, p3, p4):
            self.assertEqual(ptr.reload().reverse_domain, rd0)

    def test_master_reverse_ipv6_domains(self):
        ip = '1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0.0.0.0.0.0.0.0.0.0.0.0.3.2.1'
        nibbles = ip.split('.')
        domains = []
        name = 'ip6.arpa'
        for nibble in nibbles:
            name = nibble + '.' + name
            domains.append(Domain.objects.create(name=name))

        self.assertEqual(domains[0].master_domain.name, 'ip6.arpa')
        for i in xrange(1, len(domains)):
            self.assertEqual(domains[i].master_domain, domains[i - 1])

        self.assertRaises(ValidationError, domains[18].reload().delete)

    def test_delegation_add_domain(self):
        create_zone('3.ip6.arpa')
        Domain.objects.create(name='4.3.ip6.arpa', delegated=True)

        self.assertRaises(
            ValidationError, Domain.objects.create, name='5.4.3.ip6.arpa',
            delegated=False)
