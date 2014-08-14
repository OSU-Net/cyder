from django.core.exceptions import ValidationError

import cyder.base.tests
from cyder.core.ctnr.models import Ctnr
from cyder.cydns.txt.models import TXT
from cyder.cydns.domain.models import Domain
from cyder.core.ctnr.models import Ctnr


class TXTTests(cyder.base.tests.TestCase):
    def setUp(self):
        self.ctnr = Ctnr(name='abloobloobloo')
        self.ctnr.save()
        self.o = Domain(name="org")
        self.o.save()
        self.o_e = Domain(name="oregonstate.org")
        self.o_e.save()
        self.ctnr.domains.add(self.o)
        self.ctnr.domains.add(self.o_e)

    def do_generic_add(self, **data):
        if 'ctnr' not in data:
            data['ctnr'] = self.ctnr
        txt = TXT(**data)
        txt.full_clean()
        txt.__repr__()
        txt.save()
        rtxt = TXT.objects.filter(**data)
        self.assertTrue(len(rtxt) == 1)
        return txt

    def do_remove(self, **data):
        txt = self.do_generic_add(data)
        txt.delete()
        rmx = TXT.objects.filter(**data)
        self.assertTrue(len(rmx) == 0)

    def test_add_remove_txt(self):
        label = "asdf"
        data = "asdf"
        data = {'label': label, 'txt_data': data, 'domain': self.o_e}
        self.do_generic_add(**data)

        label = "asdf"
        data = "asdfasfd"
        data = {'label': label, 'txt_data': data, 'domain': self.o_e}
        self.do_generic_add(**data)

        label = "df"
        data = "aasdf"
        data = {'label': label, 'txt_data': data, 'domain': self.o_e}
        self.do_generic_add(**data)

        label = "12314"
        data = "dd"
        data = {'label': label, 'txt_data': data, 'domain': self.o}
        self.do_generic_add(**data)

    def test_domain_ctnr(self):
        ctnr1 = Ctnr(name='test_ctnr1')
        ctnr1.full_clean()
        ctnr1.save()
        ctnr1.domains.add(self.o_e)

        ctnr2 = Ctnr(name='test_ctnr2')
        ctnr2.full_clean()
        ctnr2.save()

        self.do_generic_add(
            label='foo', domain=self.o_e, txt_data='Data data data',
            ctnr=ctnr1)

        with self.assertRaises(ValidationError):
            self.do_generic_add(
                label='bleh', domain=self.o_e, txt_data='Data data data',
                ctnr=ctnr2)

    def test_name_duplicates(self):
        """Test that multiple TXTs may share a name"""
        for txt_data in ('qwertyuiop', 'asdfghjkl', 'zxcvbnm'):
            t = TXT(label='foo', domain=self.o_e, txt_data=txt_data,
                    ctnr=self.ctnr)
            t.full_clean()
            t.save()
