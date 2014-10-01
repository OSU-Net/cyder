from django.test import TestCase

from cyder.cydhcp.site.models import Site
from cyder.cydhcp.network.models import Network


class SiteTests(TestCase):
    def do_basic_add_network(self, network, prefixlen, ip_type,
                             name=None, number=None, site=None):
        return Network.objects.create(
            network_str=network + "/" + prefixlen, ip_type=ip_type, site=site)

    def do_basic_add_site(self, name, parent=None):
        return Site.objects.create(name=name, parent=parent)

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

        self.assertEqual(
            {s1, s2, s3, s4, s5, s6, s7, s8, s9, s10}, s1.get_related_sites())

        self.assertEqual({s2, s4, s5}, s2.get_related_sites())

        self.assertEqual({s3, s6, s7, s8, s9, s10}, s3.get_related_sites())

        self.assertEqual({s6}, s6.get_related_sites())

        self.assertEqual({s7, s8, s9, s10}, s7.get_related_sites())

    def test_related_networks(self):
        s1 = self.do_basic_add_site(name="Site 1")
        s2 = self.do_basic_add_site(name="Site 2", parent=s1)
        s3 = self.do_basic_add_site(name="Site 3", parent=s1)
        s4 = self.do_basic_add_site(name="Site 4", parent=s2)
        s7 = self.do_basic_add_site(name="Site 7", parent=s3)
        s10 = self.do_basic_add_site(name="Site 10", parent=s7)

        n1 = Network.objects.create(
            network_str="123.0.0.0/10",
            ip_type='4',
            site=s1,
        )

        n2 = Network.objects.create(
            network_str="123.0.10.0/20",
            ip_type='4',
            site=s3,
        )

        n3 = Network.objects.create(
            network_str="123.0.10.0/24",
            ip_type='4',
            site=s7,
        )

        n4 = Network.objects.create(
            network_str="123.0.16.0/20",
            ip_type='4',
        )

        n5 = Network.objects.create(
            network_str="123.0.16.0/21",
            ip_type='4',
            site=s10,
        )

        n6 = Network.objects.create(
            network_str="123.0.17.0/26",
            ip_type='4',
        )

        n7 = Network.objects.create(
            network_str="123.0.18.0/26",
            ip_type='4',
        )

        n8 = Network.objects.create(
            network_str="223.0.0.0/10",
            ip_type='4',
            site=s1,
        )

        n9 = Network.objects.create(
            network_str="223.0.10.0/24",
            ip_type='4',
        )

        n10 = Network.objects.create(
            network_str="223.0.32.0/20",
            ip_type='4',
            site=s2,
        )

        n11 = Network.objects.create(
            network_str="223.0.32.0/24",
            ip_type='4',
        )

        n12 = Network.objects.create(
            network_str="223.0.33.0/24",
            ip_type='4',
            site=s4,
        )

        self.assertEqual(
            {n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, n12},
            s1.get_related_networks(s1.get_related_sites()))

        self.assertEqual(
            {n2, n3, n5, n6, n7},
            s3.get_related_networks(s3.get_related_sites()))

        self.assertEqual(
            {n5, n6, n7}, s10.get_related_networks(s10.get_related_sites()))

        self.assertEqual(
            {n10, n11, n12}, s2.get_related_networks(s2.get_related_sites()))

        self.assertEqual(
            {n12}, s4.get_related_networks(s4.get_related_sites()))
