from cyder.base.tests import ModelTestMixin, TestCase
from cyder.cydhcp.vlan.models import Vlan


class VlanTests(TestCase, ModelTestMixin):
    @property
    def objs(self):
        """Create objects for test_create_delete."""
        return (
            Vlan.objects.create(number=1, name='a'),
            Vlan.objects.create(number=3, name='bbbbbbbbbbb'),
            Vlan.objects.create(number=666, name='Hello, world.'),
        )
