from cyder.base.tests import ModelTestMixin, TestCase
from cyder.cydhcp.vrf.models import Vrf


class VrfTests(TestCase, ModelTestMixin):
    @property
    def objs(self):
        """Create objects for test_create_delete."""
        return (
            Vrf.objects.create(name='a'),
            Vrf.objects.create(name='bbbbbbbbbbbbb'),
            Vrf.objects.create(name='Hello, world.'),
        )
