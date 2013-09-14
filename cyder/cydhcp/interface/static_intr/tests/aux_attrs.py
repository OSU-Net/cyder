from django.test import TestCase
from django.core.exceptions import ValidationError

from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.interface.static_intr.models import StaticIntrKeyValue
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.network.models import Network
from cyder.core.system.models import System
from cyder.core.ctnr.models import Ctnr
from cyder.cydns.domain.models import Domain
from cyder.cydns.address_record.models import AddressRecord

from cyder.cydns.ip.utils import ip_to_domain_name


class AuxAttrTests(TestCase):
    def create_domain(self, name, ip_type=None, delegated=False):
        if ip_type is None:
            ip_type = '4'
        if name in ('arpa', 'in-addr.arpa', 'ip6.arpa'):
            pass
        else:
            name = ip_to_domain_name(name, ip_type=ip_type)
        d = Domain(name=name, delegated=delegated)
        d.clean()
        self.assertTrue(d.is_reverse)
        return d

    def setUp(self):
        self.ctnr = Ctnr(name='abloobloobloo')
        self.ctnr.save()
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
        self.s = System(name='foobar')
        self.s.save()

        self.net = Network(network_str='10.0.0.0/29')
        self.net.update_network()
        self.net.save()
        self.sr = Range(network=self.net, range_type=STATIC,
                        start_str='10.0.0.1', end_str='10.0.0.3')
        self.sr.save()

    def do_add(self, mac, label, domain, ip_str, ip_type='4'):
        r = StaticInterface(mac=mac, label=label, domain=domain, ip_str=ip_str,
                            ip_type=ip_type, system=self.s, ctnr=self.ctnr)
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
        x = StaticIntrKeyValue.objects.filter(key='primary',
                                              static_interface=intr)
        self.assertFalse(x)
        intr.attrs.primary = '1'
        self.assertEqual(intr.attrs.cache['primary'], '1')
        self.assertEqual(intr.attrs.primary, '1')
        x = StaticIntrKeyValue.objects.filter(key='primary',
                                              static_interface=intr)
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
            return x
        self.assertRaises(AttributeError, bad_get)
        intr.attrs.primary = '1'
        self.assertEqual(intr.attrs.primary, '1')
        self.assertEqual(intr.attrs.cache['primary'], '1')

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
        self.assertEqual(intr.attrs.cache['primary'], '2')
        del intr.attrs.primary

        def bad_get():
            intr.attrs.primary
        self.assertRaises(AttributeError, bad_get)
        intr.attrs.primary = '3'
        self.assertEqual(intr.attrs.primary, '3')
        self.assertEqual(intr.attrs.cache['primary'], '3')

    def test7_create(self):
        mac = "13:22:33:44:55:27"
        label = "foo2"
        domain = self.f_c
        ip_str = "10.0.0.3"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        intr = self.do_add(**kwargs)
        intr.update_attrs()

        def bad_assign():
            intr.attrs.primary = '22f'
        self.assertRaises(ValidationError, bad_assign)
        intr.attrs.primary = '33'
        self.assertEqual(intr.attrs.primary, '33')
        self.assertEqual(intr.attrs.cache['primary'], '33')
        del intr.attrs.primary

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

    def test1_existing_attrs(self):
        mac = "19:22:33:44:55:66"
        label = "foo"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'mac': mac, 'label': label, 'domain': domain,
                  'ip_str': ip_str}
        intr = self.do_add(**kwargs)
        StaticIntrKeyValue(key="foo", value="bar",
                           static_interface=intr).save()
        StaticIntrKeyValue(
            key="interface_type", value="eth0", static_interface=intr).save()
        StaticIntrKeyValue(key="alias", value="5",
                           static_interface=intr).save()
        intr.update_attrs()
        self.assertEqual(intr.attrs.alias, '5')
        self.assertEqual(intr.attrs.cache['alias'], '5')
        self.assertEqual(intr.attrs.interface_type, 'eth0')
        self.assertEqual(intr.attrs.cache['interface_type'], 'eth0')
        self.assertEqual(intr.attrs.foo, 'bar')
        self.assertEqual(intr.attrs.cache['foo'], 'bar')
