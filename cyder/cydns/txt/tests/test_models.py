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
        txt.save()
        txt.__repr__()
        self.assertEqual(TXT.objects.filter(**data).count(), 1)
        return txt

    def do_remove(self, **data):
        txt = self.do_generic_add(data)
        txt.delete()
        rmx = TXT.objects.filter(**data)
        self.assertTrue(len(rmx) == 0)

    def test_add_remove_txt(self):
        self.do_generic_add(label="asdf", txt_data="asdf", domain=self.o_e)
        self.do_generic_add(label="asdf", txt_data="asdfasfd", domain=self.o_e)
        self.do_generic_add(label="df", txt_data="aasdf", domain=self.o_e)
        self.do_generic_add(label="12314", txt_data="dd", domain=self.o)

    def test_domain_ctnr(self):
        ctnr1 = Ctnr(name='test_ctnr1')
        ctnr1.save()
        ctnr1.domains.add(self.o_e)

        self.do_generic_add(
            label='foo', domain=self.o_e, txt_data='Data data data',
            ctnr=ctnr1)

        ctnr2 = Ctnr(name='test_ctnr2')
        ctnr2.save()

        self.assertRaises(ValidationError, self.do_generic_add,
            label='bleh', domain=self.o_e, txt_data='Data data data',
            ctnr=ctnr2)

    def test_name_duplicates(self):
        """Test that multiple TXTs may share a name"""

        for txt_data in ('qwertyuiop', 'asdfghjkl', 'zxcvbnm'):
            TXT.objects.create(
                label='foo', domain=self.o_e, txt_data=txt_data,
                ctnr=self.ctnr)
