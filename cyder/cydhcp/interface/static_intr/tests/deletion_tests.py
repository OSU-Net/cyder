from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.core.system.models import System

from basestatic import BaseStaticTests


class DeleteStaticInterTests(BaseStaticTests):
    def test1_delete_basic(self):
        # Does deleting a system delete it's interfaces?
        mac = "112233445566"
        label = "foo"
        domain = self.f_c
        ip_str = "10.0.0.2"
        system = System(name='test1_delete_basic')
        system.save()
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str, 'system': system}
        self.do_add_intr(**kwargs)
        self.assertTrue(StaticInterface.objects.filter(**kwargs))
        system.delete()
        self.assertFalse(StaticInterface.objects.filter(**kwargs))
