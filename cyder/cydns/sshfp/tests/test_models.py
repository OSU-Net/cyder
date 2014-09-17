from django.core.exceptions import ValidationError

import cyder.base.tests
from cyder.core.ctnr.models import Ctnr
from cyder.cydns.sshfp.models import SSHFP
from cyder.cydns.domain.models import Domain
from cyder.core.ctnr.models import Ctnr


class SSHFPTests(cyder.base.tests.TestCase):
    def setUp(self):
        self.ctnr = Ctnr(name='abloobloobloo')
        self.ctnr.save()
        self.o = Domain(name="org")
        self.o.save()
        self.o_e = Domain(name="mozilla.org")
        self.o_e.save()
        self.ctnr.domains.add(self.o)
        self.ctnr.domains.add(self.o_e)

    def do_generic_add(self, **data):
        data['ctnr'] = self.ctnr
        sshfp = SSHFP(**data)
        sshfp.save()
        sshfp.__repr__()
        self.assertTrue(sshfp.details())
        rsshfp = SSHFP.objects.filter(**data)
        self.assertEqual(rsshfp.count(), 1)
        return sshfp

    def do_remove(self, **data):
        sshfp = self.do_generic_add(**data)
        sshfp.delete()
        rmx = SSHFP.objects.filter(**data)
        self.assertTrue(len(rmx) == 0)

    def test_add_remove_sshfp(self):
        self.do_generic_add(
            label="asdf",
            domain=self.o_e,
            key="7d97e98f8af710c7e7fe703abc8f639e0ee507c4",
            fingerprint_type=1,
            algorithm_number=1,
        )

        self.do_generic_add(
            label="asdf2",
            domain=self.o_e,
            key="8d97e98f8af710c7e7fe703abc8f639e0ee507c4",
            fingerprint_type=1,
            algorithm_number=1,
        )

        self.do_generic_add(
            label="df",
            domain=self.o_e,
            key="8d97e98f8af710c7e7fe703abc8f639e0ee507c4",
            fingerprint_type=1,
            algorithm_number=1,
        )

        self.do_generic_add(
            label="12314",
            domain=self.o_e,
            key="8d97e98f8af710c7e7fe703abc8f639e0ee507c4",
            fingerprint_type=1,
            algorithm_number=1,
        )

    def test_domain_ctnr(self):
        key = '8d97e98f8af710c7e7fe703abc8f639e0ee507c4'

        ctnr1 = Ctnr(name='test_ctnr1')
        ctnr1.save()
        ctnr1.domains.add(self.o_e)

        SSHFP.objects.create(
            label='foo',
            domain=self.o_e,
            key=key,
            algorithm_number=1,
            fingerprint_type=1,
            ctnr=ctnr1,
        )

        ctnr2 = Ctnr(name='test_ctnr2')
        ctnr2.save()

        self.assertRaises(ValidationError, SSHFP.objects.create,
            label='bleh',
            domain=self.o_e,
            key=key,
            algorithm_number=1,
            fingerprint_type=1,
            ctnr=ctnr2,
        )

    def test_name_unique(self):
        """Test that two SSHFPs cannot share a name"""

        SSHFP.objects.create(
            label='foo',
            domain=self.o_e,
            key='7d97e98f8af710c7e7fe703abc8f639e0ee507c4',
            algorithm_number=1,
            fingerprint_type=1,
            ctnr=self.ctnr)

        self.assertRaises(ValidationError, SSHFP.objects.create,
            label='foo',
            domain=self.o_e,
            key='8d97e98f8af710c7e7fe703abc8f639e0ee507c4',
            algorithm_number=1,
            fingerprint_type=1,
            ctnr=self.ctnr)
