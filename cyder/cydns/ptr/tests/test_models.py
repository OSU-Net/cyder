from functools import partial

from django.core.exceptions import ValidationError

import cyder.base.tests
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydns.tests.utils import create_basic_dns_data, create_zone
from cyder.cydns.ip.utils import ip_to_reverse_name
from cyder.cydns.domain.models import Domain, boot_strap_ipv6_reverse_domain
from cyder.cydns.ptr.models import PTR
from cyder.cydns.ip.models import Ip
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.vrf.models import Vrf


class PTRTests(cyder.base.tests.TestCase):
    def setUp(self):
        self.ctnr = Ctnr.objects.create(name='abloobloobloo')

        create_basic_dns_data(dhcp=True)

        self._128 = create_zone('128.in-addr.arpa')
        create_zone('8.ip6.arpa')

        self.c1 = Ctnr.objects.create(name='test_ctnr1')

        self.n = Network.objects.create(
            vrf=Vrf.objects.get(name='test_vrf'), ip_type='4',
            network_str='128.193.0.0/24')

        self.r = Range.objects.create(
            network=self.n, range_type='st', start_str='128.193.0.2',
            end_str='128.193.0.100')
        self.c1.ranges.add(self.r)

        for name in ('edu', 'oregonstate.edu', 'bar.oregonstate.edu',
                     'nothing', 'nothing.nothing', 'nothing.nothing.nothing'):
            d = Domain.objects.create(name=name)
            self.c1.domains.add(d)

        boot_strap_ipv6_reverse_domain("8.6.2.0")

        self.osu_block = "8620:105:F000:"
        self.create_network_range(
            network_str="8620:105::/32", start_str='8620:105:F000::1',
            end_str='8620:105:F000::1000', ip_type='6')

    def create_domain(self, name, ip_type='4', delegated=False):
        if name not in ('arpa', 'in-addr.arpa', 'ip6.arpa'):
            name = ip_to_reverse_name(name)
        d = Domain.objects.create(name=name, delegated=delegated)
        self.assertTrue(d.is_reverse)
        return d

    def create_network_range(self, network_str, start_str, end_str,
                             range_type="st", ip_type='4', domain=None):
        if domain is None:
            domain = Domain.objects.get(name="oregonstate.edu")

        n = Network.objects.create(
            vrf=Vrf.objects.get(name='test_vrf'), ip_type=ip_type,
            network_str=network_str)

        r = Range.objects.create(
            network=n, range_type=range_type, start_str=start_str,
            end_str=end_str, domain=domain, ip_type=ip_type)
        self.c1.ranges.add(r)

    def do_generic_add(self, ip_str, fqdn, ip_type, domain=None, ctnr=None):
        if ctnr is None:
            ctnr = self.c1

        ret = PTR.objects.create(
            fqdn=fqdn, ip_str=ip_str, ip_type=ip_type, ctnr=ctnr)

        self.assertTrue(ret.details())

        ip = Ip(ip_str=ip_str, ip_type=ip_type)
        ip.clean_ip()
        ptr = PTR.objects.get(
            fqdn=fqdn, ip_upper=ip.ip_upper, ip_lower=ip.ip_lower)
        ptr.__repr__()
        ip_str = ip_str.lower()
        self.assertEqual(ptr.ip_str, ip_str)
        if domain:
            if ptr.fqdn == '':
                self.assertEqual(fqdn, domain.name)
            else:
                self.assertEqual(fqdn, ptr.fqdn + '.' + domain.name)
        else:
            self.assertEqual(fqdn, ptr.fqdn)
        return ret

    def test_no_domain(self):
        for fqdn in ('lol.foo', 'oregonstate.com', 'me.oregondfastate.edu'):
            self.assertRaises(
                ValidationError, self.do_generic_add,
                ip_str='244.123.123.123', ip_type='4', fqdn=fqdn)

    def test_invalid_name(self):
        ptr_v4 = self.do_generic_add(
            ip_str='128.123.123.99', ip_type='4', fqdn='foo.oregonstate.edu')
        ptr_v6 = self.do_generic_add(
            ip_str=(self.osu_block + ':1'), ip_type='6',
            fqdn='foo.oregonstate.edu')

        bad_fqdns = (
            '2134!@#$!@', 'asdflj..com', 'A' * 257, '.oregonstate.edu',
            '%.s#.com')
        for fqdn in bad_fqdns:
            self.assertRaises(
                ValidationError, self.do_generic_add,
                ip_str='128.123.123.123', ip_type='4', fqdn=fqdn)

            self.assertRaises(
                ValidationError, self.do_generic_update,
                ptr_v4, fqdn=fqdn)

            self.assertRaises(
                ValidationError, self.do_generic_add,
                ip_str=(self.osu_block + ':2'), ip_type='6', fqdn=fqdn)

            self.assertRaises(
                ValidationError, self.do_generic_update,
                ptr_v6, fqdn=fqdn)

    def test_invalid_ip(self):
        ptr_v4 = self.do_generic_add(
            ip_str='128.123.123.99', ip_type='4', fqdn='foo.oregonstate.edu')
        bad_ipv4_ips = (
            '123.123', 'asdfasdf', 32141243, '128.123.123.123.123', '....',
            '1234.', None, False, True)
        for ip_str in bad_ipv4_ips:
            self.assertRaises(
                ValidationError, self.do_generic_add,
                fqdn='oregonstate.edu', ip_str=ip_str, ip_type='4')

            self.assertRaises(
                ValidationError, self.do_generic_update,
                ptr_v4, ip_str=ip_str)

        ptr_v6 = self.do_generic_add(
            ip_str=(self.osu_block + ':1'), ip_type='6',
            fqdn='foo.oregonstate.edu')
        bad_ipv6_ips = (
            '123.123.123.123.', '123:!23:!23:', ':::', None, True, False,
            lambda x: x, '8::9:9:1', '11:9:9::1', '8.9.9.1', '11.9.9.1')
        for ip_str in bad_ipv6_ips:
            self.assertRaises(
                ValidationError, self.do_generic_add,
                ip_str=ip_str, fqdn='oregonstate.edu', ip_type='6')

            self.assertRaises(
                ValidationError, self.do_generic_update,
                ptr_v6, ip_str=ip_str)

    def test_no_reverse_domain(self):
        self.assertRaises(
            ValidationError, self.do_generic_add,
            fqdn='oregonstate.edu', ip_str='8.9.9.1', ip_type='4')
        self.assertRaises(
            ValidationError, self.do_generic_add,
            fqdn='oregonstate.edu', ip_str='11.9.9.1', ip_type='4')

    def do_generic_remove(self, ip_str, fqdn, ip_type):
        ptr = PTR.objects.create(
            ip_str=ip_str, fqdn=fqdn, ip_type=ip_type, ctnr=self.c1)

        ptr.delete()

        ip = Ip(ip_str=ip_str, ip_type=ip_type)
        ip.clean_ip()
        self.assertFalse(PTR.objects.filter(
            fqdn=fqdn, ip_upper=ip.ip_upper, ip_lower=ip.ip_lower).exists())

    def test_remove_ipv4(self):
        self.create_network_range(
            network_str='128.255.1.0/16', start_str='128.255.1.1',
            end_str='128.255.233.254')

        self.do_generic_remove(
            ip_str='128.255.233.244', ip_type='4',
            fqdn='asdf34foo.bar.oregonstate.edu')
        self.do_generic_remove(
            ip_str='128.255.11.13', ip_type='4',
            fqdn='fo124kfasdfko.bar.oregonstate.edu')
        self.do_generic_remove(
            ip_str='128.255.9.1', ip_type='4',
            fqdn='or1fdsaflkegonstate.edu')
        self.do_generic_remove(
            ip_str='128.255.1.7', ip_type='4',
            fqdn='12.bar.oregonstate.edu')
        self.do_generic_remove(
            ip_str='128.255.1.3', ip_type='4',
            fqdn='fcwoo.bar.oregonstate.edu')
        self.do_generic_remove(
            ip_str='128.255.1.2', ip_type='4',
            fqdn='asffad124jfasf-oregonstate.edu')

    def test_remove_ipv6(self):
        self.do_generic_remove(
            ip_str=(self.osu_block + ":1"), ip_type='6',
            fqdn='asdf34foo.bar.oregonstate.edu')
        self.do_generic_remove(
            ip_str=(self.osu_block + ":2"), ip_type='6',
            fqdn='fo124kfasdfko.bar.oregonstate.edu')
        self.do_generic_remove(
            ip_str=(self.osu_block + ":8"), ip_type='6',
            fqdn='or1fdsaflkegonstate.edu')
        self.do_generic_remove(
            ip_str=(self.osu_block + ":8"), ip_type='6',
            fqdn='12.bar.oregonstate.edu')
        self.do_generic_remove(
            ip_str=(self.osu_block + ":20"), ip_type='6',
            fqdn='fcwoo.bar.oregonstate.edu')
        self.do_generic_remove(
            ip_str=(self.osu_block + ":ad"), ip_type='6',
            fqdn='asffad124jfasf-oregonstate.edu')

    def do_generic_update(self, ptr, fqdn=None, ip_str=None):
        if fqdn is not None:
            ptr.fqdn = fqdn
        if ip_str is not None:
            ptr.ip_str = ip_str
        ptr.save()

        db_ptr = PTR.objects.get(
            fqdn=ptr.fqdn, ip_upper=ptr.ip_upper, ip_lower=ptr.ip_lower)
        self.assertEqual(ptr.fqdn, db_ptr.fqdn)
        self.assertEqual(ptr.ip_str, db_ptr.ip_str)

    def test_update_ipv4(self):
        self.create_network_range(
            network_str='128.193.1.0/24', start_str='128.193.1.1',
            end_str='128.193.1.100')

        ptr = self.do_generic_add(
            ip_str='128.193.1.1', ip_type='4', fqdn='oregonstate.edu')

        self.do_generic_update(ptr, fqdn='nothing.nothing.nothing')
        self.do_generic_update(ptr, fqdn='google.edu')
        self.do_generic_update(ptr, fqdn='bar.oregonstate.edu')

    def test_update_ipv6(self):
        ptr = self.do_generic_add(
            ip_str=(self.osu_block + ':1'), ip_type='6',
            fqdn='oregonstate.edu')

        self.do_generic_update(ptr, fqdn="nothing.nothing.nothing")
        self.do_generic_update(ptr, fqdn="google.edu")
        self.do_generic_update(ptr, fqdn="bar.oregonstate.edu")

    def test_ctnr_range(self):
        """Test that a PTR is allowed only in its IP's range's containers"""

        c2 = Ctnr.objects.create(name='test_ctnr2')

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

        c2 = Ctnr.objects.create(name='test_ctnr2')
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
            s = System.objects.create(name='test_system')
            return StaticInterface.objects.create(
                mac='be:ef:fa:ce:12:34', label='foo1',
                domain=Domain.objects.get(name='oregonstate.edu'),
                ip_str='128.193.0.2', ip_type='4', system=s,
                ctnr=self.c1, dns_enabled=dns_enabled)

        create_si_enabled = partial(create_si, True)
        create_si_enabled.name = "StaticInterface with DNS enabled"
        create_si_disabled = partial(create_si, False)
        create_si_disabled.name = "StaticInterface with DNS disabled"

        def create_ptr():
            return self.do_generic_add(
                ip_str='128.193.0.2', ip_type='4', fqdn='foo2.oregonstate.edu')
        create_ptr.name = 'PTR'

        self.assertObjectsConflict((create_si_enabled, create_ptr))
        self.assertObjectsConflict((create_si_disabled, create_ptr))

    def test_same_ip(self):
        """Test that two PTRs cannot have the same IP"""
        self.do_generic_add(
            ip_str='128.193.0.2', ip_type='4', fqdn='foo1.oregonstate.edu')

        with self.assertRaises(ValidationError):
            self.do_generic_add(
                ip_str='128.193.0.2', ip_type='4', fqdn='foo2.oregonstate.edu')

    def test_ptr_in_dynamic_range(self):
        """Test that the IP cannot be in a dynamic range"""
        self.create_network_range(
            network_str='128.193.1.0/24', start_str='128.193.1.2',
            end_str='128.193.1.100', range_type='dy')

        with self.assertRaises(ValidationError):
            self.do_generic_add(
                ip_str='128.193.1.2', ip_type='4', fqdn='foo.oregonstate.edu')
