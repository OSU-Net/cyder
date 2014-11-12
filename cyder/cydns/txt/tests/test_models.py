from django.core.exceptions import ValidationError

from cyder.base.tests import ModelTestMixin, TestCase
from cyder.core.ctnr.models import Ctnr
from cyder.cydns.txt.models import TXT
from cyder.cydns.domain.models import Domain
from cyder.core.ctnr.models import Ctnr


class TXTTests(TestCase, ModelTestMixin):
    def setUp(self):
        self.ctnr = Ctnr.objects.create(name='abloobloobloo')
        self.o = Domain.objects.create(name="org")
        self.o_e = Domain.objects.create(name="oregonstate.org")
        self.ctnr.domains.add(self.o)
        self.ctnr.domains.add(self.o_e)

    def create_txt(self, **kwargs):
        kwargs.setdefault('ctnr', self.ctnr)
        return TXT.objects.create(**kwargs)

    @property
    def objs(self):
        """Create objects for test_create_delete."""
        return (
            self.create_txt(label="asdf", txt_data="asdf", domain=self.o_e),
            self.create_txt(
                label="asdf", txt_data="asdfasfd", domain=self.o_e),
            self.create_txt(label="df", txt_data="aasdf", domain=self.o_e),
            self.create_txt(label="12314", txt_data="dd", domain=self.o),
        )

    def test_domain_ctnr(self):
        ctnr1 = Ctnr.objects.create(name='test_ctnr1')
        ctnr1.domains.add(self.o_e)

        self.create_txt(
            label='foo', domain=self.o_e, txt_data='Data data data',
            ctnr=ctnr1)

        ctnr2 = Ctnr.objects.create(name='test_ctnr2')

        self.assertRaises(
            ValidationError, self.create_txt,
            label='bleh', domain=self.o_e, txt_data='Data data data',
            ctnr=ctnr2)

    def test_name_duplicates(self):
        """Test that multiple TXTs may share a name"""
        for txt_data in ('qwertyuiop', 'asdfghjkl', 'zxcvbnm'):
            self.create_txt(label='foo', domain=self.o_e, txt_data=txt_data)
