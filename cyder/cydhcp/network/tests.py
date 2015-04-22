from django.core.exceptions import ValidationError
from nose.plugins.skip import SkipTest

from cyder.base.tests import ModelTestMixin, TestCase
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.validation import get_partial_overlap, get_total_overlap
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.models import ipv6_to_longs


class NetworkTests(TestCase, ModelTestMixin):
    @property
    def objs(self):
        """Create objects for test_create_delete."""
        return (
            Network.objects.create(network_str='10.0.0.0/8', ip_type='4'),
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
        start_upper, start_lower = ipv6_to_longs(
            'ffff:ff00:0000:0000:0000:0000:0000:0000')
        # Network address was canonicalized.
        self.assertEqual(s.start_upper, start_upper)
        self.assertEqual(s.start_lower, start_lower)

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
            network_str='129.0.0.0/24', ip_type='4')

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

    def test_overlap_validation(self):
        n1 = Network(network_str='1::/65', ip_type='6')
        n1.update_network()
        n1.save()
        self.assertFalse(n1 in get_total_overlap(n1))
        self.assertFalse(n1 in get_partial_overlap(n1))

        n2 = Network(network_str='1::/66', ip_type='6')
        n2.update_network()
        self.assertEqual(n1.start_upper, n2.start_upper)
        self.assertEqual(n1.end_upper, n2.end_upper)
        self.assertFalse(n1 in get_total_overlap(n2))
        self.assertTrue(n1 in get_partial_overlap(n2))

        n2 = Network(network_str='1::/64', ip_type='6')
        n2.update_network()
        self.assertEqual(n1.start_upper, n2.start_upper)
        self.assertEqual(n1.end_upper, n2.end_upper)
        self.assertTrue(n1 in get_total_overlap(n2))
        self.assertTrue(n1 in get_partial_overlap(n2))

        n2 = Network(network_str='1:0:0:0:8000::/65', ip_type='6')
        n2.update_network()
        self.assertEqual(n1.start_upper, n2.start_upper)
        self.assertEqual(n1.end_upper, n2.end_upper)
        self.assertFalse(n1 in get_total_overlap(n2))
        self.assertFalse(n1 in get_partial_overlap(n2))

        n1 = Network(network_str='2::/16', ip_type='6')
        n1.update_network()
        n1.save()
        self.assertFalse(n1 in get_total_overlap(n1))
        self.assertFalse(n1 in get_partial_overlap(n1))

        n2 = Network(network_str='2::/17', ip_type='6')
        n2.update_network()
        self.assertEqual(n1.start_upper, n2.start_upper)
        self.assertNotEqual(n1.end_upper, n2.end_upper)
        self.assertFalse(n1 in get_total_overlap(n2))
        self.assertTrue(n1 in get_partial_overlap(n2))

        n2 = Network(network_str='2::/15', ip_type='6')
        n2.update_network()
        self.assertEqual(n1.start_upper, n2.start_upper)
        self.assertNotEqual(n1.end_upper, n2.end_upper)
        self.assertTrue(n1 in get_total_overlap(n2))
        self.assertTrue(n1 in get_partial_overlap(n2))

        n2 = Network(network_str='3::/16', ip_type='6')
        n2.update_network()
        self.assertNotEqual(n1.start_upper, n2.start_upper)
        self.assertNotEqual(n1.end_upper, n2.end_upper)
        self.assertFalse(n1 in get_total_overlap(n2))
        self.assertFalse(n1 in get_partial_overlap(n2))
