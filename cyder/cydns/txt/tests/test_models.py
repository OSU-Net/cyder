from django.test import TestCase

from cyder.cydns.txt.models import TXT
from cyder.cydns.domain.models import Domain


class TXTTests(TestCase):
    def setUp(self):
        self.o = Domain(name="org")
        self.o.save()
        self.o_e = Domain(name="oregonstate.org")
        self.o_e.save()

    def do_generic_add(self, data):
        txt = TXT(**data)
        txt.__repr__()
        txt.save()
        rtxt = TXT.objects.filter(**data)
        self.assertTrue(len(rtxt) == 1)
        return txt

    def do_remove(self, data):
        txt = self.do_generic_add(data)
        txt.delete()
        rmx = TXT.objects.filter(**data)
        self.assertTrue(len(rmx) == 0)

    def test_add_remove_txt(self):
        label = "asdf"
        data = "asdf"
        data = {'label': label, 'txt_data': data, 'domain': self.o_e}
        self.do_generic_add(data)

        label = "asdf"
        data = "asdfasfd"
        data = {'label': label, 'txt_data': data, 'domain': self.o_e}
        self.do_generic_add(data)

        label = "df"
        data = "aasdf"
        data = {'label': label, 'txt_data': data, 'domain': self.o_e}
        self.do_generic_add(data)

        label = "12314"
        data = "dd"
        data = {'label': label, 'txt_data': data, 'domain': self.o}
        self.do_generic_add(data)
