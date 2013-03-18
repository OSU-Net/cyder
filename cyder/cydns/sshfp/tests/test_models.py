from django.test import TestCase
from cyder.cydns.sshfp.models import SSHFP
from cyder.cydns.domain.models import Domain


class SSHFPTests(TestCase):
    def setUp(self):
        self.o = Domain(name="org")
        self.o.save()
        self.o_e = Domain(name="mozilla.org")
        self.o_e.save()

    def do_generic_add(self, data):
        sshfp = SSHFP(**data)
        sshfp.__repr__()
        sshfp.save()
        self.assertTrue(sshfp.details())
        rsshfp = SSHFP.objects.filter(**data)
        self.assertEqual(len(rsshfp), 1)
        return sshfp

    def do_remove(self, data):
        sshfp = self.do_generic_add(data)
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
        self.do_generic_add(data)

        label = "asdf"
        key = "8d97e98f8af710c7e7fe703abc8f639e0ee507c4"
        s_type = 1
        a_type = 1
        data = {'label': label, 'key': key, 'domain': self.o_e,
                'algorithm_number': a_type, 'fingerprint_type': s_type}
        self.do_generic_add(data)

        label = "df"
        key = "8d97e98f8af710c7e7fe703abc8f639e0ee507c4"
        s_type = 1
        a_type = 1
        data = {'label': label, 'key': key, 'domain': self.o_e,
                'algorithm_number': a_type, 'fingerprint_type': s_type}
        self.do_generic_add(data)

        label = "12314"
        key = "8d97e98f8af710c7e7fe703abc8f639e0ee507c4"
        s_type = 1
        a_type = 1
        data = {'label': label, 'key': key, 'domain': self.o,
                'algorithm_number': a_type, 'fingerprint_type': s_type}
        self.do_generic_add(data)
