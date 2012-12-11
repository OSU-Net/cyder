from django.test import TestCase
from django.core.exceptions import ValidationError

from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.interface.static_intr.models import StaticIntrKeyValue
from cyder.core.system.models import System
from cyder.cydns.domain.models import Domain
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.ptr.models import PTR

from cyder.cydns.ip.utils import ip_to_domain_name, nibbilize



class SystemIntegrationTests(TestCase):
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

    def do_add(self, mac, label, domain, ip_str, ip_type='4'):
        self.n = System()
        r = StaticInterface(mac=mac, label=label, domain=domain, ip_str=ip_str,
                            ip_type=ip_type, system=self.n)
        r.clean()
        r.save()
        repr(r)
        return r

    def do_delete(self, r):
        ip_str = r.ip_str
        fqdn = r.fqdn
        r.delete()
        self.assertFalse(
            AddressRecord.objects.filter(ip_str=ip_str, fqdn=fqdn))

    def test1_create(self):
        mac = "11:22:33:44:55:66"
        label = "foo"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        intr = self.do_add(**kwargs)
        intr.update_attrs()

        def bad_get():
            intr.attrs.primary
        self.assertRaises(AttributeError, bad_get)
        x = StaticIntrKeyValue.objects.filter(key='primary', intr=intr)
        self.assertFalse(x)
        intr.attrs.primary = '1'
        self.assertEqual(intr.attrs.primary, '1')
        x = StaticIntrKeyValue.objects.filter(key='primary', intr=intr)
        self.assertEqual(x[0].value, '1')

    def test6_create(self):
        mac = "24:22:33:44:55:66"
        label = "foo"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        intr = self.do_add(**kwargs)
        intr.update_attrs()
        intr.update_attrs()
        intr.update_attrs()

        def bad_get():
            x = intr.attrs.primary
        self.assertRaises(AttributeError, bad_get)
        intr.attrs.primary = '1'
        self.assertEqual(intr.attrs.primary, '1')

    def test2_create(self):
        mac = "13:22:33:44:55:66"
        label = "foo"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        intr = self.do_add(**kwargs)
        intr.update_attrs()
        intr.attrs.primary = '2'
        self.assertEqual(intr.attrs.primary, '2')
        del intr.attrs.primary

        def bad_get():
            intr.attrs.primary
        self.assertRaises(AttributeError, bad_get)
        intr.attrs.primary = '3'
        self.assertEqual(intr.attrs.primary, '3')

    def test1_del(self):
        mac = "12:22:33:44:55:66"
        label = "foo"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        intr = self.do_add(**kwargs)
        intr.update_attrs()
        intr.attrs.primary = '88'
        self.assertEqual(intr.attrs.primary, '88')
        del intr.attrs.primary

        def bad_get():
            intr.attrs.primary
        self.assertRaises(AttributeError, bad_get)

    def test3_create(self):
        mac = "19:22:33:44:55:66"
        label = "foo"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        intr = self.do_add(**kwargs)
        intr.update_attrs()

        def bad_assign():
            intr.attrs.primary = 'a'
        self.assertRaises(ValidationError, bad_assign)
