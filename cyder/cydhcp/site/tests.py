from django.test import TestCase
from django.core.exceptions import ValidationError

from cyder.cydhcp.site.models import Site
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.models import ipv6_to_longs

import random
import ipaddr
import pdb


class SiteTests(TestCase):
    def do_basic_add_network(self, network, prefixlen, ip_type, name=None, number=None, site=None):
        if site:
            s = Network(network_str=network + "/" + prefixlen, ip_type=ip_type, site=site)
        else:
            s = Network(network_str=network + "/" + prefixlen, ip_type=ip_type)
        s.clean()
        s.save()
        self.assertTrue(s)
        return s

    def do_basic_add_site(self, name, parent=None):
        s = Site(name=name, parent=parent)
        s.clean()
        s.save()
        self.assertTrue(s)
        return s

    def test_related_sites(self):
        s1 = self.do_basic_add_site(name="Site 1")
        s2 = self.do_basic_add_site(name="Site 2", parent=s1)
        s3 = self.do_basic_add_site(name="Site 3", parent=s1)
        s4 = self.do_basic_add_site(name="Site 4", parent=s2)
        s5 = self.do_basic_add_site(name="Site 5", parent=s4)
        s6 = self.do_basic_add_site(name="Site 6", parent=s3)
        s7 = self.do_basic_add_site(name="Site 7", parent=s3)
        s8 = self.do_basic_add_site(name="Site 8", parent=s7)
        s9 = self.do_basic_add_site(name="Site 9", parent=s7)
        s10 = self.do_basic_add_site(name="Site 10", parent=s7)
        related_sites = s1.get_related_sites()
        self.assertEqual(set([s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]), related_sites)
        related_sites = s2.get_related_sites()
        self.assertEqual(set([s2, s4, s5]), related_sites)
        related_sites = s3.get_related_sites()
        self.assertEqual(set([s3, s6, s7, s8, s9, s10]), related_sites)
        related_sites = s6.get_related_sites()
        self.assertEqual(set([s6]))
        related_sites = s7.get_related_sites()
        self.assertEqual(set[s7, s8, s9, s10])

    def test_related_networks(self):
        s1 = self.do_basic_add_site(name="Site 1")
        s2 = self.do_basic_add_site(name="Site 2", parent=s1)
        s3 = self.do_basic_add_site(name="Site 3", parent=s1)
        s4 = self.do_basic_add_site(name="Site 4", parent=s2)
        s5 = self.do_basic_add_site(name="Site 5", parent=s4)
        s6 = self.do_basic_add_site(name="Site 6", parent=s3)
        s7 = self.do_basic_add_site(name="Site 7", parent=s3)
        s8 = self.do_basic_add_site(name="Site 8", parent=s7)
        s9 = self.do_basic_add_site(name="Site 9", parent=s7)
        s10 = self.do_basic_add_site(name="Site 10", parent=s7)

        n1 = "123.0.0.0"
        prefixlen = "10"
        kwargs = {'network': network, 'prefixlen': prefixlen, 'ip_type': '4', 'site': s1}
        s = self.do_basic_add_network(**kwargs)

        n2 = "123.0.10.0"
        prefixlen = "20"
        kwargs = {'network': network, 'prefixlen': prefixlen, 'ip_type': '4', 'site': s3}
        s = self.do_basic_add_network(**kwargs)

        n3 = "123.0.10.0"
        prefixlen = "24"
        kwargs = {'network': network, 'prefixlen': prefixlen, 'ip_type': '4', 'site': s7}
        s = self.do_basic_add_network(**kwargs)

        n4 = "123.0.16.0"
        prefixlen = "20"
        kwargs = {'network': network, 'prefixlen': prefixlen, 'ip_type': '4'}
        s = self.do_basic_add_network(**kwargs)

        n5 = "123.0.32.0"
        prefixlen = "20"
        kwargs = {'network': network, 'prefixlen': prefixlen, 'ip_type': '4', 'site': s10}
        s = self.do_basic_add_network(**kwargs)

        n6 = "123.0.32.0"
        prefixlen = "24"
        kwargs = {'network': network, 'prefixlen': prefixlen, 'ip_type': '4'}
        s = self.do_basic_add_network(**kwargs)

        n7 = "123.0.33.0"
        prefixlen = "24"
        kwargs = {'network': network, 'prefixlen': prefixlen, 'ip_type': '4'}
        s = self.do_basic_add_network(**kwargs)

        n8 = "223.0.0.0"
        prefixlen = "10"
        kwargs = {'network': network, 'prefixlen': prefixlen, 'ip_type': '4', 'site': s1}
        s = self.do_basic_add_network(**kwargs)

        n9 = "223.0.10.0"
        prefixlen = "24"
        kwargs = {'network': network, 'prefixlen': prefixlen, 'ip_type': '4'}
        s = self.do_basic_add_network(**kwargs)

        n10 = "223.0.32.0"
        prefixlen = "20"
        kwargs = {'network': network, 'prefixlen': prefixlen, 'ip_type': '4', 'site': s2}
        s = self.do_basic_add_network(**kwargs)

        n11 = "223.0.32.0"
        prefixlen = "24"
        kwargs = {'network': network, 'prefixlen': prefixlen, 'ip_type': '4'}
        s = self.do_basic_add_network(**kwargs)

        n12 = "223.0.33.0"
        prefixlen = "24"
        kwargs = {'network': network, 'prefixlen': prefixlen, 'ip_type': '4', 'site': s4}
        s = self.do_basic_add_network(**kwargs)

        related_networks = s1.get_related_networks()
        self.assertEqual(set([n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, n12]), related_networks)
        related_networks = s3.get_related_networks()
        self.assertEqual(set([n2, n3, n5, n6, n7]), related_networks)
        related_networks = s10.get_related_networks()
        self.assertEqual(set([n5,n6,n7]), related_networks)
        related_networks = s2.get_related_networks()
        self.assertEqual(set([n10, n11, n12]), related_networks)
        related_networks = s4.get_related_networks()
        self.assertEqual(set([n12]), related_networks)
