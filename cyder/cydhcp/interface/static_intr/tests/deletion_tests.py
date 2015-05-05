from django.core.exceptions import ValidationError
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.core.system.models import System

from basestatic import BaseStaticTests


class DeleteStaticInterTests(BaseStaticTests):
    def test_delete_basic(self):
        # Deleting a system should delete its interfaces.
        system = System.objects.create(name='test_delete_basic',
                                       ctnr=self.ctnr)

        i = self.create_si(
            mac='112233445566',
            label='foo',
            domain=self.f_c,
            ip_str='10.0.0.2',
            system=system,
        )
        self.assertTrue(StaticInterface.objects.filter(pk=i.pk).exists())

        system.delete()
        self.assertFalse(StaticInterface.objects.filter(pk=i.pk).exists())

    def test_cant_delete_range(self):
        i = self.create_si(
            mac="15:22:33:44:55:66",
            label="8888foo",
            domain=self.f_c,
            ip_str="10.0.0.1",
        )
        r = i.range
        self.assertRaises(ValidationError, r.delete)
        i.delete()
        r.delete()
