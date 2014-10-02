from django.core.exceptions import ValidationError

from cyder.cydns.cname.models import CNAME

from basestatic import BaseStaticTests


class CNAMEStaticRegTests(BaseStaticTests):
    def test1_delete_cname(self):
        i = self.do_add_intr(
            mac="11:22:33:44:55:66",
            label="foo4",
            domain=self.f_c,
            ip_str="10.0.0.2",
        )
        cn = CNAME.objects.create(
            label='foo', domain=self.f_c, target='foo4.foo.ccc',
            ctnr=self.ctnr)
        self.assertRaises(ValidationError, i.delete)

    def test1_delete_override(self):
        i = self.do_add_intr(
            mac="12:22:33:44:55:66",
            label="foo6",
            domain=self.f_c,
            ip_str="10.0.0.2",
        )
        cn = CNAME.objects.create(
            label='food', domain=self.f_c, target='foo6.foo.ccc',
            ctnr=self.ctnr)
        i.delete(check_cname=False, delete_system=False)
