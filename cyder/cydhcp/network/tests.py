from django.core.exceptions import ValidationError
from nose.plugins.skip import SkipTest

from cyder.base.tests import ModelTestMixin, TestCase
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.models import ipv6_to_longs


class NetworkTests(TestCase, ModelTestMixin):
    @property
    def objs(self):
        """Create objects for test_create_delete."""
        return (
            Network.objects.create(network_str='10.0.0.0/8', ip_type='4'),
            Network.objects.create(network_str='10.0.0.0/16', ip_type='4'),
            Network.objects.create(network_str='10.0.0.0/17', ip_type='4'),
            Network.objects.create(network_str='192.168.0.0/24', ip_type='4'),
            Network.objects.create(network_str='192.168.128.0/25',
                ip_type='4'),
            Network.objects.create(network_str='abcd::1234/126', ip_type='6'),
            Network.objects.create(network_str='f::/24', ip_type='6'),
        )

    def test2_create_ipv6(self):
        s = Network.objects.create(
            network_str='ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/24',
            ip_type='6')
        str(s)
        s.__repr__()
        ip_upper, ip_lower = ipv6_to_longs(
            'ffff:ff00:0000:0000:0000:0000:0000:0000')
        # Network address was canonicalized.
        self.assertEqual(s.ip_upper, ip_upper)
        self.assertEqual(s.ip_lower, ip_lower)

    def test_bad_resize(self):
        s = Network.objects.create(network_str='129.0.0.0/24', ip_type='4')

        d = Domain(name="asdf")
        d.save()

        r = Range.objects.create(
            start_str='129.0.0.1', end_str='129.0.0.255', network=s)

        self.assertEqual(r.network, s)
        self.assertEqual(s.range_set.count(), 1)

        s.network_str = '129.0.0.0/25'
        self.assertRaises(ValidationError, s.save)

    def test_bad_delete(self):
        s = Network.objects.create(
            network_str='129.0.0.0/24', prefixlen='24', ip_type='4')

        d = Domain.objects.create(name="asdf")

        r = Range.objects.create(
            start_str='129.0.0.1', end_str='129.0.0.255', network=s)

        self.assertEqual(r.network, s)
        self.assertEqual(s.range_set.count(), 1)

        self.assertRaises(ValidationError, s.delete)
        self.assertTrue(Network.objects.filter(pk=s.pk).exists())

        r.delete()
        s_pk = s.pk
        s.delete()
        self.assertFalse(Network.objects.filter(pk=s_pk).exists())

    def test_get_related_networks(self):
        s1 = Network.objects.create(network_str='129.0.0.1/20')
        s2 = Network.objects.create(network_str='129.0.2.1/25')
        s3 = Network.objects.create(network_str='129.0.4.1/29')
        s4 = Network.objects.create(network_str='129.0.2.1/29')

        self.assertEqual(set(s1.get_related_networks()), {s1, s2, s3, s4})

    def test_get_related_sites(self):
        s1 = Site.objects.create(name='Kerr')
        s2 = Site.objects.create(name='Business', parent=s1)
        s3 = Site.objects.create(name='Registration', parent=s1)

        n1 = Network.objects.create(network_str='129.0.0.0/19', site=s1)
        n2 = Network.objects.create(network_str='129.0.1.0/24', site=s2)
        n3 = Network.objects.create(network_str='129.0.1.0/22', site=s3)
        n4 = Network.objects.create(network_str='129.0.1.0/25')

        self.assertEqual(set(n1.get_related_networks()), {n1, n2, n3, n4})

        """
        TODO:

        if we choose s1 as a site then s2, s3, n1, n2, n3, and n4 are returned
        if we choose n2 then n3 and n4 should be returned
        if we choose s3 then n2, n3, and n4 should be returned
        """

    def test_parent_children_descendants(self):
        n1 = Network.objects.create(network_str='10.0.0.0/8')
        n2 = Network.objects.create(network_str='10.0.0.0/14')
        n3 = Network.objects.create(network_str='10.1.0.0/16')
        n4 = Network.objects.create(network_str='10.1.244.0/23')
        n5 = Network.objects.create(network_str='10.1.245.0/24')
        n6 = Network.objects.create(network_str='10.2.0.0/16')

        self.assertEqual(n1.parent, None)
        self.assertEqual(n2.parent, n1)
        self.assertEqual(n3.parent, n2)
        self.assertEqual(n4.parent, n3)
        self.assertEqual(n5.parent, n4)
        self.assertEqual(n6.parent, n2)

        self.assertEqual(set(n1.children), {n2})
        self.assertEqual(set(n2.children), {n3, n6})
        self.assertEqual(set(n3.children), {n4})
        self.assertEqual(set(n4.children), {n5})
        self.assertEqual(set(n5.children), set())
        self.assertEqual(set(n6.children), set())

        self.assertEqual(set(n1.descendants), {n2, n3, n4, n5, n6})
        self.assertEqual(set(n2.descendants), {n3, n4, n5, n6})
        self.assertEqual(set(n3.descendants), {n4, n5})
        self.assertEqual(set(n4.descendants), {n5})
        self.assertEqual(set(n5.descendants), set())
        self.assertEqual(set(n6.descendants), set())

    def test_check_valid_ranges_v4_valid(self):
        n = Network(network_str='10.0.0.0/8')
        n.full_clean()
        n.save()

        r = Range(ip_type='4', start_str='10.4.0.2', end_str='10.4.255.254',
                  network=n)
        r.full_clean()
        r.save()

        n.network_str = '10.4.0.0/16'
        n.full_clean()
        n.save()

    def test_check_valid_ranges_v4_start_low(self):
        n = Network(network_str='10.0.0.0/8')
        n.full_clean()
        n.save()

        r = Range(ip_type='4', start_str='10.3.0.2', end_str='10.4.255.254',
                  network=n)
        r.full_clean()
        r.save()

        n.network_str = '10.4.0.0/16'
        with self.assertRaises(ValidationError):
            n.full_clean()
            n.save()

    def test_check_valid_ranges_v4_start_end_low(self):
        n = Network(network_str='10.0.0.0/8')
        n.full_clean()
        n.save()

        r = Range(ip_type='4', start_str='10.3.0.2', end_str='10.3.255.254',
                  network=n)
        r.full_clean()
        r.save()

        n.network_str = '10.4.0.0/16'
        with self.assertRaises(ValidationError):
            n.full_clean()
            n.save()

    def test_check_valid_ranges_v4_end_high(self):
        n = Network(network_str='10.0.0.0/8')
        n.full_clean()
        n.save()

        r = Range(ip_type='4', start_str='10.4.0.2', end_str='10.5.255.254',
                  network=n)
        r.full_clean()
        r.save()

        n.network_str = '10.4.0.0/16'
        with self.assertRaises(ValidationError):
            n.full_clean()
            n.save()

    def test_check_valid_ranges_v4_start_end_high(self):
        n = Network(network_str='10.0.0.0/8')
        n.full_clean()
        n.save()

        r = Range(ip_type='4', start_str='10.5.0.2', end_str='10.5.255.254',
                  network=n)
        r.full_clean()
        r.save()

        n.network_str = '10.4.0.0/16'
        with self.assertRaises(ValidationError):
            n.full_clean()
            n.save()

    def test_check_valid_ranges_v4_start_low_end_high(self):
        n = Network(network_str='10.0.0.0/8')
        n.full_clean()
        n.save()

        r = Range(ip_type='4', start_str='10.3.0.2', end_str='10.5.255.254',
                network=n)
        r.full_clean()
        r.save()

        n.network_str = '10.4.0.0/16'
        with self.assertRaises(ValidationError):
            n.full_clean()
            n.save()
