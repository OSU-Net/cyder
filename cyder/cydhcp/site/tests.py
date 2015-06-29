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
