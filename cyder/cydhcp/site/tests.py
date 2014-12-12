from cyder.base.tests import ModelTestMixin, TestCase
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.network.models import Network


class SiteTests(TestCase, ModelTestMixin):
    @property
    def objs(self):
        """Create objects for test_create_delete."""
        return (
            Site.objects.create(name='a'),
            Site.objects.create(name='bbbbbbbbbbbbbbbbbb'),
            Site.objects.create(name='c-c-c'),
            Site.objects.create(name='100'),
            Site.objects.create(name='Hello, world.'),
        )

    def test_related_sites(self):
        s1 = Site.objects.create(name="Site 1")
        s2 = Site.objects.create(name="Site 2", parent=s1)
        s3 = Site.objects.create(name="Site 3", parent=s1)
        s4 = Site.objects.create(name="Site 4", parent=s2)
        s5 = Site.objects.create(name="Site 5", parent=s4)
        s6 = Site.objects.create(name="Site 6", parent=s3)
        s7 = Site.objects.create(name="Site 7", parent=s3)
        s8 = Site.objects.create(name="Site 8", parent=s7)
        s9 = Site.objects.create(name="Site 9", parent=s7)
        s10 = Site.objects.create(name="Site 10", parent=s7)

        self.assertEqual(
            {s1, s2, s3, s4, s5, s6, s7, s8, s9, s10}, s1.get_related_sites())

        self.assertEqual({s2, s4, s5}, s2.get_related_sites())

        self.assertEqual({s3, s6, s7, s8, s9, s10}, s3.get_related_sites())

        self.assertEqual({s6}, s6.get_related_sites())

        self.assertEqual({s7, s8, s9, s10}, s7.get_related_sites())

    def test_related_networks(self):
        s1 = Site.objects.create(name="Site 1")
        s2 = Site.objects.create(name="Site 2", parent=s1)
        s3 = Site.objects.create(name="Site 3", parent=s1)
        s4 = Site.objects.create(name="Site 4", parent=s2)
        s7 = Site.objects.create(name="Site 7", parent=s3)
        s10 = Site.objects.create(name="Site 10", parent=s7)

        n1 = Network.objects.create(network_str="123.0.0.0/10", site=s1)
        n2 = Network.objects.create(network_str="123.0.10.0/20", site=s3)
        n3 = Network.objects.create(network_str="123.0.10.0/24", site=s7)
        n4 = Network.objects.create(network_str="123.0.16.0/20")
        n5 = Network.objects.create(network_str="123.0.16.0/21", site=s10)
        n6 = Network.objects.create(network_str="123.0.17.0/26")
        n7 = Network.objects.create(network_str="123.0.18.0/26")
        n8 = Network.objects.create(network_str="223.0.0.0/10", site=s1)
        n9 = Network.objects.create(network_str="223.0.10.0/24")
        n10 = Network.objects.create(network_str="223.0.32.0/20", site=s2)
        n11 = Network.objects.create(network_str="223.0.32.0/24")
        n12 = Network.objects.create(network_str="223.0.33.0/24", site=s4)

        self.assertEqual(
            {n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, n12},
            Site.get_related_networks(s1.get_related_sites()))

        self.assertEqual(
            {n2, n3, n5, n6, n7},
            Site.get_related_networks(s3.get_related_sites()))

        self.assertEqual(
            {n5, n6, n7}, Site.get_related_networks(s10.get_related_sites()))

        self.assertEqual(
            {n10, n11, n12}, Site.get_related_networks(s2.get_related_sites()))

        self.assertEqual(
            {n12}, Site.get_related_networks(s4.get_related_sites()))
