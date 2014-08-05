from django.core.exceptions import ValidationError
from functools import partial

from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.ptr.models import PTR
from basestatic import BaseStaticTests


class StaticInterTests(BaseStaticTests):
    def test1_create_basic(self):
        mac = "11:22:33:44:55:66"
        label = "foo"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        i = self.do_add_intr(**kwargs)
        i.clean()

    def test2_create_basic(self):
        mac = "11:22:33:44:55:66"
        label = "foo1"
        domain = self.f_c
        ip_str = "10.0.0.1"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        i = self.do_add_intr(**kwargs)

        i.dhcp_enabled = False
        i.clean()
        i.save()
        i2 = StaticInterface.objects.get(pk=i.pk)
        self.assertFalse(i2.dhcp_enabled)

        i.dhcp_enabled = True
        i.clean()
        i.save()
        i3 = StaticInterface.objects.get(pk=i.pk)
        self.assertTrue(i3.dhcp_enabled)

    def test3_create_basic(self):
        mac = "11:22:33:44:55:66"
        label = "foo1"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        self.do_add_intr(**kwargs)

    def test4_create_basic(self):
        mac = "12:22:33:44:55:66"
        label = "foo1"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        self.do_add_intr(**kwargs)

    def test5_create_basic(self):
        mac = "00:00:00:00:00:01"
        label = "foo1"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        self.do_add_intr(**kwargs)

        # Change the mac by one.
        mac = "00:00:00:00:00:02"
        label = "foo2"
        ip_str = "10.0.0.3"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        self.do_add_intr(**kwargs)

    def test1_delete(self):
        mac = "12:22:33:44:55:66"
        label = "foo1"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        r = self.do_add_intr(**kwargs)
        self.do_delete(r)

    def test1_dup_create_basic(self):
        mac = "11:22:33:44:55:66"
        label = "foo3"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        self.do_add_intr(**kwargs)
        self.assertRaises(ValidationError, self.do_add_intr, **kwargs)

    def test1_bad_add_for_a_ptr(self):
        # Intr exists, then try ptr and A
        mac = "11:22:33:44:55:66"
        label = "9988food"
        domain = self.c
        ip_str = "10.0.0.1"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        ip_type = '4'
        i = self.do_add_intr(**kwargs)
        i.clean()
        i.save()
        a = AddressRecord(label=label, domain=domain, ip_str=ip_str,
                          ip_type=ip_type, ctnr=self.ctnr)
        self.assertRaises(ValidationError, a.clean)
        ptr = PTR(ip_str=ip_str, ip_type=ip_type, fqdn=i.fqdn, ctnr=self.ctnr)
        self.assertRaises(ValidationError, ptr.clean)

    def test2_bad_add_for_a_ptr(self):
        # PTR and A exist, then try add intr
        mac = "11:22:33:44:55:66"
        label = "9988fdfood"
        domain = self.c
        ip_str = "10.0.0.1"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        ip_type = '4'
        a = AddressRecord(label=label, domain=domain, ip_str=ip_str,
                          ip_type=ip_type, ctnr=self.ctnr)
        a.clean()
        a.save()
        ptr = PTR(ip_str=ip_str, ip_type=ip_type, fqdn=a.fqdn, ctnr=self.ctnr)
        ptr.clean()
        ptr.save()
        self.assertRaises(ValidationError, self.do_add_intr, **kwargs)

    def test1_bad_reverse_domain(self):
        mac = "11:22:33:44:55:66"
        label = "8888foo"
        domain = self.f_c
        ip_str = "10.0.0.1"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        i = self.do_add_intr(**kwargs)
        i.ip_str = "9.0.0.1"
        self.assertRaises(ValidationError, i.save)

    def test1_no_system(self):
        mac = "15:22:33:44:55:66"
        label = "8888foo"
        domain = self.f_c
        ip_str = "10.0.0.1"
        ip_type = '4'

        create = partial(StaticInterface, label=label, domain=domain,
                         ip_str=ip_str, ip_type=ip_type, system=None, mac=mac,
                         ctnr=self.ctnr)
        self.assertRaises(ValueError, create)

    def test_has_range(self):
        mac = "15:22:33:44:55:66"
        label = "8888foo"
        domain = self.f_c
        ip_str = "10.0.0.1"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        i = self.do_add_intr(**kwargs)

        i.clean()
        i.ip_str = "10.0.0.4"
        self.assertRaises(ValidationError, i.clean)
        i.dhcp_enabled = False
        i.clean()
