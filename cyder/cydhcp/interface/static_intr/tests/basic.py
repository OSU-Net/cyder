from django.test import TestCase
from django.core.exceptions import ValidationError

from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.core.system.models import System
from cyder.cydns.domain.models import Domain
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.ptr.models import PTR
from cyder.cydns.view.models import View

from cyder.cydns.ip.utils import ip_to_domain_name, nibbilize



class StaticInterTests(TestCase):
    def create_domain(self, name, ip_type=None, delegated=False):
        if ip_type is None:
            ip_type = '4'
        if name in ('arpa', 'in-addr.arpa', 'ipv6.arpa'):
            pass
        else:
            name = ip_to_domain_name(name, ip_type=ip_type)
        d = Domain(name=name, delegated=delegated)
        d.clean()
        self.assertTrue(d.is_reverse)
        return d

    def setUp(self):
        self.arpa = self.create_domain(name='arpa')
        self.arpa.save()
        self.i_arpa = self.create_domain(name='in-addr.arpa')
        self.i_arpa.save()

        self.c = Domain(name="ccc")
        self.c.save()
        self.f_c = Domain(name="foo.ccc")
        self.f_c.save()
        self.r1 = self.create_domain(name="10")
        self.r1.save()
        self.n = System()
        self.n.clean()
        self.n.save()
        View.objects.get_or_create(name="private")

    def do_add(self, mac, label, domain, ip_str, ip_type='4'):
        r = StaticInterface(mac=mac, label=label, domain=domain, ip_str=ip_str,
                            ip_type=ip_type, system=self.n)
        r.clean()
        r.save()
        r.details()
        r.get_update_url()
        r.get_delete_url()
        r.get_detail_url()
        repr(r)
        return r

    def do_delete(self, r):
        ip_str = r.ip_str
        fqdn = r.fqdn
        r.delete()
        self.assertFalse(
            AddressRecord.objects.filter(ip_str=ip_str, fqdn=fqdn))

    def test1_create_basic(self):
        mac = "11:22:33:44:55:66"
        label = "foo"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        i = self.do_add(**kwargs)
        i.update_attrs()
        self.assertEqual('None', i.interface_name())
        i.attrs.interface_type = "eth"
        self.assertEqual('None', i.interface_name())
        i.attrs.primary = "0"
        self.assertEqual('eth0', i.interface_name())
        i.attrs.alias = "0"
        self.assertEqual('eth0.0', i.interface_name())
        i.clean()

        def bad_assign():
            i.attrs.interface_type = "wee"
        self.assertRaises(ValidationError, bad_assign)

        def bad_assign():
            i.attrs.primary = "wee"
        self.assertRaises(ValidationError, bad_assign)

        def bad_assign():
            i.attrs.alias = "wee"
        self.assertRaises(ValidationError, bad_assign)

    def test2_create_basic(self):
        mac = "11:22:33:44:55:66"
        label = "foo1"
        domain = self.f_c
        ip_str = "10.0.0.1"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        i = self.do_add(**kwargs)

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
        self.do_add(**kwargs)

    def test4_create_basic(self):
        mac = "12:22:33:44:55:66"
        label = "foo1"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        self.do_add(**kwargs)

    def test5_create_basic(self):
        mac = "00:00:00:00:00:00"
        label = "foo1"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        r = self.do_add(**kwargs)

        # Change the mac by one.
        mac = "00:00:00:00:00:01"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        r = self.do_add(**kwargs)

    def test1_delete(self):
        mac = "12:22:33:44:55:66"
        label = "foo1"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        r = self.do_add(**kwargs)
        self.do_delete(r)

    def test1_dup_create_basic(self):
        mac = "11:22:33:44:55:66"
        label = "foo3"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        self.do_add(**kwargs)
        self.assertRaises(ValidationError, self.do_add, **kwargs)

    def test1_bad_add_for_a_ptr(self):
        # Intr exists, then try ptr and A
        mac = "11:22:33:44:55:66"
        label = "9988food"
        domain = self.c
        ip_str = "10.0.0.1"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        ip_type = '4'
        i = self.do_add(**kwargs)
        i.clean()
        i.save()
        a = AddressRecord(label=label, domain=domain, ip_str=ip_str,
                          ip_type=ip_type)
        self.assertRaises(ValidationError, a.clean)
        ptr = PTR(ip_str=ip_str, ip_type=ip_type, name=i.fqdn)
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
                          ip_type=ip_type)
        a.clean()
        a.save()
        ptr = PTR(ip_str=ip_str, ip_type=ip_type, name=a.fqdn)
        ptr.clean()
        ptr.save()
        self.assertRaises(ValidationError, self.do_add, **kwargs)

    def test1_bad_reverse_domain(self):
        mac = "11:22:33:44:55:66"
        label = "8888foo"
        domain = self.f_c
        ip_str = "10.0.0.1"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        i = self.do_add(**kwargs)
        i.ip_str = "9.0.0.1"
        self.assertRaises(ValidationError, i.clean)

    def test1_no_system(self):
        mac = "15:22:33:44:55:66"
        label = "8888foo"
        domain = self.f_c
        ip_str = "10.0.0.1"
        ip_type = '4'
        r = StaticInterface(label=label, domain=domain, ip_str=ip_str,
                            ip_type=ip_type, system=None)
        self.assertRaises(ValidationError, r.clean)
