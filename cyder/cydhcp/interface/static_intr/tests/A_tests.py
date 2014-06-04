from django.core.exceptions import ValidationError

from basestatic import BaseStaticTests


class AStaticRegTests(BaseStaticTests):
    def test1_conflict_add_intr_first(self):
        # Add an intr and make sure A can't exist.
        mac = "11:22:33:44:55:66"
        label = "foo4"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        self.do_add_intr(**kwargs)
        kwargs = {'label': label, 'domain': domain, 'ip_str': ip_str}
        self.assertRaises(ValidationError, self.do_add_a, **kwargs)

    def test1_conflict_add_A_first(self):
        # Add an A and make sure an intr can't exist.
        mac = "11:22:33:44:55:66"
        label = "foo5"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'label': label, 'domain': domain, 'ip_str': ip_str}
        self.do_add_a(**kwargs)
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        self.assertRaises(ValidationError, self.do_add_intr, **kwargs)

    def test2_conflict_add_intr_first(self):
        # Add an intr and update an existing A to conflict. Test for exception.
        mac = "12:22:33:44:55:66"
        label = "fo99"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        self.do_add_intr(**kwargs)
        ip_str = "10.0.0.3"
        kwargs = {'label': label, 'domain': domain, 'ip_str': ip_str}
        a = self.do_add_a(**kwargs)
        a.ip_str = "10.0.0.2"
        self.assertRaises(ValidationError, a.save)

    def test2_conflict_add_A_first(self):
        # Add an A and update and existing intr to conflict. Test for
        # exception.
        mac = "11:22:33:44:55:66"
        label = "foo98"
        domain = self.f_c
        ip_str = "10.0.0.2"
        # Add A
        kwargs = {'label': label, 'domain': domain, 'ip_str': ip_str}
        self.do_add_a(**kwargs)

        # Add Intr with diff IP
        ip_str = "10.0.0.3"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        intr = self.do_add_intr(**kwargs)

        # Conflict the IP on the intr
        intr.ip_str = "10.0.0.2"
        self.assertRaises(ValidationError, intr.save)
