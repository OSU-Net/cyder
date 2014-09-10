from functools import partial

from django.core.exceptions import ValidationError

import cyder.base.tests
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydns.tests.utils import create_basic_dns_data, create_zone
from cyder.cydns.ip.utils import ip_to_domain_name
from cyder.cydns.domain.models import Domain, boot_strap_ipv6_reverse_domain
from cyder.cydns.ptr.models import PTR
from cyder.cydns.ip.models import Ip
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.vrf.models import Vrf


class PTRTests(cyder.base.tests.TestCase):
    def setUp(self):
        self.ctnr = Ctnr(name='abloobloobloo')
        self.ctnr.save()

        create_basic_dns_data(dhcp=True)

        self._128 = create_zone('128.in-addr.arpa')
        create_zone('8.ip6.arpa')

        self.c1 = Ctnr(name='test_ctnr1')
        self.c1.save()

        self.n = Network(vrf=Vrf.objects.get(name='test_vrf'), ip_type='4',
                         network_str='128.193.0.0/24')
        self.n.save()

        self.r = Range(network=self.n, range_type='st',
                       start_str='128.193.0.2', end_str='128.193.0.100')
        self.r.save()

        self.c1.ranges.add(self.r)

        for name in ('edu', 'oregonstate.edu', 'bar.oregonstate.edu',
                     'nothing', 'nothing.nothing', 'nothing.nothing.nothing'):
            d = Domain(name=name)
            d.save()
            self.c1.domains.add(d)

        boot_strap_ipv6_reverse_domain("8.6.2.0")

        self.osu_block = "8620:105:F000:"
        self.create_network_range(network_str="8620:105::/32",
                                  start_str='8620:105:F000::1',
                                  end_str='8620:105:F000::1000', ip_type='6')

    def create_domain(self, name, ip_type=None, delegated=False):
        if ip_type is None:
            ip_type = '4'
        if name in ('arpa', 'in-addr.arpa', 'ip6.arpa'):
            pass
        else:
            name = ip_to_domain_name(name, ip_type=ip_type)
        d = Domain.objects.create(name=name, delegated=delegated)
        self.assertTrue(d.is_reverse)
        return d

    def create_network_range(self, network_str, start_str, end_str,
                             range_type="st", ip_type='4', domain=None):
        if domain is None:
            domain = Domain.objects.get(name="oregonstate.edu")

        n = Network(vrf=Vrf.objects.get(name='test_vrf'), ip_type=ip_type,
                    network_str=network_str)
        n.save()

        r = Range(network=n, range_type=range_type, start_str=start_str,
                  end_str=end_str, domain=domain, ip_type=ip_type)
        r.save()

        self.c1.ranges.add(r)

    def do_generic_add(self, ip_str, fqdn, ip_type, domain=None, ctnr=None):
        if ctnr is None:
            ctnr = self.c1

        ret = PTR(fqdn=fqdn, ip_str=ip_str, ip_type=ip_type,
                  ctnr=ctnr)
        ret.save()

        self.assertTrue(ret.details())

        ip = Ip(ip_str=ip_str, ip_type=ip_type)
        ip.clean_ip()
        ptr = PTR.objects.filter(
            fqdn=fqdn, ip_upper=ip.ip_upper, ip_lower=ip.ip_lower)
        ptr.__repr__()
        self.assertTrue(ptr)
        ip_str = ip_str.lower()
        self.assertEqual(ptr[0].ip_str, ip_str)
        if domain:
            if ptr[0].fqdn == "":
                self.assertEqual(fqdn, domain.name)
            else:
                self.assertEqual(fqdn, ptr[0].fqdn + "." + domain.name)
        else:
            self.assertEqual(fqdn, ptr[0].fqdn)
        return ret

    def test_dns_form_ipv4(self):
        self.create_network_range(network_str='128.193.1.0/24',
                                  start_str='128.193.1.201',
                                  end_str='128.193.1.240')
        ret = self.do_generic_add(
            "128.193.1.230", "foo.bar.oregonstate.edu", '4')
        self.assertEqual("230.1.193.128.in-addr.arpa.", ret.dns_name())

    def test_dns_form_ipv6(self):
        ret = self.do_generic_add("8620:105:F000::1",
                                  "foo.bar.oregonstate.edu", '6')
        self.assertEqual(
            "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.f.5.0.1.0.0.2.6.8"
            ".ip6.arpa.", ret.dns_name())

    def do_generic_invalid_add(
            self, ip, fqdn, ip_type, exception, domain=None):
        with self.assertRaises(exception):
            self.do_generic_add(ip, fqdn, ip_type, domain)

    def test_no_domain(self):
        test_ip = "244.123.123.123"
        name = "lol.foo"
        self.do_generic_invalid_add(test_ip, name, '4', ValidationError)
        name = "oregonstate.com"
        self.do_generic_invalid_add(test_ip, name, '4', ValidationError)
        name = "me.oregondfastate.edu"
        self.do_generic_invalid_add(test_ip, name, '4', ValidationError)

    def test_add_invalid_name_ipv6_ptr(self):
        bad_name = "testyfoo.com"
        test_ip = self.osu_block + ":1"
        bad_name = "2134!@#$!@"
        self.do_generic_invalid_add(test_ip, bad_name, '6', ValidationError)
        bad_name = "asdflj..com"
        self.do_generic_invalid_add(test_ip, bad_name, '6', ValidationError)
        bad_name = "A" * 257
        self.do_generic_invalid_add(test_ip, bad_name, '6', ValidationError)

    """
    Is this test redundant?
    """
    def test_add_invalid_name_ipv4_ptr(self):
        bad_name = "testyfoo.com"
        test_ip = "128.123.123.123"
        bad_name = "2134!@#$!@"
        self.do_generic_invalid_add(test_ip, bad_name, '4', ValidationError)
        bad_name = "asdflj..com"
        self.do_generic_invalid_add(test_ip, bad_name, '4', ValidationError)
        bad_name = "A" * 257
        self.do_generic_invalid_add(test_ip, bad_name, '4', ValidationError)

    def test_add_invalid_ip_ipv6_ptr(self):
        test_name = "oregonstate.edu"
        bad_ip = "123.123.123.123."
        self.do_generic_invalid_add(bad_ip, test_name, '6', ValidationError)
        bad_ip = "123:!23:!23:"
        self.do_generic_invalid_add(bad_ip, test_name, '6', ValidationError)
        bad_ip = ":::"
        self.do_generic_invalid_add(bad_ip, test_name, '6', ValidationError)
        bad_ip = None
        self.do_generic_invalid_add(bad_ip, test_name, '6', ValidationError)
        bad_ip = True
        self.do_generic_invalid_add(bad_ip, test_name, '6', ValidationError)
        bad_ip = False
        self.do_generic_invalid_add(bad_ip, test_name, '6', ValidationError)
        bad_ip = lambda x: x
        self.do_generic_invalid_add(bad_ip, test_name, '6', ValidationError)

        bad_ip = "8::9:9:1"
        self.do_generic_invalid_add(bad_ip, test_name, '6', ValidationError)
        bad_ip = "11:9:9::1"
        self.do_generic_invalid_add(bad_ip, test_name, '6', ValidationError)

        bad_ip = "8.9.9.1"
        self.do_generic_invalid_add(bad_ip, test_name, '6', ValidationError)
        bad_ip = "11.9.9.1"
        self.do_generic_invalid_add(bad_ip, test_name, '6', ValidationError)

        bad_ip = self.osu_block + ":233"
        self.do_generic_add(bad_ip, "foo.bar.oregonstate.edu", '6')
        self.do_generic_invalid_add(
            bad_ip, "foo.bar.oregonstate.edu", '6', ValidationError)
        self.do_generic_invalid_add(self.osu_block + ":0:0:0233",
                                    "foo.bar.oregonstate.edu", '6',
                                    ValidationError)

        self.do_generic_add(self.osu_block + ":dd",
                            "foo.bar.oregonstate.edu", '6')
        self.do_generic_invalid_add(self.osu_block + ":dd",
                                    "foo.bar.oregonstate.edu", '6',
                                    ValidationError)

    def test_add_invalid_ip_ipv4_ptr(self):
        test_name = "oregonstate.edu"
        bad_ip = "123.123"
        self.do_generic_invalid_add(bad_ip, test_name, '4', ValidationError)
        bad_ip = "asdfasdf"
        self.do_generic_invalid_add(bad_ip, test_name, '4', ValidationError)
        bad_ip = 32141243
        self.do_generic_invalid_add(bad_ip, test_name, '4', ValidationError)
        bad_ip = "128.123.123.123.123"
        self.do_generic_invalid_add(bad_ip, test_name, '4', ValidationError)
        bad_ip = "...."
        self.do_generic_invalid_add(bad_ip, test_name, '4', ValidationError)
        bad_ip = "1234."
        self.do_generic_invalid_add(bad_ip, test_name, '4', ValidationError)
        bad_ip = None
        self.do_generic_invalid_add(bad_ip, test_name, '4', ValidationError)
        bad_ip = False
        self.do_generic_invalid_add(bad_ip, test_name, '4', ValidationError)
        bad_ip = True
        self.do_generic_invalid_add(bad_ip, test_name, '4', ValidationError)

        bad_ip = "8.9.9.1"
        self.do_generic_invalid_add(bad_ip, test_name, '4', ValidationError)
        bad_ip = "11.9.9.1"
        self.do_generic_invalid_add(bad_ip, test_name, '4', ValidationError)

        self.create_network_range(network_str='128.193.1.0/24',
                                  start_str='128.193.1.1',
                                  end_str='128.193.1.100')
        self.do_generic_add("128.193.1.1", "foo.bar.oregonstate.edu", '4')
        self.do_generic_invalid_add(
            "128.193.1.1", "foo.bar.oregonstate.edu", '4', ValidationError)

        self.create_network_range(network_str='128.128.1.0/24',
                                  start_str='128.128.1.1',
                                  end_str='128.128.1.100')
        self.do_generic_add(
            "128.128.1.1", "foo.bar.oregonstate.edu", '4')
        self.do_generic_invalid_add(
            "128.128.1.1", "foo.bar.oregonstate.edu", '4', ValidationError)

    def do_generic_remove(self, ip, fqdn, ip_type):
        ptr = PTR(ctnr=self.c1, ip_str=ip, fqdn=fqdn, ip_type=ip_type)
        ptr.save()

        ptr.delete()

        ip = Ip(ip_str=ip, ip_type=ip_type)
        ip.clean_ip()
        ptr = PTR.objects.filter(fqdn=fqdn, ip_upper=ip.ip_upper,
                                 ip_lower=ip.ip_lower)
        self.assertFalse(ptr)

    def test_remove_ipv4(self):
        self.create_network_range(network_str='128.255.1.0/16',
                                  start_str='128.255.1.1',
                                  end_str='128.255.233.254')
        ip = "128.255.233.244"
        fqdn = "asdf34foo.bar.oregonstate.edu"
        self.do_generic_remove(ip, fqdn, '4')
        ip = "128.255.11.13"
        fqdn = "fo124kfasdfko.bar.oregonstate.edu"
        self.do_generic_remove(ip, fqdn, '4')
        ip = "128.255.9.1"
        fqdn = "or1fdsaflkegonstate.edu"
        self.do_generic_remove(ip, fqdn, '4')
        ip = "128.255.1.7"
        fqdn = "12.bar.oregonstate.edu"
        self.do_generic_remove(ip, fqdn, '4')
        ip = "128.255.1.3"
        fqdn = "fcwoo.bar.oregonstate.edu"
        self.do_generic_remove(ip, fqdn, '4')
        ip = "128.255.1.2"
        fqdn = "asffad124jfasf-oregonstate.edu"
        self.do_generic_remove(ip, fqdn, '4')

    def test_remove_ipv6(self):
        ip = self.osu_block + ":1"
        fqdn = "asdf34foo.bar.oregonstate.edu"
        self.do_generic_remove(ip, fqdn, '6')
        ip = self.osu_block + ":2"
        fqdn = "fo124kfasdfko.bar.oregonstate.edu"
        self.do_generic_remove(ip, fqdn, '6')
        ip = self.osu_block + ":8"
        fqdn = "or1fdsaflkegonstate.edu"
        self.do_generic_remove(ip, fqdn, '6')
        ip = self.osu_block + ":8"
        fqdn = "12.bar.oregonstate.edu"
        self.do_generic_remove(ip, fqdn, '6')
        ip = self.osu_block + ":20"
        fqdn = "fcwoo.bar.oregonstate.edu"
        self.do_generic_remove(ip, fqdn, '6')
        ip = self.osu_block + ":ad"
        fqdn = "asffad124jfasf-oregonstate.edu"
        self.do_generic_remove(ip, fqdn, '6')

    def do_generic_update(self, ptr, new_fqdn, ip_type):
        ptr.fqdn = new_fqdn
        ptr.save()

        ptr = PTR.objects.filter(fqdn=new_fqdn, ip_upper=ptr.ip_upper,
                                 ip_lower=ptr.ip_lower)
        self.assertTrue(ptr)
        self.assertEqual(new_fqdn, ptr[0].fqdn)

    def test_update_ipv4(self):
        self.create_network_range(network_str='128.193.1.0/24',
                                  start_str='128.193.1.1',
                                  end_str='128.193.1.100')
        ptr = self.do_generic_add("128.193.1.1", "oregonstate.edu", '4')
        fqdn = "nothing.nothing.nothing"
        self.do_generic_update(ptr, fqdn, '4')
        fqdn = "google.edu"
        self.do_generic_update(ptr, fqdn, '4')
        fqdn = "bar.oregonstate.edu"
        self.do_generic_update(ptr, fqdn, '6')

    def test_update_ipv6(self):
        ptr = self.do_generic_add(
            self.osu_block + ":1", "oregonstate.edu", '6')
        fqdn = "nothing.nothing.nothing"
        self.do_generic_update(ptr, fqdn, '6')
        fqdn = "google.edu"
        self.do_generic_update(ptr, fqdn, '6')
        fqdn = "bar.oregonstate.edu"
        self.do_generic_update(ptr, fqdn, '6')

    def do_generic_invalid_update(self, ptr, fqdn, ip_type, exception):
        with self.assertRaises(exception):
            self.do_generic_update(ptr, fqdn, ip_type)

    def test_invalid_update_ipv4(self):
        self.create_network_range(network_str='128.3.1.0/24',
                                  start_str='128.3.1.1',
                                  end_str='128.3.1.100')
        ptr = self.do_generic_add("128.3.1.1", "oregonstate.edu", '4')
        ptr2 = self.do_generic_add("128.3.1.2", "oregonstate.edu", '4')
        with self.assertRaises(ValidationError):
            ptr2.ip_str = ptr.ip_str
            ptr2.save()
        fqdn = ".oregonstate.edu "
        self.do_generic_invalid_update(ptr, fqdn, '4', ValidationError)
        fqdn = "asfd..as"
        self.do_generic_invalid_update(ptr, fqdn, '4', ValidationError)
        fqdn = "%.s#.com"
        self.do_generic_invalid_update(ptr, fqdn, '4', ValidationError)

    def test_invalid_update_ipv6(self):
        ptr = self.do_generic_add(
            self.osu_block + ":aa", "oregonstate.edu", '6')
        ptr2 = self.do_generic_add(
            self.osu_block + ":ab", "foo.oregonstate.edu", '6')
        with self.assertRaises(ValidationError):
            ptr2.ip_str = ptr.ip_str
            ptr2.save()
        fqdn = "oregonstate.edu"
        self.do_generic_invalid_update(ptr2, fqdn, '6', ValidationError)
        fqdn = "asfd..as"
        self.do_generic_invalid_update(ptr, fqdn, '6', ValidationError)
        fqdn = "%.s#.com"
        self.do_generic_invalid_update(ptr, fqdn, '6', ValidationError)

    def test_ctnr_range(self):
        """Test that a PTR is allowed only in its IP's range's containers"""

        c2 = Ctnr(name='test_ctnr2')
        c2.save()

        r = self.r
        self.c1.ranges.add(r)

        self.do_generic_add('128.193.0.2', 'www1.oregonstate.edu', '4',
                            ctnr=self.c1)

        with self.assertRaises(ValidationError):
            self.do_generic_add('128.193.0.3', 'www2.oregonstate.edu', '4',
                                ctnr=c2)

    def test_target_existence(self):
        """Test that a PTR's target is not required to exist"""
        self.do_generic_add(
            ip_str='128.193.0.2', fqdn='nonexistent.oregonstate.edu',
            ip_type='4')

    def test_domain_ctnr(self):
        """Test that a PTR's container is independent of its domain's container
        """
        self.c1.domains.add(Domain.objects.get(name='oregonstate.edu'))

        c2 = Ctnr(name='test_ctnr2')
        c2.save()
        c2.ranges.add(self.r)

        self.do_generic_add(
            ip_str='128.193.0.2', fqdn='foo1.oregonstate.edu',
            ip_type='4', ctnr=self.c1)
        self.do_generic_add(
            ip_str='128.193.0.3', fqdn='foo2.oregonstate.edu',
            ip_type='4', ctnr=c2)

    def test_target_resembles_ip(self):
        """Test that a PTR's target cannot resemble an IP address"""
        for fqdn in ('10.234.30.253', '128.193.0.3', 'fe80::e1c9:1:228d:d8'):
            with self.assertRaises(ValidationError):
                self.do_generic_add(ip_str='128.193.0.2', fqdn=fqdn,
                                    ip_type='4')

    def test_same_ip_as_static_intr(self):
        """Test that a PTR and a static inteface cannot share an IP

        (It doesn't matter whether the static interface is enabled.)
        """

        def create_si(dns_enabled):
            s = System(name='test_system')
            s.save()

            i1 = StaticInterface(
                mac='be:ef:fa:ce:12:34', label='foo1',
                domain=Domain.objects.get(name='oregonstate.edu'),
                ip_str='128.193.0.2', ip_type='4', system=s,
                ctnr=self.c1, dns_enabled=dns_enabled)
            i1.save()
            return i1

        create_si_enabled = partial(create_si, True)
        create_si_enabled.name = "StaticInterface with DNS enabled"
        create_si_disabled = partial(create_si, False)
        create_si_disabled.name = "StaticInterface with DNS disabled"

        def create_ptr():
            return self.do_generic_add(
                ip_str='128.193.0.2', ip_type='4', fqdn='foo2.oregonstate.edu')
        create_ptr.name = "PTR"

        self.assertObjectsConflict((create_si_enabled, create_ptr))
        self.assertObjectsConflict((create_si_disabled, create_ptr))

    def test_same_ip(self):
        """Test that two PTRs cannot have the same IP"""
        self.do_generic_add(ip_str='128.193.0.2', ip_type='4',
                            fqdn='foo1.oregonstate.edu')

        with self.assertRaises(ValidationError):
            self.do_generic_add(ip_str='128.193.0.2', ip_type='4',
                                fqdn='foo2.oregonstate.edu')

    def test_ptr_in_dynamic_range(self):
        """Test that the IP cannot be in a dynamic range"""
        self.create_network_range(network_str='128.193.1.0/24',
                                  start_str='128.193.1.2',
                                  end_str='128.193.1.100', range_type='dy')

        with self.assertRaises(ValidationError):
            self.do_generic_add(ip_str='128.193.1.2', ip_type='4',
                                fqdn='foo.oregonstate.edu')
