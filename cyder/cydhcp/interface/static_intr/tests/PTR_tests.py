from django.core.exceptions import ValidationError

from cyder.cydns.ptr.models import PTR
from .basestatic import BaseStaticTests


class PTRStaticRegTests(BaseStaticTests):
    def test_conflict_add_intr_first(self):
        # Make sure static interface conflicts with PTR.
        def create_intr():
            return self.create_si(
                mac='11:22:33:44:55:66',
                label='foo4',
                domain=self.f_c,
                ip_str='10.0.0.2',
            )
        create_intr.name = 'StaticInterface'

        def create_ptr():
            return PTR.objects.create(
                ip_str='10.0.0.2', fqdn='foo4.foo.ccc',
                ctnr=self.ctnr)
        create_ptr.name = 'PTR'

        self.assertObjectsConflict((create_intr, create_ptr))

    def test_conflict_add_intr_first(self):
        self.create_si(
            mac='12:22:33:44:55:66',
            label='fo99',
            domain=self.f_c,
            ip_str='10.0.0.2',
        )

        ptr = PTR.objects.create(
            ip_str='10.0.0.3',
            fqdn='fo99.foo.ccc',
            ctnr=self.ctnr,
        )

        ptr.ip_str = '10.0.0.2'
        self.assertRaises(ValidationError, ptr.save)  # IP conflict

    def test_conflict_add_A_first(self):
        PTR.objects.create(
            fqdn='foo98.foo.ccc',
            ip_str='10.0.0.2',
            ctnr=self.ctnr,
        )

        intr = self.create_si(
            mac='11:22:33:44:55:66',
            label='foo98',
            domain=self.f_c,
            ip_str='10.0.0.3',
        )

        intr.ip_str = '10.0.0.2'
        self.assertRaises(ValidationError, intr.save)  # IP conflict
