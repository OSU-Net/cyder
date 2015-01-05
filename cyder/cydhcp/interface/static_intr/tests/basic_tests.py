from django.core.exceptions import ValidationError
from functools import partial

from cyder.base.tests import ModelTestMixin
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.ptr.models import PTR

from basestatic import BaseStaticTests


class StaticInterTests(BaseStaticTests, ModelTestMixin):
    @property
    def objs(self):
        """Create objects for test_create_delete."""
        return (
            self.create_si(
                mac="11:22:33:44:55:66", label="foo0", domain=self.f_c,
                ip_str="10.0.0.2"),
            self.create_si(
                mac="22:33:44:DD:ee:Ff", label="foo1", domain=self.f_c,
                ip_str="10.0.0.3"),
            self.create_si(
                mac="00:00:00:00:00:01", label="foo2", domain=self.f_c,
                ip_str="10.0.0.4"),
            self.create_si(
                mac="00:00:00:00:00:02", label="foo3", domain=self.f_c,
                ip_str="10.0.0.5"),
        )

    def test_update(self):
        i = self.create_si(
            mac="11:22:33:44:55:66",
            label="foo1",
            domain=self.f_c,
            ip_str="10.0.0.1",
        )

        i.dhcp_enabled = False
        i.save()
        self.assertFalse(i.reload().dhcp_enabled)

        i.dhcp_enabled = True
        i.save()
        self.assertTrue(i.reload().dhcp_enabled)

    def test_dup_create_basic(self):
        def x():
            self.create_si(
                mac="11:22:33:44:55:66",
                label="foo3",
                domain=self.f_c,
                ip_str="10.0.0.2",
            )

        x()

        self.assertRaises(ValidationError, x)

    def test_bad_add_for_a_ptr(self):
        # Intr exists, then try PTR and A
        self.create_si(
            mac="11:22:33:44:55:66", label='9988food', domain=self.c,
            ip_str='10.0.0.1')

        self.assertRaises(
            ValidationError, AddressRecord.objects.create,
            label='9988food', domain=self.c, ip_str='10.0.0.1', ip_type='4',
            ctnr=self.ctnr)

        self.assertRaises(
            ValidationError, PTR.objects.create,
            fqdn='9988food.ccc', ip_str='10.0.0.1', ip_type='4',
            ctnr=self.ctnr)

    def test_bad_add_for_a_ptr2(self):
        # PTR and A exist, then try add intr
        AddressRecord.objects.create(
            label='9988food', domain=self.c, ip_str='10.0.0.1', ip_type='4',
            ctnr=self.ctnr)

        PTR.objects.create(
            fqdn='9988food.ccc', ip_str='10.0.0.1', ip_type='4',
            ctnr=self.ctnr)

        self.assertRaises(
            ValidationError, self.create_si,
            mac="11:22:33:44:55:66", label='9988food', domain=self.c,
            ip_str='10.0.0.1')

    def test_bad_reverse_domain(self):
        i = self.create_si(
            mac="11:22:33:44:55:66",
            label="8888foo",
            domain=self.f_c,
            ip_str="10.0.0.1",
        )

        i.ip_str = "9.0.0.1"
        self.assertRaises(ValidationError, i.save)

    def test_no_system(self):
        self.assertRaises(
            ValueError, StaticInterface.objects.create,
            mac="15:22:33:44:55:66",
            label="8888foo",
            domain=self.f_c,
            ip_str="10.0.0.1",
            ip_type='4',
            system=None,
            ctnr=self.ctnr,
        )

    def test_has_range(self):
        i = self.create_si(
            mac="15:22:33:44:55:66",
            label="8888foo",
            domain=self.f_c,
            ip_str="10.0.0.1",
        )

        i.ip_str = "10.0.0.20"
        self.assertRaises(ValidationError, i.save)
        i.dhcp_enabled = False
        i.save()
