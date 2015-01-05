from cyder.base.tests import ModelTestMixin, TestCase
from cyder.cydhcp.workgroup.models import Workgroup


class WorkgroupTests(TestCase, ModelTestMixin):
    @property
    def objs(self):
        """Create objects for test_create_delete."""
        return (
            Workgroup.objects.create(name='a'),
            Workgroup.objects.create(name='bbbbbbbbbbbbbb'),
            Workgroup.objects.create(name='Hello, world.'),
        )
