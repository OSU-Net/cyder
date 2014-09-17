from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.core.system.models import System

from basestatic import BaseStaticTests


class DeleteStaticInterTests(BaseStaticTests):
    def test1_delete_basic(self):
        # Deleting a system should delete its interfaces.
        system = System(name='test1_delete_basic')
        system.save()

        kwargs = {
            'mac': "112233445566",
            'label': "foo",
            'domain': self.f_c,
            'ip_str': "10.0.0.2",
            'system': system,
        }
        self.do_add_intr(**kwargs)
        self.assertTrue(StaticInterface.objects.filter(**kwargs))

        system.delete()
        self.assertFalse(StaticInterface.objects.filter(**kwargs))
