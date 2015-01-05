from django.core.exceptions import ValidationError

from cyder.cydns.address_record.models import AddressRecord
from .basestatic import BaseStaticTests


class AStaticRegTests(BaseStaticTests):
    def test_conflict(self):
        # Add an intr and make sure A can't exist.
        label = "foo4"
        domain = self.f_c
        ip_str = "10.0.0.2"

        def i():
            return self.create_si(
                mac="11:22:33:44:55:66",
                label=label,
                domain=domain,
                ip_str=ip_str,
            )
        i.name = 'StaticInterface'

        def a():
            return AddressRecord.objects.create(
                label=label,
                domain=domain,
                ip_str=ip_str,
                ctnr=self.ctnr,
            )
        a.name = 'AddressRecord'

        self.assertObjectsConflict((i, a))

    def test_conflict_add_intr_first(self):
        # Add an intr and update an existing A to conflict. Test for exception.
        label = "fo99"
        domain = self.f_c

        self.create_si(
            mac="12:22:33:44:55:66",
            label=label,
            domain=domain,
            ip_str='10.0.0.2',
        )

        a = AddressRecord.objects.create(
            label=label,
            domain=domain,
            ip_str='10.0.0.3',
            ctnr=self.ctnr,
        )

        a.ip_str = "10.0.0.2"
        self.assertRaises(ValidationError, a.save)

    def test_conflict_add_A_first(self):
        # Add an A and update and existing intr to conflict. Test for
        # exception.
        label = "foo98"
        domain = self.f_c

        AddressRecord.objects.create(
            label=label,
            domain=domain,
            ip_str='10.0.0.2',
            ctnr=self.ctnr,
        )

        intr = self.create_si(
            mac="11:22:33:44:55:66",
            label=label,
            domain=domain,
            ip_str='10.0.0.3',
        )

        intr.ip_str = "10.0.0.2"
        self.assertRaises(ValidationError, intr.save)
