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
        sshfp.full_clean()
        sshfp.__repr__()
        sshfp.save()
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
        label = "asdf"
        key = "7d97e98f8af710c7e7fe703abc8f639e0ee507c4"
        s_type = 1
        a_type = 1
        data = {'label': label, 'key': key, 'domain': self.o_e,
                'algorithm_number': a_type, 'fingerprint_type': s_type}
        self.do_generic_add(**data)

        label = "asdf2"
        key = "8d97e98f8af710c7e7fe703abc8f639e0ee507c4"
        s_type = 1
        a_type = 1
        data = {'label': label, 'key': key, 'domain': self.o_e,
                'algorithm_number': a_type, 'fingerprint_type': s_type}
        self.do_generic_add(**data)

        label = "df"
        key = "8d97e98f8af710c7e7fe703abc8f639e0ee507c4"
        s_type = 1
        a_type = 1
        data = {'label': label, 'key': key, 'domain': self.o_e,
                'algorithm_number': a_type, 'fingerprint_type': s_type}
        self.do_generic_add(**data)

        label = "12314"
        key = "8d97e98f8af710c7e7fe703abc8f639e0ee507c4"
        s_type = 1
        a_type = 1
        data = {'label': label, 'key': key, 'domain': self.o,
                'algorithm_number': a_type, 'fingerprint_type': s_type}
        self.do_generic_add(**data)

    def test_domain_ctnr(self):
        key = '8d97e98f8af710c7e7fe703abc8f639e0ee507c4'

        ctnr1 = Ctnr(name='test_ctnr1')
        ctnr1.full_clean()
        ctnr1.save()
        ctnr1.domains.add(self.o_e)

        ctnr2 = Ctnr(name='test_ctnr2')
        ctnr2.full_clean()
        ctnr2.save()

        s1 = SSHFP(label='foo', domain=self.o_e, key=key, algorithm_number=1,
                   fingerprint_type=1, ctnr=ctnr1)
        s1.full_clean()
        s1.save()

        with self.assertRaises(ValidationError):
            s2 = SSHFP(label='bleh', domain=self.o_e, key=key,
                       algorithm_number=1, fingerprint_type=1, ctnr=ctnr2)
            s2.full_clean()
            s2.save()

    def test_name_unique(self):
        """Test that two SSHFPs cannot share a name"""
        key1 = '7d97e98f8af710c7e7fe703abc8f639e0ee507c4'
        key2 = '8d97e98f8af710c7e7fe703abc8f639e0ee507c4'

        s1 = SSHFP(label='foo', domain=self.o_e, key=key1, algorithm_number=1,
                   fingerprint_type=1, ctnr=self.ctnr)
        s1.full_clean()
        s1.save()

        with self.assertRaises(ValidationError):
            s2 = SSHFP(label='foo', domain=self.o_e, key=key2,
                       algorithm_number=1, fingerprint_type=1, ctnr=self.ctnr)
            s2.full_clean()
            s2.save()
