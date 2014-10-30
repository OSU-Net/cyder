from django.core.exceptions import ValidationError

from basestatic import BaseStaticTests


class PTRStaticRegTests(BaseStaticTests):
    def test1_conflict_add_intr_first(self):
        # PTRdd an intr and make sure PTR can't exist.
        mac = "11:22:33:44:55:66"
        label = "foo4"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        self.do_add_intr(**kwargs)
        kwargs = {'label': label, 'domain': domain, 'ip_str': ip_str}
        self.assertRaises(ValidationError, self.do_add_ptr, **kwargs)

    def test1_conflict_add_PTR_first(self):
        # Add an PTR and make sure an intr can't exist.
        mac = "11:22:33:44:55:66"
        label = "foo5"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'label': label, 'domain': domain, 'ip_str': ip_str}
        self.do_add_ptr(**kwargs)
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        self.assertRaises(ValidationError, self.do_add_intr, **kwargs)

    def test2_conflict_add_intr_first(self):
        # Add an intr and update an existing PTR to conflict.
        # Test for exception.
        mac = "12:22:33:44:55:66"
        label = "fo99"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        self.do_add_intr(**kwargs)
        ip_str = "10.0.0.3"
        kwargs = {'label': label, 'domain': domain, 'ip_str': ip_str}
        ptr = self.do_add_ptr(**kwargs)
        ptr.ip_str = "10.0.0.2"
        self.assertRaises(ValidationError, ptr.save)

    def test2_conflict_add_A_first(self):
        # Add an PTR and update and existing intr to conflict.
        # Test for exception.
        mac = "11:22:33:44:55:66"
        label = "foo98"
        domain = self.f_c
        ip_str = "10.0.0.2"
        # Add PTR
        kwargs = {'label': label, 'domain': domain, 'ip_str': ip_str}
        self.do_add_ptr(**kwargs)

        # Add Intr with diff IP
        ip_str = "10.0.0.3"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        intr = self.do_add_intr(**kwargs)

        # Conflict the IP on the intr
        intr.ip_str = "10.0.0.2"
        self.assertRaises(ValidationError, intr.save)
