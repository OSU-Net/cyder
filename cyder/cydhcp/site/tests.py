from django.test import TestCase

from cyder.cydhcp.site.models import Site
from cyder.cydhcp.network.models import Network


class SiteTests(TestCase):

    def do_basic_add_network(self, network, prefixlen, ip_type,
                             name=None, number=None, site=None):
        s = Network(network_str=network + "/" + prefixlen,
                        ip_type=ip_type, site=site)
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
        self.assertEqual(set([s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]),
                         related_sites)
        related_sites = s2.get_related_sites()
        self.assertEqual(set([s2, s4, s5]), related_sites)
        related_sites = s3.get_related_sites()
        self.assertEqual(set([s3, s6, s7, s8, s9, s10]), related_sites)
        related_sites = s6.get_related_sites()
        self.assertEqual(set([s6]), related_sites)
        related_sites = s7.get_related_sites()
        self.assertEqual(set([s7, s8, s9, s10]), related_sites)

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

        network = "123.0.0.0"
        prefixlen = "10"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4',
                  'site': s1}
        n1 = self.do_basic_add_network(**kwargs)

        network = "123.0.10.0"
        prefixlen = "20"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4',
                  'site': s3}
        n2 = self.do_basic_add_network(**kwargs)

        network = "123.0.10.0"
        prefixlen = "24"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4',
                  'site': s7}
        n3 = self.do_basic_add_network(**kwargs)

        network = "123.0.16.0"
        prefixlen = "20"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4'}
        n4 = self.do_basic_add_network(**kwargs)

        network = "123.0.16.0"
        prefixlen = "21"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4',
                  'site': s10}
        n5 = self.do_basic_add_network(**kwargs)

        network = "123.0.17.0"
        prefixlen = "26"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4'}
        n6 = self.do_basic_add_network(**kwargs)

        network = "123.0.18.0"
        prefixlen = "26"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4'}
        n7 = self.do_basic_add_network(**kwargs)

        network = "223.0.0.0"
        prefixlen = "10"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4',
                  'site': s1}
        n8 = self.do_basic_add_network(**kwargs)

        network = "223.0.10.0"
        prefixlen = "24"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4'}
        n9 = self.do_basic_add_network(**kwargs)

        network = "223.0.32.0"
        prefixlen = "20"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4',
                  'site': s2}
        n10 = self.do_basic_add_network(**kwargs)

        network = "223.0.32.0"
        prefixlen = "24"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4'}
        n11 = self.do_basic_add_network(**kwargs)

        network = "223.0.33.0"
        prefixlen = "24"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4',
                  'site': s4}
        n12 = self.do_basic_add_network(**kwargs)
        related_sites = s1.get_related_sites()
        related_networks = s1.get_related_networks(related_sites)
        self.assertEqual(
                set([n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, n12]),
                related_networks)
        related_sites = s3.get_related_sites()
        related_networks = s3.get_related_networks(related_sites)
        self.assertEqual(set([n2, n3, n5, n6, n7]), related_networks)
        related_sites = s10.get_related_sites()
        related_networks = s10.get_related_networks(related_sites)
        self.assertEqual(set([n5, n6, n7]), related_networks)
        related_sites = s2.get_related_sites()
        related_networks = s2.get_related_networks(related_sites)
        self.assertEqual(set([n10, n11, n12]), related_networks)
        related_sites = s4.get_related_sites()
        related_networks = s4.get_related_networks(related_sites)
        self.assertEqual(set([n12]), related_networks)
