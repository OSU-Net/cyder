from django.core.exceptions import ValidationError

from cyder.cydns.cname.models import CNAME

from basestatic import BaseStaticTests


class CNAMEStaticRegTests(BaseStaticTests):
    def test1_delete_cname(self):
        mac = "11:22:33:44:55:66"
        label = "foo4"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        i = self.do_add_intr(**kwargs)
        cn, _ = CNAME.objects.get_or_create(label='foo', domain=domain,
                                            target=label + "." + domain.name,
                                            ctnr=self.ctnr)
        self.assertRaises(ValidationError, i.delete)

    def test1_delete_override(self):
        mac = "12:22:33:44:55:66"
        label = "foo6"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        i = self.do_add_intr(**kwargs)
        cn, _ = CNAME.objects.get_or_create(label='food', domain=domain,
                                            target=label + "." + domain.name,
                                            ctnr=self.ctnr)
        i.delete(check_cname=False, **{'delete_system': False})
